#!/usr/bin/env python3
"""Finite quality/resource sanity checks; not human or real-200B evaluation."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import random
import struct
import time

HERE=Path(__file__).resolve().parent
EOS=2


def kernel(prefix,x,shift):
    if EOS in prefix: return (F(0),F(0),F(1))
    parity=(x+sum(prefix))%2
    weights=(6+2*parity+shift,8-2*parity-shift,2)
    assert min(weights)>=0 and sum(weights)==16
    return tuple(F(w,16) for w in weights)


def law(horizon,x,shift):
    current={():F(1)}
    for _ in range(horizon):
        nxt={}
        for prefix,mass in current.items():
            for token,p in enumerate(kernel(prefix,x,shift)):
                if p: nxt[prefix+(token,)]=mass*p
        current=nxt
    assert sum(current.values())==1
    return current


def tv(a,b):
    return sum(abs(a.get(key,F(0))-b.get(key,F(0))) for key in set(a)|set(b))/2


def parity_loss(x,sequence):
    tokens=sequence[:sequence.index(EOS)] if EOS in sequence else sequence
    return F(sum(tokens)%2!=x)


def exact_quality():
    cases=[]
    for x in (0,1):
        for horizon in range(1,6):
            p=law(horizon,x,0); q=law(horizon,x,1)
            epsilon=F(1,16); distance=tv(p,q)
            multiplicative=1-(1-epsilon)**horizon
            linear=min(F(1),horizon*epsilon)
            assert distance<=multiplicative<=linear
            risk_p=sum(m*parity_loss(x,s) for s,m in p.items())
            risk_q=sum(m*parity_loss(x,s) for s,m in q.items())
            assert abs(risk_p-risk_q)<=distance
            # Post-hoc mathematical TV witness, NOT a benchmark loss.
            event={s for s in set(p)|set(q) if p.get(s,F(0))>q.get(s,F(0))}
            witness=sum(p.get(s,F(0))-q.get(s,F(0)) for s in event)
            assert witness==distance
            cases.append({'input_context':x,'horizon':horizon,'states':len(p),
                          'sequence_TV':str(distance),'coupling_bound':str(multiplicative),
                          'sum_bound':str(linear),'reference_parity_risk':str(risk_p),
                          'approximate_parity_risk':str(risk_q),'passed':True})
    return cases


def greedy(values):
    return max(range(len(values)),key=lambda i:values[i])


def softmax(values,tau):
    maximum=max(values)
    weights=[math.exp((v-maximum)/tau) for v in values]
    total=sum(weights)
    return [w/total for w in weights]


def logit_checks():
    eta=F(1,2**20)
    a=(F(0),F(0)); b=(-eta,eta)
    assert greedy(a)==0 and greedy(b)==1
    assert F(struct.unpack('!f',struct.pack('!f',float(eta)))[0])==eta
    safe_cases=0
    for eta_safe in (F(1,8),F(1,4),F(1,2)):
        values=(F(3),F(1),F(0)); gap=values[0]-values[1]
        assert gap>2*eta_safe
        for signs in itertools.product((-1,1),repeat=3):
            perturbed=tuple(v+s*eta_safe for v,s in zip(values,signs))
            assert greedy(perturbed)==0; safe_cases+=1
    numerical=0; max_excess=-1.0
    for width in (2,3):
        for values in itertools.product((-.5,0.,.5),repeat=width):
            for signs in itertools.product((-1.,1.),repeat=width):
                for err in (.01,.1,.5):
                    for tau in (.5,1.,2.):
                        p=softmax(values,tau)
                        q=softmax([v+s*err for v,s in zip(values,signs)],tau)
                        distance=sum(abs(a-b) for a,b in zip(p,q))/2
                        bound=math.tanh(err/(2*tau))
                        max_excess=max(max_excess,distance-bound)
                        assert distance<=bound+1e-12
                        numerical+=1
    tight=[]
    for err,tau in ((.1,1.),(.5,1.),(.5,.5)):
        p=softmax((-err/2,err/2),tau); q=softmax((err/2,-err/2),tau)
        distance=sum(abs(a-b) for a,b in zip(p,q))/2
        bound=math.tanh(err/(2*tau)); assert abs(distance-bound)<1e-12
        tight.append({'eta':err,'temperature':tau,'TV':distance,'bound':bound})
    return {'greedy_no_margin_counterexample':{'eta':str(eta),'reference_choice':0,'perturbed_choice':1,'output_TV':1},
            'safe_margin_cases':safe_cases,'softmax_float_sanity_cases':numerical,
            'softmax_max_excess_with_tolerance':max_excess,'tight_examples':tight,
            'scope':'exact rational margin controls; floating softmax sanity, not a proof/actual sampling-kernel error certificate'}


def interval_crossover(k,rate,kind):
    intervals=[]
    for h in range(1,128):
        if kind=='allocated': low=(1<<(h-1))-1; high=(1<<h)-2
        else: low=(1<<h)-2; high=(1<<(h+1))-3
        threshold=(k*h+rate-1)//rate
        fit=max(low,threshold)
        failure_end=min(high,threshold-1)
        intervals.append({'level':h,'start':low,'end':high,'required_t':threshold,
                          'first_fit_here':fit if fit<=high else None,
                          'last_failure_here':failure_end if failure_end>=low else None})
        if rate*low>=k*h:
            # For the next level, low_next=2*low+c, c=1 or 2.
            # This base inequality inductively guarantees all later intervals.
            first=min(v['first_fit_here'] for v in intervals if v['first_fit_here'] is not None)
            last=max(v['last_failure_here'] for v in intervals if v['last_failure_here'] is not None)
            return {'first_fit':first,'permanent_from':last+1,'fully_fitting_level_base':h,
                    'inductive_base_t':low,'intervals':intervals,
                    'proof_basis':'interval arithmetic plus low_next=2*low+c, not finite scan alone'}
    raise AssertionError('No analytic base found in configured limit')


def resource_ledger():
    spec=importlib.util.spec_from_file_location('frozen_causal',HERE/'causal_model_probe.py')
    model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    rng=random.Random(2026110504); prompt=tuple(rng.choice(model.PROMPT) for _ in range(128))
    reference=model.FullKV(model.CONFIGS[0],23); compiled=model.ForestModel(model.CONFIGS[0],23)
    trace_r=[]; trace_c=[]
    def observe_r(kind,audit): trace_r.append({'kind':kind,**reference.storage()})
    def observe_c(kind,audit): trace_c.append({'kind':kind,**compiled.storage()})
    output_r=list(reference.stream(iter(prompt),6,False,observe_r))
    output_c=list(compiled.stream(iter(prompt),6,False,observe_c))
    assert output_r==output_c
    previous=json.loads((HERE.parent/'reports/causal-model-tests-v1.json').read_text())['long_cases'][0]
    assert output_r==previous['outputs']
    k=compiled.storage()['parameter_forests']
    rate=reference.storage()['kv_numeric_words']//reference.position
    assert k==3996 and rate==8
    for row in trace_r: assert row['kv_numeric_words']==rate*row['position']
    for row in trace_c:
        p=row['position']; assert row['allocated_word_slots']==k*(p+1).bit_length()
        assert row['live_numeric_words']==k*(p+1).bit_count()
    p=compiled.position
    allocated=k*(p+1).bit_length()
    current_live=k*(p+1).bit_count()
    peak_live=k*((p+2).bit_length()-1)
    assert max(row['allocated_word_slots'] for row in trace_c)==allocated
    assert max(row['live_numeric_words'] for row in trace_c)==peak_live
    reference_peak=max(row['kv_numeric_words'] for row in trace_r)
    allocation=interval_crossover(k,rate,'allocated')
    live_peak=interval_crossover(k,rate,'peak_live')
    bound=allocation['permanent_from']
    first_live=next(t for t in range(1,bound+1) if k*(t+1).bit_count()<=rate*t)
    last_failure=max(t for t in range(bound) if k*(t+1).bit_count()>rate*t)
    instant={'first_fit':first_live,'permanent_from':last_failure+1,
             'failure_immediately_after_first_fit':k*(first_live+2).bit_count()>rate*(first_live+1),
             'proof_basis':'finite check below analytically certified allocated threshold; live<=allocated above it'}
    assert instant['failure_immediately_after_first_fit']
    budget=2048
    assert reference_peak<=budget<peak_live
    ledger={'position':p,'reference_KV_word_peak':reference_peak,
            'compiled_allocated_word_peak':allocated,'compiled_current_live_words':current_live,
            'compiled_post_feed_peak_live_words':peak_live,
            'allocated_over_reference_component_ratio':allocated/reference_peak,
            'parameter_forests':k,'reference_words_per_position':rate,
            'crossover_allocated':allocation,'crossover_peak_live':live_peak,
            'crossover_instant_live':instant,
            'budget_counterexample':{'numeric_cache_component_budget_words':budget,
              'reference_status':'OK','compiled_status':'BUDGET_FAIL','functional_outputs_equal':True,
              'resource_status_TV':1,'reference_resource_failure_loss':0,'compiled_resource_failure_loss':1,
              'illustrative_not_user_adopted':True,'hypothetical_component_observer':True,
              'actually_forced_OS_failure':False},
            'measurement_scope':'post-feed logical numeric cache snapshots; not RSS/device total, excludes readonly weights/program, PRNG/control and transient scratch',
            'analytical_scope':'packed logical KV versus level table; not all layouts/compilers',
            'trace':{'reference':trace_r,'compiled':trace_c}}
    return ledger


def run(path):
    started=time.perf_counter()
    quality=exact_quality(); logits=logit_checks(); ledger=resource_ledger()
    trace=ledger.pop('trace')
    trace_path=path.with_name('adequacy-resource-trace-v1.json')
    trace_path.write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
    report={'passed':True,'exact_sequence_cases':quality,'logit_controls':logits,'resource_ledger':ledger,
            'resource_trace_path':str(trace_path),'resource_trace_sha256':hashlib.sha256(trace_path.read_bytes()).hexdigest(),
            'seconds':time.perf_counter()-started,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'frozen_model_sha256':hashlib.sha256((HERE/'causal_model_probe.py').read_bytes()).hexdigest(),
            'not_claimed':['human accuracy estimates','real 200B performance','user acceptance of numeric budgets','all compiler lower bound','hardware/API resource equivalence'],
            'loss_caveat':'TV-maximizing event is a post-hoc mathematical witness, not a preregistered performance benchmark.'}
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'exact_sequence_cases':len(quality),
                      'softmax_sanity_cases':logits['softmax_float_sanity_cases'],
                      'allocated_crossover':ledger['crossover_allocated']['permanent_from'],
                      'peak_live_crossover':ledger['crossover_peak_live']['permanent_from'],
                      'instant_live_first_fit':ledger['crossover_instant_live']['first_fit'],
                      'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=HERE.parent/'reports/adequacy-probe-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
