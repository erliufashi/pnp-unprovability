#!/usr/bin/env python3
"""Finite 2-layer/2-head incremental policy comparison, not a real LLM.

FullKV and ForestModel share only frozen pure word/profile functions.
The production stream has no observer and stores no output history.
Test observers/output lists are passive external instrumentation.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prefix_kernel',HERE/'prefix_query_forest.py')
f=importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
t=f.t
PROMPT=(-2,2)
VOCAB=(-2,0,2)
EOS=0
INVALID=-99
CONFIGS=[
 {'name':'toy-A','heads':[
     [(2,0,2,0,2,0),(-2,2,2,-2,2,2)],
     [(2,2,-2,0,2,-2),(4,-2,2,2,-2,0)]], 'post':[1,2]},
 {'name':'toy-B','heads':[
     [(2,2,-2,2,4,-2),(2,-2,4,0,-2,2)],
     [(-2,0,2,2,2,0),(2,2,-2,-2,4,0)]], 'post':[1,1]},
]


def position_word(p):
    return (-2,0,2)[(p-1)%3]


def qkv(hidden,p,weights):
    pos=position_word(p)
    aq,bq,ak,bk,av,bv=weights
    return (t.add(t.mul(hidden,aq),t.mul(pos,bq)),
            t.add(t.mul(hidden,ak),t.mul(pos,bk)),
            t.add(t.mul(hidden,av),t.mul(pos,bv)))


class Base:
    def __init__(self,config,seed):
        self.config=config
        self.position=0
        self.last_hidden=None
        self.rng=random.Random(seed)
        self.samples=0
    def counts(self): raise NotImplementedError
    def attend(self,layer,head,q,k,v): raise NotImplementedError
    def feed(self,token):
        p=self.position+1
        hidden=token
        steps=[]; processed=set()
        for layer,heads in enumerate(self.config['heads']):
            before=hidden; outputs=[]
            for head,weights in enumerate(heads):
                q,k,v=qkv(before,p,weights)
                assert q in t.QUERIES and k in t.F and v in t.F
                output=self.attend(layer,head,q,k,v)
                assert output in t.F
                outputs.append(output); processed.add((layer,head))
                expected=[[p+1 if (a,b) in processed else p for b in range(len(row))]
                          for a,row in enumerate(self.config['heads'])]
                actual=self.counts(); assert actual==expected
                steps.append({'layer':layer,'head':head,'q':q,'k':k,'v':v,'output':output,
                              'seed_inclusive_head_counts':actual})
            combined=t.fold(t.add,0,outputs)
            hidden=(0 if self.config.get('constant_post') else
                    t.add(before,t.mul(combined,self.config['post'][layer])))
            assert hidden in t.F
            steps.append({'layer':layer,'hidden_before':before,'hidden_after':hidden})
        self.position=p; self.last_hidden=hidden
        return {'position':p,'input_token':token,'steps':steps,'last_hidden':hidden}
    def draw_next(self,stochastic):
        assert self.last_hidden in t.F
        h=self.last_hidden
        weights=(7-h,2,7+h)  # Positive integers summing to 16.
        assert sum(weights)==16 and min(weights)>0
        if not stochastic:
            return VOCAB[max(range(3),key=lambda i:weights[i])]
        # Bounded 4-bit sampling: no unbounded rejection loop.
        draw=self.rng.getrandbits(4); self.samples+=1
        if draw<weights[0]: return VOCAB[0]
        if draw<weights[0]+weights[1]: return EOS
        return VOCAB[2]
    def stream(self,prompt,budget,stochastic=False,observer=None):
        any_input=False; invalid=False
        for token in prompt:
            any_input=True
            if invalid or token not in PROMPT:
                invalid=True; continue
            audit=self.feed(token)
            if observer is not None: observer('prompt',audit)
        if invalid or not any_input:
            yield INVALID
            return
        for step in range(budget):
            token=self.draw_next(stochastic)
            yield token  # Only answer output, after prompt EOF.
            if token==EOS: return
            audit=self.feed(token)
            if observer is not None: observer('feedback',audit)


class FullKV(Base):
    def __init__(self,config,seed):
        super().__init__(config,seed)
        self.histories=[[[] for head in heads] for heads in config['heads']]
    def attend(self,layer,head,q,k,v):
        history=self.histories[layer][head]
        history.append((k,v))
        return f.literal_kernel(history,q)
    def counts(self):
        return [[len(history)+1 for history in row] for row in self.histories]
    def storage(self):
        return {'kv_numeric_words':sum(2*len(history) for row in self.histories for history in row),
                'position':self.position,'scope':'KV numeric entries only; program/PRNG/control excluded'}


class ForestModel(Base):
    def __init__(self,config,seed):
        super().__init__(config,seed)
        self.caches=[[f.TreeCache() for head in heads] for heads in config['heads']]
    def attend(self,layer,head,q,k,v):
        cache=self.caches[layer][head]
        cache.append(k,v)
        return cache.query(q)
    def counts(self):
        return [[cache.count for cache in row] for row in self.caches]
    def storage(self):
        shapes=[cache.shape() for row in self.caches for cache in row]
        return {'allocated_word_slots':sum(x['allocated_word_slots'] for x in shapes),
                'live_numeric_words':sum(x['live_numeric_words'] for x in shapes),
                'parameter_forests':sum(cache.parameters() for row in self.caches for cache in row),
                'max_level_span':max(x['level_span'] for x in shapes),
                'position':self.position,
                'scope':'numeric forest slots only, not RSS; fixed PRNG and log counters separate'}


def paired_case(config,prompt,stochastic,seed,budget=6):
    reference=FullKV(config,seed); compiled=ForestModel(config,seed)
    audit_a=[]; audit_b=[]; digest=hashlib.sha256(); hidden_values=set()
    def observe_a(kind,audit): audit_a.append((kind,audit))
    def observe_b(kind,audit): audit_b.append((kind,audit))
    ra=reference.stream(iter(prompt),budget,stochastic,observe_a)
    rb=compiled.stream(iter(prompt),budget,stochastic,observe_b)
    outputs=[]; feedback_steps=0; feed_steps=0; sample_checks=0; head_count_checks=0
    while True:
        try: a=next(ra); done_a=False
        except StopIteration: a=None; done_a=True
        try: b=next(rb); done_b=False
        except StopIteration: b=None; done_b=True
        assert done_a==done_b and a==b,(config['name'],prompt,stochastic,seed,a,b)
        assert audit_a==audit_b,(config['name'],prompt,seed,'step trace mismatch')
        for kind,audit in audit_a:
            hidden_values.add(audit['last_hidden']); feed_steps+=1
            feedback_steps+=int(kind=='feedback')
            head_count_checks+=sum('head' in step for step in audit['steps'])
            digest.update(json.dumps((kind,audit),sort_keys=True).encode())
        audit_a.clear(); audit_b.clear()
        assert reference.rng.getstate()==compiled.rng.getstate()
        assert reference.samples==compiled.samples
        sample_checks+=1
        if done_a: break
        outputs.append(a)
    assert reference.position==compiled.position
    assert 'histories' not in compiled.__dict__
    for row in compiled.caches:
        for cache in row:
            assert cache.count==compiled.position+1
            assert cache.shape()['allocated_word_slots']==cache.parameters()*cache.count.bit_length()
    return {'profile':config['name'],'prompt_length':len(prompt),'stochastic':stochastic,'seed':seed,
            'outputs':outputs,'feed_steps':feed_steps,'feedback_steps':feedback_steps,
            'per_head_phase_count_checks':head_count_checks,'random_state_checks':sample_checks,
            'hidden_word_codes':sorted(hidden_values),'trace_digest':digest.hexdigest(),
            'reference_storage':reference.storage(),'compiled_storage':compiled.storage(),
            'eos_seen':bool(outputs and outputs[-1]==EOS),'passed':True}


def run(path):
    started=time.perf_counter(); cases=[]
    prompts=[tuple(bits) for n in range(1,5) for bits in itertools.product(PROMPT,repeat=n)]
    modes=[(False,0),(True,0),(True,7),(True,23)]
    for config in CONFIGS:
        for prompt in prompts:
            for stochastic,seed in modes:
                cases.append(paired_case(config,prompt,stochastic,seed))
    # Empty/invalid-input controller paths are finite guards, not a neural oracle.
    guards=[paired_case(CONFIGS[0],prompt,True,7) for prompt in [(),(-2,99,2)]]
    assert all(case['outputs']==[INVALID] for case in guards)
    # Explicit EOS fixture, in addition to EOS observed in the nonconstant cases.
    eos_seed=next(seed for seed in range(100) if random.Random(seed).getrandbits(4) in (7,8))
    constant={**CONFIGS[0],'name':'EOS-control-only','constant_post':True}
    eos_control=paired_case(constant,(-2,),True,eos_seed)
    assert eos_control['outputs']==[EOS] and eos_control['feedback_steps']==0
    rng=random.Random(2026110504)
    long_prompt=tuple(rng.choice(PROMPT) for _ in range(128))
    long_cases=[paired_case(config,long_prompt,stochastic,23) for config in CONFIGS for stochastic in (False,True)]
    all_cases=cases+guards+[eos_control]+long_cases
    hidden=set(value for case in cases for value in case['hidden_word_codes'])
    output_patterns={tuple(case['outputs']) for case in cases}
    assert len(hidden)>1 and len(output_patterns)>1
    totals={'ordinary_cases':len(cases),'guard_cases':len(guards),'EOS_control_cases':1,'long_cases':len(long_cases),
            'feed_step_trace_comparisons':sum(c['feed_steps'] for c in all_cases),
            'per_head_phase_count_checks':sum(c['per_head_phase_count_checks'] for c in all_cases),
            'random_state_checks':sum(c['random_state_checks'] for c in all_cases),
            'distinct_hidden_word_codes':sorted(hidden),'distinct_output_patterns':len(output_patterns),
            'ordinary_cases_with_EOS':sum(c['eos_seen'] for c in cases)}
    report={'passed':True,'scope':'2 finite toy profiles, 2 layers and 2 heads each; not a real LLM',
            'configurations':CONFIGS,'totals':totals,'ordinary_cases':cases,'guard_cases':guards,
            'EOS_control':eos_control,'long_cases':long_cases,
            'sampling':'one bounded 4-bit draw; weights (7-h,2,7+h) sum to 16; forward has no RNG',
            'memory_caveat':'At toy sizes compiled numeric tables may be larger than full KV. Counts are not RSS and exclude program/PRNG/control. No practical speed/memory win claimed.',
            'observer_caveat':'Observers/history/output lists belong to passive test harness. Default stream has no observer, emits only after EOF, and never stores past outputs.',
            'seconds':time.perf_counter()-started,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'frozen_kernel_sha256':hashlib.sha256((HERE/'prefix_query_forest.py').read_bytes()).hexdigest(),
            'frozen_word_sha256':hashlib.sha256((HERE/'tiny_query_summary.py').read_bytes()).hexdigest(),
            'not_claimed':['batch re-evaluation equivalence','all GPU kernels','real 200B/human tasks','uniform polynomial cost in model size','OOM/wallclock API equivalence']}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'totals':totals,'seconds':report['seconds'],'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=HERE.parent/'reports/causal-model-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
