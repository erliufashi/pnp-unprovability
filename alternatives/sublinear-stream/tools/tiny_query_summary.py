#!/usr/bin/env python3
"""Small finite-domain sanity checks for the all-query left-fold cache.

Not float32, not arbitrary GPUs, and not a proof of the general theorem.
The harness retains histories to compute an independent literal reference;
the Cache algorithm itself stores no history.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

F=tuple(range(-4,5))  # code a denotes the number a/2, clipped to [-2,2].
ERR='ERR'
WORDS=F+(ERR,)
INDEX={value:i for i,value in enumerate(WORDS)}
QUERIES=F
QINDEX={value:i for i,value in enumerate(QUERIES)}
LOW=-4
ZERO=0
EXP={-4:0,-3:0,-2:1,-1:1,0:2,1:3,2:4,3:4,4:4}


def clip(value): return max(-4,min(4,value))


def nearest_even_ratio(numerator,denominator):
    sign=-1 if (numerator<0) != (denominator<0) else 1
    quotient,remainder=divmod(abs(numerator),abs(denominator))
    if 2*remainder>abs(denominator) or (2*remainder==abs(denominator) and quotient%2):
        quotient+=1
    return sign*quotient


def add(a,b):
    return ERR if a==ERR or b==ERR else clip(a+b)


def sub(a,b):
    return ERR if a==ERR or b==ERR else clip(a-b)


def mul(a,b):
    return ERR if a==ERR or b==ERR else clip(nearest_even_ratio(a*b,2))


def div(a,b):
    return ERR if a==ERR or b==ERR or b==0 else clip(nearest_even_ratio(2*a,b))


def maximum(a,b):
    return ERR if a==ERR or b==ERR else max(a,b)


def exponential(a):
    return ERR if a==ERR else EXP[a]


def fold(function,initial,values):
    out=initial
    for value in values: out=function(out,value)
    return out


def literal(history,q):
    # Literal final-max, final-denominator reference, retaining all history.
    scores=[mul(q,k) for k,v in history]
    m=fold(maximum,LOW,scores)
    weights=[exponential(sub(score,m)) for score in scores]
    z=fold(add,ZERO,weights)
    terms=[mul(div(u,z),v) for u,(k,v) in zip(weights,history)]
    return fold(add,ZERO,terms)


class Cache:
    def __init__(self):
        self.maxima=[LOW for q in QUERIES]
        self.den=[[ZERO for m in WORDS] for q in QUERIES]
        self.out=[[[ZERO for z in WORDS] for m in WORDS] for q in QUERIES]

    def clone(self):
        other=object.__new__(Cache)
        other.maxima=self.maxima.copy()
        other.den=[row.copy() for row in self.den]
        other.out=[[row.copy() for row in plane] for plane in self.out]
        return other

    def append(self,k,v):
        for qi,q in enumerate(QUERIES):
            score=mul(q,k)
            self.maxima[qi]=maximum(self.maxima[qi],score)
            for mi,m in enumerate(WORDS):
                u=exponential(sub(score,m))
                self.den[qi][mi]=add(self.den[qi][mi],u)
                # z is a fixed hypothetical FINAL word, NOT the running den.
                for zi,z in enumerate(WORDS):
                    term=mul(div(u,z),v)
                    self.out[qi][mi][zi]=add(self.out[qi][mi][zi],term)

    def query(self,q):
        qi=QINDEX[q]; mi=INDEX[self.maxima[qi]]
        zi=INDEX[self.den[qi][mi]]
        return self.out[qi][mi][zi]

    def cells(self):
        return len(self.maxima)+sum(map(len,self.den))+sum(len(row) for plane in self.out for row in plane)

    def invalid_counterfactual_cells(self):
        return sum(value==ERR for plane in self.out for row in plane for value in row)


def campaign(name,alphabet,depth):
    digest=hashlib.sha256(); prefixes=0; comparisons=0; invalid_prefixes=0
    expected=len(QUERIES)*(1+len(WORDS)+len(WORDS)**2)
    def visit(cache,history):
        nonlocal prefixes,comparisons,invalid_prefixes
        prefixes+=1
        assert cache.cells()==expected
        if cache.invalid_counterfactual_cells(): invalid_prefixes+=1
        for qi,q in enumerate(QUERIES):
            got=cache.query(q); want=literal(history,q)
            assert got==want,{'history':history,'q':q,'cache':got,'reference':want}
            assert got!=ERR  # selected denominators are valid for this dataset.
            digest.update(bytes([qi,INDEX[got]])); comparisons+=1
        if len(history)<depth:
            for record in alphabet:
                successor=cache.clone(); successor.append(*record)
                visit(successor,history+[record])
    visit(Cache(),[])
    assert invalid_prefixes>0
    return {'name':name,'alphabet_size':len(alphabet),'max_history_length':depth,
            'prefix_cases':prefixes,'query_comparisons':comparisons,
            'prefixes_with_isolated_counterfactual_errors':invalid_prefixes,
            'cache_cells':expected,'output_digest':digest.hexdigest(),'passed':True}


def naive_running_normalizers(history,q):
    m=LOW; z=ZERO; out=ZERO
    for k,v in history:
        score=mul(q,k); m=maximum(m,score)
        u=exponential(sub(score,m)); z=add(z,u)
        out=add(out,mul(div(u,z),v))
    return out


def run(path):
    started=time.perf_counter()
    full=list(itertools.product(F,F))
    endpoint=list(itertools.product((-2,2),(-4,4)))
    campaigns=[campaign('full KV grid, all prefixes through length 2',full,2),
               campaign('4 extreme records, all prefixes through length 5',endpoint,5)]
    rng=random.Random(20261105); history=[]; cache=Cache(); comparisons=0
    expected=cache.cells(); digest=hashlib.sha256()
    for _ in range(512):
        record=rng.choice(full); history.append(record); cache.append(*record)
        assert cache.cells()==expected
        for qi,q in enumerate(QUERIES):
            got=cache.query(q); want=literal(history,q); assert got==want
            digest.update(bytes([qi,INDEX[got]])); comparisons+=1
    long_stream={'length':512,'all_prefix_query_comparisons':comparisons,
                 'cache_cells_initial_and_final':expected,'output_digest':digest.hexdigest(),'passed':True}
    # Two invalid simplifications are deliberately made to fail.
    history_a=[(-2,4),(-2,4),(-2,4),(-2,-4)]
    history_b=[(-2,-4),(-2,4),(-2,4),(-2,4)]
    assert Counter(history_a)==Counter(history_b)
    a=literal(history_a,0); b=literal(history_b,0); assert a!=b
    history_c=[(-2,-4),(-2,4)]
    correct=literal(history_c,0); online=naive_running_normalizers(history_c,0); assert correct!=online
    controls={'histogram_forgets_nonassociative_order':{'same_record_multiset':True,
               'history_a':history_a,'history_b':history_b,'output_a_code':a,'output_b_code':b},
              'running_denominator_is_not_final_denominator':{'history':history_c,
               'correct_code':correct,'naive_online_code':online}}
    report={'passed':True,'scope':'finite toy word domain, NOT IEEE32/real LLM',
            'domain':{'numeric_codes':list(F),'code_meaning':'a/2','error_word':ERR,
                      'number_queries':len(QUERIES),'number_words':len(WORDS),
                      'number_cache_words':expected,'raw_word_encoding_bits':4},
            'campaigns':campaigns,'long_stream':long_stream,'negative_controls':controls,
            'seconds':time.perf_counter()-started,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'harness_note':'Literal reference/DFS retain histories and clones for testing; Cache itself stores no input history. Constant table is exponential in general model word width/dimension.'}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'campaign_prefix_cases':[x['prefix_cases'] for x in campaigns],
                      'comparisons':sum(x['query_comparisons'] for x in campaigns)+comparisons,
                      'cache_words':expected,'seconds':report['seconds'],'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=Path(__file__).resolve().parents[1]/'reports/tiny-domain-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
