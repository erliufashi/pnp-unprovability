#!/usr/bin/env python3
"""Canonical finite-precision attention scheduling sanity/aux-memory probe.

NOT an oracle for arbitrary hardware IEEE32, torch, fused kernels or 200B LLMs.
Both schedules intentionally share the same pure primitives/reduction trees.
"""
import argparse
import gc
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import time
import tracemalloc


def f32(x):
    return struct.unpack('!f',struct.pack('!f',x))[0]


def add(a,b): return f32(a+b)
def mul(a,b): return f32(a*b)
def sub(a,b): return f32(a-b)
def div(a,b): return f32(a/b)
def exp32(a): return f32(math.exp(a))


def fold(values):
    out=f32(0)
    for value in values: out=add(out,value)
    return out


def dot(a,b):
    return fold(mul(x,y) for x,y in zip(a,b))


def softmax(row):
    maximum=max(row)
    values=[exp32(sub(x,maximum)) for x in row]
    total=fold(values)
    return [div(value,total) for value in values]


def materialized(q,k,v,causal=False):
    c=len(q); d=len(q[0]); scale=f32(1/math.sqrt(d))
    scores=[]
    for i in range(c):
        scores.append([mul(dot(q[i],k[j]),scale) if not causal or j<=i else -math.inf
                       for j in range(c)])
    probabilities=[softmax(row) for row in scores]
    output=[]
    for i in range(c):
        output.append([fold(mul(probabilities[i][j],v[j][channel]) for j in range(c))
                       for channel in range(d)])
    return output,{'score_cells':sum(map(len,scores)),
                   'probability_cells':sum(map(len,probabilities))}


def row_scheduled(q,k,v,causal=False):
    c=len(q); d=len(q[0]); scale=f32(1/math.sqrt(d))
    output=[]; peak_score_cells=0; peak_probability_cells=0
    for i in range(c):
        scores=[mul(dot(q[i],k[j]),scale) if not causal or j<=i else -math.inf
                for j in range(c)]
        probabilities=softmax(scores)
        peak_score_cells=max(peak_score_cells,len(scores))
        peak_probability_cells=max(peak_probability_cells,len(probabilities))
        output.append([fold(mul(probabilities[j],v[j][channel]) for j in range(c))
                       for channel in range(d)])
        del scores,probabilities
    return output,{'peak_score_cells':peak_score_cells,
                   'peak_probability_cells':peak_probability_cells}


def bits(matrix):
    return b''.join(struct.pack('!f',value) for row in matrix for value in row)


def inputs(c,d,seed):
    rng=random.Random(seed)
    return tuple([[f32(rng.uniform(-2,2)) for _ in range(d)] for _ in range(c)] for _ in range(3))


def measure(function,q,k,v):
    # q/k/v already exist. This is auxiliary traced Python allocation, NOT RSS.
    gc.collect(); tracemalloc.start()
    started=time.perf_counter()
    value,stats=function(q,k,v)
    _,peak=tracemalloc.get_traced_memory()
    elapsed=time.perf_counter()-started
    tracemalloc.stop()
    return value,stats,peak,elapsed


def run(report_path):
    checks=[]; numerical=[]; memory=[]
    for c in (1,2,3,7,16,31):
        for d in (1,2,4):
            for causal in (False,True):
                q,k,v=inputs(c,d,seed=20261105+100*c+10*d+int(causal))
                a,a_stats=materialized(q,k,v,causal)
                b,b_stats=row_scheduled(q,k,v,causal)
                assert bits(a)==bits(b),(c,d,causal)
                assert a_stats['score_cells']==c*c and b_stats['peak_score_cells']==c
                numerical.append({'C':c,'d':d,'causal':causal,'bitwise_equal':True,
                                  'output_sha256':hashlib.sha256(bits(a)).hexdigest()})
    checks.append({'name':'36 finite shape/mask cases bitwise equal','passed':True,'cases':len(numerical)})
    a=f32(1e20); b=f32(-1e20); c=f32(3.14)
    left=add(add(a,b),c); right=add(a,add(b,c))
    assert left!=right and left==c and right==0
    reassociation={'a':a,'b':b,'c':c,'left':left,'right':right,'equal':False}
    checks.append({'name':'reassociation changes canonical float32 result','passed':True})
    for c in (16,32,64,128):
        q,k,v=inputs(c,4,seed=9000+c)
        a,astats,apeak,atime=measure(materialized,q,k,v)
        b,bstats,bpeak,btime=measure(row_scheduled,q,k,v)
        assert bits(a)==bits(b)
        assert astats['score_cells']==c*c and bstats['peak_score_cells']==c
        if c>=64: assert apeak>bpeak,(c,apeak,bpeak)
        memory.append({'C':c,'d':4,'materialized':{'aux_peak_bytes':apeak,'seconds':atime,**astats},
                       'row_scheduled':{'aux_peak_bytes':bpeak,'seconds':btime,**bstats},
                       'bitwise_equal':True,'inputs_excluded_from_trace':True})
    checks.append({'name':'4 auxiliary-memory measurements and logical buffer counts','passed':True})
    # Explicit budget-return counterexample: numerical equality on successful
    # runs does not imply equality of a memory-limit API.
    length=16; budget_cells=32
    materialized_status='OOM' if length*length>budget_cells else 'OK'
    row_status='OOM' if length>budget_cells else 'OK'
    assert materialized_status!=row_status
    checks.append({'name':'observable memory-limit return may change','passed':True})
    report={'passed':True,'kind':'finite sanity + auxiliary Python allocation; not proof assistant',
            'checks':checks,'numerical_cases':numerical,'reassociation_counterexample':reassociation,
            'memory_measurements':memory,
            'budget_counterexample':{'C':length,'score_cell_budget':budget_cells,
                                    'materialized':materialized_status,'row_scheduled':row_status},
            'semantics':'Python arithmetic then struct binary32; same host libm exp then binary32; shared primitive/reduction helpers',
            'not_claimed':['torch or GPU kernel equivalence','all IEEE32 hardware implementations','real 200B measurement',
                           'proof of asymptotic complexity from finite measurements','unchanged OOM/wallclock-timeout protocol'],
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'bitwise_cases':len(numerical),'memory_sizes':[m['C'] for m in memory],
                      'report':str(report_path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=Path(__file__).resolve().parents[1]/'reports/hour1-tests.json')
    raise SystemExit(run(parser.parse_args().report))
