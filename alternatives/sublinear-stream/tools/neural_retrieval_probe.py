#!/usr/bin/env python3
"""Finite neural-score/one-hot retrieval sanity checks, not a trained LLM.

The reference intentionally stores all values/keys. No small-space compiler
is claimed; the state lower bound is proved separately, not by these tests.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import struct
import time


def f32(x): return struct.unpack('!f',struct.pack('!f',x))[0]


class Ops:
    def __init__(self): self.count=0
    def add(self,a,b): self.count+=1; return f32(a+b)
    def sub(self,a,b): self.count+=1; return f32(a-b)
    def mul(self,a,b): self.count+=1; return f32(a*b)
    def relu(self,a): self.count+=1; return f32(max(0.0,a))


def neural_score(q,k):
    assert len(q)==len(k) and len(q)>=1
    assert all(bit in (0,1) for bit in q+k)
    op=Ops(); equal=[]
    for a,b in zip(q,k):
        a=f32(a); b=f32(b)
        difference=op.add(op.relu(op.sub(a,b)),op.relu(op.sub(b,a)))
        equal.append(op.sub(1.0,difference))
    depth=0; and_nodes=0
    while len(equal)>1:
        nxt=[]
        for i in range(0,len(equal),2):
            if i+1==len(equal): nxt.append(equal[i])
            else:
                nxt.append(op.relu(op.sub(op.add(equal[i],equal[i+1]),1.0)))
                and_nodes+=1
        equal=nxt; depth+=1
    result=op.sub(op.mul(120.0,equal[0]),60.0)
    d=len(q)
    assert op.count==9*d-1 and and_nodes==d-1
    assert depth==(d-1).bit_length()
    return result,{'primitive_calls':op.count,'AND_nodes':and_nodes,'AND_depth':depth,'coordinate_XNORs':d}


def bits_of(index,d):
    return tuple((index>>shift)&1 for shift in range(d-1,-1,-1))


def tree_sum(values):
    if len(values)==1: return values[0]
    p=1<<((len(values)-1).bit_length()-1)
    return f32(tree_sum(values[:p])+tree_sum(values[p:]))


def reference_retrieve(values,query,d,mode):
    assert len(values)==1<<d and all(bit in (0,1) for bit in values)
    q=bits_of(query,d)
    scores=[neural_score(q,bits_of(i,d))[0] for i in range(1<<d)]
    maximum=max(scores)
    weights=[f32(math.exp(f32(s-maximum))) for s in scores]
    if mode=='left':
        denominator=0.0
        for w in weights: denominator=f32(denominator+w)
    else: denominator=tree_sum([0.0]+weights)
    normalized=[f32(w/denominator) for w in weights]
    terms=[f32(p*f32(v)) for p,v in zip(normalized,values)]
    if mode=='left':
        output=0.0
        for term in terms: output=f32(output+term)
    else: output=tree_sum([0.0]+terms)
    assert maximum==60.0 and denominator==1.0
    assert sum(w!=0 for w in weights)==1 and weights[query]==1.0
    assert all(w in (0.0,1.0) for w in normalized)
    assert struct.pack('!f',output)==struct.pack('!f',float(values[query]))
    return output


def run(path):
    started=time.perf_counter()
    exp_zero=f32(math.exp(0.0)); exp_negative=f32(math.exp(-120.0))
    assert exp_zero==1.0 and struct.pack('!f',exp_negative).hex()=='00000000'
    equality=[]; digest=hashlib.sha256()
    for d in range(1,7):
        cases=0; shape=None
        for q in itertools.product((0,1),repeat=d):
            for k in itertools.product((0,1),repeat=d):
                score,shape=neural_score(q,k)
                assert score==(60.0 if q==k else -60.0)
                digest.update(struct.pack('!f',score)); cases+=1
        equality.append({'d':d,'all_query_key_pairs':cases,'shape':shape,'passed':True})
    exhaustive=[]
    for d in (1,2,3):
        m=1<<d; cases=0
        for values in itertools.product((0,1),repeat=m):
            for query in range(m):
                for mode in ('left','B-tree'):
                    output=reference_retrieve(values,query,d,mode)
                    digest.update(struct.pack('!f',output)); cases+=1
        exhaustive.append({'d':d,'history_length':m,'all_value_strings':1<<m,
                           'query_layout_comparisons':cases,'layouts':['left','B-tree'],'passed':True})
    rng=random.Random(2026110506); random_cases=[]
    for d in (4,6,8):
        m=1<<d; cases=0
        for _ in range(8):
            values=tuple(rng.randrange(2) for _ in range(m))
            for query in rng.sample(range(m),min(8,m)):
                for mode in ('left','B-tree'):
                    output=reference_retrieve(values,query,d,mode)
                    digest.update(struct.pack('!f',output)); cases+=1
        random_cases.append({'d':d,'history_length':m,'random_value_strings':8,
                             'query_layout_comparisons':cases,'passed':True})
    report={'passed':True,'scope':'compact ReLU comparator score, specified canonical binary32; not stock bilinear score or trained LLM',
            'exp_points':{'exp32_0':exp_zero,'exp32_minus120':exp_negative,
                          'minus120_output_hex':struct.pack('!f',exp_negative).hex(),
                          'implementation':'host binary64 exp then struct binary32; general theorem states required exp property'},
            'equality_truth_tables':equality,'exhaustive_retrieval':exhaustive,
            'random_retrieval':random_cases,'output_digest':digest.hexdigest(),
            'seconds':time.perf_counter()-started,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'not_claimed':['a small-space compiler','proof of lower bound by finite tests','all hardware exp','actual 200B/human coverage','standard P vs NP result'],
            'model_note':'Sparse circuit has linear gates; dense parameter expansion remains polynomial. Reference retains full KV; query is late, and expected x_i is used only by the test observer.'}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'equality_pairs':sum(x['all_query_key_pairs'] for x in equality),
                      'exhaustive_retrieval_layout_comparisons':sum(x['query_layout_comparisons'] for x in exhaustive),
                      'random_retrieval_layout_comparisons':sum(x['query_layout_comparisons'] for x in random_cases),
                      'seconds':report['seconds'],'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=Path(__file__).resolve().parents[1]/'reports/retrieval-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
