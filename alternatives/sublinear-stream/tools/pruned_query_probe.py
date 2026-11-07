#!/usr/bin/env python3
"""Certified finite-domain specialization sanity, not actual 200B optimization.

Compile domains from the complete frozen toy phi input alphabet, NOT prompts.
Certificates/metadata are read-only and their size is reported separately.
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
spec=importlib.util.spec_from_file_location('frozen_model',HERE/'causal_model_probe.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
f=m.f
t=f.t


def selected_closure(q,maximum,keys):
    states={(0,False)}
    for key in keys:
        score=t.mul(q,key)
        if score<=maximum:
            states.add((t.exponential(t.sub(score,maximum)),score==maximum))
    while True:
        nxt=set(states)
        for a,seen_a in states:
            for b,seen_b in states:
                nxt.add((t.add(a,b),seen_a or seen_b))
        if nxt==states: break
        states=nxt
    selected=tuple(sorted({value for value,seen in states if seen},key=t.INDEX.get))
    assert selected
    return selected,tuple(sorted(states,key=lambda pair:(t.INDEX[pair[0]],pair[1])))


def certificate(queries,keys):
    queries=tuple(sorted(set(queries))); keys=tuple(sorted(set(keys)))
    assert queries and keys and all(q in t.F for q in queries) and all(k in t.F for k in keys)
    signatures={}; rep_for={}; reps=[]; score_signatures={}
    for q in queries:
        signature=tuple(t.mul(q,k) for k in keys)
        if signature not in signatures:
            signatures[signature]=q; reps.append(q); score_signatures[q]=signature
        rep_for[q]=signatures[signature]
    maxima={}; normalizers={}; closures={}
    for q in reps:
        maxima[q]=tuple(sorted(set(score_signatures[q])))
        normalizers[q]={}; closures[q]={}
        for maximum in maxima[q]:
            zs,closure=selected_closure(q,maximum,keys)
            normalizers[q][maximum]=zs; closures[q][maximum]=closure
    count=len(reps)+sum(len(maxima[q]) for q in reps)+sum(len(zs) for q in reps for zs in normalizers[q].values())
    return {'queries':queries,'keys':keys,'representatives':tuple(reps),'rep_for':rep_for,
            'score_signatures':score_signatures,'maxima':maxima,'normalizers':normalizers,
            'closure_proofs':closures,'parameter_forests':count,
            'empty_read':0,'domain_method':'static whole finite phi domain, not observed prompt values'}


def compile_profile(config):
    started=time.perf_counter(); rows=[]
    for heads in config['heads']:
        row=[]
        for weights in heads:
            assert all(value in t.F for value in weights)
            triples=[m.qkv(h,p,weights) for h in t.F for p in (1,2,3)]
            cert=certificate([q for q,k,v in triples],[k for q,k,v in triples])
            cert['phi_weights']=weights
            cert['phi_inputs']='all h in F9; position p=1,2,3 spans exact period'
            cert['value_image']=tuple(sorted({v for q,k,v in triples}))
            row.append(cert)
        rows.append(row)
    result={'profile':config['name'],'config_sha256':hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest(),
            'generator_sha256':hashlib.sha256((HERE/'causal_model_probe.py').read_bytes()).hexdigest(),
            'word_sha256':hashlib.sha256((HERE/'tiny_query_summary.py').read_bytes()).hexdigest(),
            'heads':rows,'compile_seconds':time.perf_counter()-started}
    result['total_parameter_forests']=sum(cert['parameter_forests'] for row in rows for cert in row)
    assert result['total_parameter_forests']<=4*999
    return result


class PrunedCache:
    def __init__(self,cert):
        self.cert=cert
        self.count=1; self.merges=0
        self.maxima={q:[t.LOW] for q in cert['representatives']}
        self.den={(q,maximum):[0] for q in cert['representatives'] for maximum in cert['maxima'][q]}
        self.out={(q,maximum,z):[0] for q in cert['representatives'] for maximum in cert['maxima'][q]
                  for z in cert['normalizers'][q][maximum]}
    def clone(self):
        other=object.__new__(PrunedCache)
        other.cert=self.cert; other.count=self.count; other.merges=self.merges
        other.maxima={key:a.copy() for key,a in self.maxima.items()}
        other.den={key:a.copy() for key,a in self.den.items()}
        other.out={key:a.copy() for key,a in self.out.items()}
        return other
    def arrays(self):
        yield from self.maxima.values(); yield from self.den.values(); yield from self.out.values()
    def parameters(self):
        return len(self.maxima)+len(self.den)+len(self.out)
    def append(self,k,v):
        assert k in self.cert['keys'] and v in t.WORDS
        carry=f.trailing_ones(self.count)
        for q in self.cert['representatives']:
            score=t.mul(q,k)
            self.merges+=f.append_levels(self.maxima[q],score,t.maximum,carry)
            for maximum in self.cert['maxima'][q]:
                u=t.exponential(t.sub(score,maximum))
                self.merges+=f.append_levels(self.den[q,maximum],u,t.add,carry)
                for z in self.cert['normalizers'][q][maximum]:
                    leaf=t.mul(t.div(u,z),v)
                    self.merges+=f.append_levels(self.out[q,maximum,z],leaf,t.add,carry)
        self.count+=1
    def query(self,q):
        assert q in self.cert['rep_for'],'query outside certified domain'
        if self.count==1: return 0
        rep=self.cert['rep_for'][q]
        maximum=f.root_levels(self.maxima[rep],self.count,t.maximum)
        assert maximum in self.cert['maxima'][rep]
        z=f.root_levels(self.den[rep,maximum],self.count,t.add)
        assert z in self.cert['normalizers'][rep][maximum], 'selected certificate violated'
        return f.root_levels(self.out[rep,maximum,z],self.count,t.add)
    def shape(self):
        return {'seed_inclusive_count':self.count,'level_span':self.count.bit_length(),
                'active_blocks':self.count.bit_count(),
                'allocated_word_slots':sum(len(a) for a in self.arrays()),
                'live_numeric_words':sum(value is not None for a in self.arrays() for value in a),
                'merges':self.merges}


class PrunedModel(m.ForestModel):
    def __init__(self,config,seed,compiled):
        # Deliberately skip ForestModel.__init__: never allocate a full table.
        m.Base.__init__(self,config,seed)
        expected=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
        assert compiled['config_sha256']==expected
        assert compiled['generator_sha256']==hashlib.sha256((HERE/'causal_model_probe.py').read_bytes()).hexdigest()
        assert compiled['word_sha256']==hashlib.sha256((HERE/'tiny_query_summary.py').read_bytes()).hexdigest()
        self.caches=[[PrunedCache(cert) for cert in row] for row in compiled['heads']]


def kernel_campaign(cert,depth,values):
    alphabet=list(itertools.product(cert['keys'],values))
    prefixes=0; comparisons=0; digest=hashlib.sha256()
    def visit(cache,history):
        nonlocal prefixes,comparisons
        prefixes+=1
        assert cache.parameters()==cert['parameter_forests']
        assert cache.shape()['allocated_word_slots']==cache.parameters()*cache.count.bit_length()
        assert cache.merges==cache.parameters()*(cache.count-cache.count.bit_count())
        for q in cert['queries']:
            result=cache.query(q); expected=f.literal_kernel(history,q)
            assert result==expected,(history,q,result,expected)
            digest.update(bytes([t.QINDEX[q],t.INDEX[result]])); comparisons+=1
        if len(history)<depth:
            for record in alphabet:
                nxt=cache.clone(); nxt.append(*record); visit(nxt,history+[record])
    visit(PrunedCache(cert),[])
    return {'prefix_cases':prefixes,'query_comparisons':comparisons,'max_length':depth,
            'alphabet_size':len(alphabet),'parameter_forests':cert['parameter_forests'],
            'output_digest':digest.hexdigest(),'passed':True}


def triple_case(config,compiled,prompt,stochastic,seed,budget=6):
    models=[m.FullKV(config,seed),m.ForestModel(config,seed),PrunedModel(config,seed,compiled)]
    observations=[[],[],[]]
    def observer(index):
        return lambda kind,audit: observations[index].append((kind,audit))
    streams=[model.stream(iter(prompt),budget,stochastic,observer(i)) for i,model in enumerate(models)]
    outputs=[]; feed_steps=0; rng_checks=0; digest=hashlib.sha256()
    while True:
        results=[]
        for stream in streams:
            try: results.append((False,next(stream)))
            except StopIteration: results.append((True,None))
        assert results[0]==results[1]==results[2]
        assert observations[0]==observations[1]==observations[2]
        for item in observations[0]:
            feed_steps+=1; digest.update(json.dumps(item,sort_keys=True).encode())
        for items in observations: items.clear()
        assert models[0].rng.getstate()==models[1].rng.getstate()==models[2].rng.getstate()
        rng_checks+=1
        if results[0][0]: break
        outputs.append(results[0][1])
    assert models[0].position==models[1].position==models[2].position
    assert 'histories' not in models[2].__dict__
    assert models[2].storage()['parameter_forests']==compiled['total_parameter_forests']
    return {'profile':config['name'],'prompt_length':len(prompt),'stochastic':stochastic,'seed':seed,
            'outputs':outputs,'feed_step_comparisons':feed_steps,'random_state_checks':rng_checks,
            'trace_digest':digest.hexdigest(),'reference':models[0].storage(),
            'full_table':models[1].storage(),'pruned':models[2].storage(),'passed':True}


def run(path):
    started=time.perf_counter()
    profiles=[compile_profile(config) for config in m.CONFIGS]
    readonly_before=[hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest() for p in profiles]
    kernels=[]
    for profile in profiles:
        for row in profile['heads']:
            for cert in row: kernels.append(kernel_campaign(cert,2,(-4,0,4)))
    zero_key=certificate(t.QUERIES,(0,))
    assert len(zero_key['representatives'])==1 and zero_key['parameter_forests']==4
    zero_control=kernel_campaign(zero_key,3,t.F)
    # Inactive-m normalizer can lie outside its SELECTED certificate.
    witness=PrunedCache(profiles[0]['heads'][0][0]); witness.append(-2,2)
    rep=witness.cert['rep_for'][3]; inactive=-4
    inactive_z=f.root_levels(witness.den[rep,inactive],witness.count,t.add)
    allowed=witness.cert['normalizers'][rep][inactive]
    assert inactive_z not in allowed
    assert witness.query(3)==f.literal_kernel([(-2,2)],3)
    # Unsound generic rules, not predictions of a real policy activation.
    h=[(-2,-4),(2,4)]
    q1=f.literal_kernel(h,1); q2=f.literal_kernel(h,2); assert q1!=q2
    h2=[(-2,2)]; unseen=f.literal_kernel(h2,2); assert unseen!=0
    controls={'same_sign_queries_not_equivalent':{'history':h,'q1_output':q1,'q2_output':q2},
              'observed_query_default_zero_is_unsound':{'observed_queries':[0],'query':2,'correct':unseen,'unsafe_default':0},
              'inactive_D_outside_selected_Z_is_allowed':{'q':3,'inactive_m':inactive,'counterfactual_z':inactive_z,
                 'selected_Z_for_inactive_m':list(allowed),'actual_read_matches':True},
              'scope':'kernel product-domain controls, not measured trained-LM activations'}
    cases=[]
    prompts=[tuple(bits) for n in range(1,5) for bits in itertools.product(m.PROMPT,repeat=n)]
    for config,compiled in zip(m.CONFIGS,profiles):
        for prompt in prompts:
            for stochastic,seed in [(False,0),(True,0),(True,7),(True,23)]:
                cases.append(triple_case(config,compiled,prompt,stochastic,seed))
    guards=[triple_case(m.CONFIGS[0],profiles[0],prompt,True,7) for prompt in [(),(-2,99,2)]]
    eos_seed=next(seed for seed in range(100) if random.Random(seed).getrandbits(4) in (7,8))
    constant={**m.CONFIGS[0],'name':'EOS-pruning-control-only','constant_post':True}
    constant_cert=compile_profile(constant)
    eos=triple_case(constant,constant_cert,(-2,),True,eos_seed)
    assert eos['outputs']==[m.EOS]
    rng=random.Random(2026110504); prompt=tuple(rng.choice(m.PROMPT) for _ in range(128))
    long_cases=[triple_case(config,compiled,prompt,stochastic,23)
                for config,compiled in zip(m.CONFIGS,profiles) for stochastic in (False,True)]
    # The retrieval family's raw signatures remain distinct, as M17 predicts.
    nspec=importlib.util.spec_from_file_location('frozen_retrieval',HERE/'neural_retrieval_probe.py')
    neural=importlib.util.module_from_spec(nspec); nspec.loader.exec_module(neural)
    retrieval_signatures=[]
    for d in range(1,5):
        signatures={tuple(neural.neural_score(neural.bits_of(q,d),neural.bits_of(k,d))[0]
                          for k in range(1<<d)) for q in range(1<<d)}
        assert len(signatures)==1<<d
        retrieval_signatures.append({'d':d,'queries':1<<d,'distinct_signatures':len(signatures)})
    assert readonly_before==[hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest() for p in profiles]
    serialized=json.dumps(profiles,ensure_ascii=False,sort_keys=True)
    cert_path=path.with_name('pruning-certificates-v1.json'); cert_path.write_text(serialized+'\n')
    all_cases=cases+guards+[eos]+long_cases
    report={'passed':True,'scope':'frozen toy profile static certificates; not arbitrary 200B optimizer',
            'readonly_certificates_unchanged':True,
            'profile_costs':[{'profile':p['profile'],'full_parameter_forests':3996,
                              'pruned_parameter_forests':p['total_parameter_forests'],
                              'certificate_json_bytes':len(json.dumps(p,ensure_ascii=False,sort_keys=True).encode()),
                              'compile_seconds':p['compile_seconds']} for p in profiles],
            'kernel_campaigns':kernels,'zero_key_merge_control':zero_control,'negative_controls':controls,
            'ordinary_cases':len(cases),'guard_cases':len(guards),'EOS_control':eos,
            'policy_feed_step_comparisons':sum(c['feed_step_comparisons'] for c in all_cases),
            'policy_random_state_checks':sum(c['random_state_checks'] for c in all_cases),
            'long_cases':long_cases,'ordinary_trace_digest':hashlib.sha256(''.join(c['trace_digest'] for c in cases).encode()).hexdigest(),
            'retrieval_signatures':retrieval_signatures,
            'certificate_path':str(cert_path),'certificate_sha256':hashlib.sha256(cert_path.read_bytes()).hexdigest(),
            'seconds':time.perf_counter()-started,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependencies_sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in
              ['causal_model_probe.py','prefix_query_forest.py','tiny_query_summary.py','neural_retrieval_probe.py']},
            'not_claimed':['RSS/latency win','actual 200B use','minimal quotient','polynomial static-analysis cost in model size','new termination certificate'],
            'metadata_note':'JSON contains proof closures and decimal word keys; runtime object uses integer keys. Bytes are serialized artifact size, not actual resident memory. Static data must be charged separately.'}
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'profile_costs':report['profile_costs'],
                      'kernel_query_comparisons':sum(c['query_comparisons'] for c in kernels)+zero_control['query_comparisons'],
                      'policy_feed_step_comparisons':report['policy_feed_step_comparisons'],
                      'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=HERE.parent/'reports/pruning-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
