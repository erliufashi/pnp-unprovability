#!/usr/bin/env python3
"""Fixed-H lazy reconstruction sanity. Numeric-cache counts are NOT RSS."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_causal',HERE/'causal_model_probe.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
pspec=importlib.util.spec_from_file_location('frozen_pruning',HERE/'pruned_query_probe.py')
p=importlib.util.module_from_spec(pspec); pspec.loader.exec_module(p)
f=m.f; t=f.t


class Hybrid(m.FullKV):
    def __init__(self,config,seed,horizon,backend='full',diagnostics=False):
        assert isinstance(horizon,int) and horizon>=0 and backend in ('full','pruned')
        super().__init__(config,seed)
        self.horizon=horizon; self.backend=backend; self.diagnostics=diagnostics
        self.caches=None; self.compiled_profile=None; self.metadata_bytes=0
        self.transition=None; self.cache_component_peak=0
    def counts(self):
        return m.FullKV.counts(self) if self.caches is None else m.ForestModel.counts(self)
    def attend(self,layer,head,q,k,v):
        return (m.FullKV.attend(self,layer,head,q,k,v) if self.caches is None else
                m.ForestModel.attend(self,layer,head,q,k,v))
    def component_now(self):
        if self.caches is None:
            return sum(2*len(h) for row in self.histories for h in row)
        return sum(c.parameters()*c.count.bit_length() for row in self.caches for c in row)
    def rebuild(self):
        assert self.caches is None and self.transition is None and self.position==self.horizon
        old=self.histories
        assert all(len(history)==self.position for row in old for history in row)
        control=(self.position,self.last_hidden,self.samples)
        rng_before=self.rng.getstate() if self.diagnostics else None
        native_words=sum(2*len(history) for row in old for history in row)
        if self.backend=='pruned':
            # Deferred until the switch: never analyze/materialize this table early.
            self.compiled_profile=p.compile_profile(self.config)
            self.metadata_bytes=len(json.dumps(self.compiled_profile,sort_keys=True).encode())
        new=[]; replay_records=0; read_checks=0
        for layer,row in enumerate(old):
            out=[]
            for head,history in enumerate(row):
                cache=(f.TreeCache() if self.backend=='full' else
                       p.PrunedCache(self.compiled_profile['heads'][layer][head]))
                for k,v in history:
                    cache.append(k,v); replay_records+=1
                assert cache.count==self.position+1
                if self.diagnostics:
                    queries=t.QUERIES if self.backend=='full' else cache.cert['queries']
                    for q in queries:
                        # Validation observer only; never repairs the cache from answers.
                        assert cache.query(q)==f.literal_kernel(history,q)
                        read_checks+=1
                out.append(cache)
            new.append(out)
        self.caches=new
        compressed_words=self.component_now()
        self.cache_component_peak=max(self.cache_component_peak,native_words+compressed_words)
        self.histories=None  # No old-token/KV alias is retained by the solver.
        assert control==(self.position,self.last_hidden,self.samples)
        if self.diagnostics: assert rng_before==self.rng.getstate()
        self.transition={'boundary':self.position,'backend':self.backend,'internal_records_replayed':replay_records,
                         'native_words_at_boundary':native_words,'compressed_slots_at_boundary':compressed_words,
                         'simultaneously_held_cache_words':native_words+compressed_words,
                         'read_checks_at_rebuild':read_checks,'RNG_untouched':True,
                         'head_counts':self.counts(),'input_or_output_reread':False,
                         'scope':'cache components only; compile scratch/code/metadata/control excluded'}
    def feed(self,token):
        if self.caches is None and self.position>=self.horizon: self.rebuild()
        audit=m.Base.feed(self,token)
        self.cache_component_peak=max(self.cache_component_peak,self.component_now())
        return audit
    def storage(self):
        return {'position':self.position,'mode':'native' if self.caches is None else self.backend,
                'current_cache_words':self.component_now(),'cache_component_peak':self.cache_component_peak,
                'parameter_forests':0 if self.caches is None else sum(c.parameters() for row in self.caches for c in row),
                'metadata_serialized_bytes':self.metadata_bytes,
                'scope':'numeric cache component ledger, not RSS/whole-process budget'}


def paired(config,prompt,horizon,stochastic,seed,budget=6,backend='full',competitive_control=False):
    a=m.FullKV(config,seed); b=Hybrid(config,seed,horizon,backend,diagnostics=True)
    assert b.caches is None and b.compiled_profile is None and b.storage()['parameter_forests']==0
    traces=[[],[]]; native_checks=0; competitive_checks=0
    def observe_a(kind,audit): traces[0].append((kind,audit))
    def observe_b(kind,audit):
        nonlocal native_checks,competitive_checks
        traces[1].append((kind,audit))
        if b.position<=horizon:
            assert b.caches is None and b.compiled_profile is None
            assert b.component_now()==8*b.position
            native_checks+=1
        if competitive_control:
            assert b.cache_component_peak<=2*8*b.position
            if b.position>horizon: assert b.component_now()<=8*b.position
            competitive_checks+=1
    sa=a.stream(iter(prompt),budget,stochastic,observe_a)
    sb=b.stream(iter(prompt),budget,stochastic,observe_b)
    outputs=[]; feeds=0; rng_checks=0; digest=hashlib.sha256(); feedback=0
    while True:
        try: x=next(sa); da=False
        except StopIteration: x=None; da=True
        try: y=next(sb); db=False
        except StopIteration: y=None; db=True
        assert (da,x)==(db,y)
        assert traces[0]==traces[1]
        for item in traces[0]:
            feeds+=1; feedback+=int(item[0]=='feedback'); digest.update(json.dumps(item,sort_keys=True).encode())
        traces[0].clear(); traces[1].clear()
        assert a.rng.getstate()==b.rng.getstate() and a.samples==b.samples
        rng_checks+=1
        if da: break
        outputs.append(x)
    assert a.position==b.position
    if b.position<=horizon:
        assert b.transition is None and b.caches is None
    else:
        assert b.transition is not None and b.transition['boundary']==horizon and b.histories is None
        assert b.transition['internal_records_replayed']==4*horizon
        for row in b.caches:
            for cache in row:
                assert cache.count==b.position+1
                assert cache.shape()['allocated_word_slots']==cache.parameters()*cache.count.bit_length()
    return {'profile':config['name'],'backend':backend,'H':horizon,'prompt_length':len(prompt),
            'stochastic':stochastic,'seed':seed,'outputs':outputs,'feed_comparisons':feeds,
            'feedback_feed_comparisons':feedback,'RNG_checks':rng_checks,
            'native_prefix_checks':native_checks,'competitive_component_checks':competitive_checks,
            'trace_digest':digest.hexdigest(),'transition':b.transition,'hybrid':b.storage(),
            'reference':a.storage(),'passed':True}


def crossover_certificate(K,a=8):
    intervals=[]; last_bad=-1
    for length in range(1,65):
        lo=(1<<(length-1))-1; hi=(1<<length)-2
        first_good=(K*length+a-1)//a
        bad=min(hi,first_good-1)
        if bad>=lo: last_bad=max(last_bad,bad)
        intervals.append({'L':length,'lo':lo,'hi':hi,'last_bad_if_any':bad if bad>=lo else None})
        if a*lo>=K*length:
            return {'K':K,'rate':a,'permanent_H':last_bad+1,'first_fully_good_L':length,
                    'intervals':intervals,'future_proof':'a*next_lo=2*a*lo+a >=2*K*L+a >=K*(L+1)',
                    'scope':'allocated cache components only; no time/RSS/readonly guarantee'}
    raise AssertionError('fixture interval limit exceeded')


def run(path):
    assert not path.exists(),'immutable run report already exists; use a fresh run directory'
    started=time.perf_counter(); cases=[]
    prompts=[bits for length in range(1,4) for bits in itertools.product(m.PROMPT,repeat=length)]
    for config in m.CONFIGS:
        for horizon in (0,1,3,6,16):
            for prompt in prompts:
                for stochastic,seed in [(False,0),(True,0),(True,7)]:
                    cases.append(paired(config,prompt,horizon,stochastic,seed))
    pruned_cases=[paired(config,prompt,h,True,23,backend='pruned') for config in m.CONFIGS
                  for h in (0,1,3) for prompt in [(-2,),(2,-2,2)]]
    boundaries=[]
    for config in m.CONFIGS:
        for horizon in (1,3,6):
            exact=paired(config,(-2,)*horizon,horizon,False,0,budget=0)
            beyond=paired(config,(-2,)*(horizon+1),horizon,False,0,budget=0)
            assert exact['transition'] is None and beyond['transition'] is not None
            boundaries.extend([exact,beyond])
    guards=[paired(m.CONFIGS[0],prompt,h,True,7) for h in (0,3) for prompt in [(),(-2,99,2)]]
    constant={**m.CONFIGS[0],'name':'EOS-hybrid-control-only','constant_post':True}
    eos_seed=next(seed for seed in range(100) if random.Random(seed).getrandbits(4) in (7,8))
    eos=paired(constant,(-2,),3,True,eos_seed)
    assert eos['outputs']==[m.EOS] and eos['transition'] is None and eos['hybrid']['parameter_forests']==0
    rng=random.Random(2026110504); long_prompt=tuple(rng.choice(m.PROMPT) for _ in range(128))
    long_cases=[paired(config,long_prompt,16,stochastic,23) for config in m.CONFIGS for stochastic in (False,True)]
    # Structural control only, NOT a chosen human baseline.
    zero={**m.CONFIGS[0],'name':'zero-key-competitive-control-only',
          'heads':[[(aq,bq,0,0,av,bv) for aq,bq,ak,bk,av,bv in row] for row in m.CONFIGS[0]['heads']]}
    control=[]
    for length in (1,7,8,9,15,16,31,32,64):
        prompt=tuple(rng.choice(m.PROMPT) for _ in range(length))
        for stochastic,seed in [(False,0),(True,0),(True,7)]:
            result=paired(zero,prompt,8,stochastic,seed,backend='pruned',competitive_control=True)
            if result['transition'] is not None: assert result['hybrid']['parameter_forests']==16
            control.append(result)
    certificates=[crossover_certificate(K) for K in (3996,752,776,16)]
    assert [cert['permanent_H'] for cert in certificates]==[6494,1034,1067,8]
    all_cases=cases+pruned_cases+boundaries+guards+[eos]+long_cases+control
    report={'passed':True,'scope':'fixed-H word/profile conditional construction, not actual 200B',
            'ordinary_cases':len(cases),'pruned_cases':len(pruned_cases),'boundary_cases':len(boundaries),
            'total_cases':len(all_cases),'feed_comparisons':sum(c['feed_comparisons'] for c in all_cases),
            'RNG_checks':sum(c['RNG_checks'] for c in all_cases),
            'native_prefix_checks':sum(c['native_prefix_checks'] for c in all_cases),
            'rebuilds':sum(c['transition'] is not None for c in all_cases),
            'rebuild_Read_checks':sum(c['transition']['read_checks_at_rebuild'] for c in all_cases if c['transition']),
            'competitive_component_checks':sum(c['competitive_component_checks'] for c in control),
            'ordinary_digest':hashlib.sha256(''.join(c['trace_digest'] for c in cases).encode()).hexdigest(),
            'ordinary_sample_cases':cases[:3],'boundary_records':boundaries,'guards':guards,'EOS_control':eos,
            'long_cases':long_cases,'pruned_case_records':pruned_cases,'zero_key_control':control,
            'permanent_crossover_certificates':certificates,
            'memory_caveat':'Before H no mutable forest; after small test H it can still exceed native. Overlap ledger counts old+new caches, not compiler scratch, code, readonly, Python or total RSS.',
            'test_caveat':'All-query replay checks are passive diagnostics, never supply corrections. Production stream default has no observer; solver retains no output history.',
            'seconds':time.perf_counter()-started,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'frozen_dependencies':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in
                ['causal_model_probe.py','prefix_query_forest.py','tiny_query_summary.py','pruned_query_probe.py']},
            'not_claimed':['actual 200B/human adequacy','2x full device','wallclock competitive','uniform model/H constants','new T3 scope']}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['passed','total_cases','feed_comparisons','RNG_checks','rebuilds','seconds']},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=HERE.parent/'reports/hybrid-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
