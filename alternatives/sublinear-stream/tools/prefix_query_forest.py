#!/usr/bin/env python3
"""Finite sanity checks for an explicit prefix-compatible reduction tree.

Reuses the frozen hour2 toy primitives. Not arbitrary balanced/GPU reduction.
The reference/test harness stores histories; TreeCache itself does not.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import struct
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('tiny_words',HERE/'tiny_query_summary.py')
t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)


def reference_tree(values,operation):
    assert values
    if len(values)==1: return values[0]
    # Largest power of two STRICTLY smaller than this length.
    p=1<<((len(values)-1).bit_length()-1)
    return operation(reference_tree(values[:p],operation),reference_tree(values[p:],operation))


def trailing_ones(count):
    out=0
    while count&1:
        out+=1; count>>=1
    return out


def append_levels(levels,leaf,operation,carry):
    value=leaf; merges=0
    for height in range(carry):
        assert levels[height] is not None
        value=operation(levels[height],value)  # old/left BEFORE new/right
        levels[height]=None; merges+=1
    while len(levels)<=carry: levels.append(None)
    assert levels[carry] is None
    levels[carry]=value
    return merges


def root_levels(levels,count,operation):
    result=None
    # Read suffix/small blocks first, forming RIGHT-nested combination.
    for height in range(len(levels)):
        if (count>>height)&1:
            value=levels[height]; assert value is not None
            result=value if result is None else operation(value,result)
    assert result is not None
    return result


class Forest:
    def __init__(self,operation,seed):
        self.operation=operation; self.levels=[seed]; self.count=1; self.merges=0
    def clone(self):
        other=object.__new__(Forest)
        other.operation=self.operation; other.levels=self.levels.copy()
        other.count=self.count; other.merges=self.merges
        return other
    def append(self,value):
        self.merges+=append_levels(self.levels,value,self.operation,trailing_ones(self.count))
        self.count+=1
    def query(self):
        return root_levels(self.levels,self.count,self.operation)


class TreeCache:
    def __init__(self):
        self.count=1  # genuine seed leaf in EVERY parameter forest
        self.merges=0
        self.maxima=[[t.LOW] for q in t.QUERIES]
        self.den=[[[t.ZERO] for m in t.WORDS] for q in t.QUERIES]
        self.out=[[[[t.ZERO] for z in t.WORDS] for m in t.WORDS] for q in t.QUERIES]
    def clone(self):
        other=object.__new__(TreeCache)
        other.count=self.count; other.merges=self.merges
        other.maxima=[a.copy() for a in self.maxima]
        other.den=[[a.copy() for a in row] for row in self.den]
        other.out=[[[a.copy() for a in row] for row in plane] for plane in self.out]
        return other
    def arrays(self):
        yield from self.maxima
        for row in self.den: yield from row
        for plane in self.out:
            for row in plane: yield from row
    def parameters(self):
        return len(t.QUERIES)*(1+len(t.WORDS)+len(t.WORDS)**2)
    def append(self,k,v):
        carry=trailing_ones(self.count)
        for qi,q in enumerate(t.QUERIES):
            score=t.mul(q,k)
            self.merges+=append_levels(self.maxima[qi],score,t.maximum,carry)
            for mi,m in enumerate(t.WORDS):
                u=t.exponential(t.sub(score,m))
                self.merges+=append_levels(self.den[qi][mi],u,t.add,carry)
                for zi,z in enumerate(t.WORDS):
                    leaf=t.mul(t.div(u,z),v)
                    self.merges+=append_levels(self.out[qi][mi][zi],leaf,t.add,carry)
        self.count+=1
    def query(self,q):
        qi=t.QINDEX[q]
        m=root_levels(self.maxima[qi],self.count,t.maximum); mi=t.INDEX[m]
        z=root_levels(self.den[qi][mi],self.count,t.add); zi=t.INDEX[z]
        return root_levels(self.out[qi][mi][zi],self.count,t.add)
    def shape(self):
        allocated=sum(len(a) for a in self.arrays())
        live=sum(value is not None for a in self.arrays() for value in a)
        return {'seed_inclusive_count':self.count,'level_span':self.count.bit_length(),
                'active_blocks':self.count.bit_count(),'allocated_word_slots':allocated,
                'live_numeric_words':live,'merges':self.merges}


def literal_kernel(history,q):
    scores=[t.mul(q,k) for k,v in history]
    m=reference_tree([t.LOW]+scores,t.maximum)
    weights=[t.exponential(t.sub(score,m)) for score in scores]
    z=reference_tree([t.ZERO]+weights,t.add)
    terms=[t.mul(t.div(u,z),v) for u,(k,v) in zip(weights,history)]
    return reference_tree([t.ZERO]+terms,t.add)


def generic_campaign(operation,seed):
    prefixes=0; digest=hashlib.sha256(); max_span=0; max_blocks=0
    def visit(forest,history):
        nonlocal prefixes,max_span,max_blocks
        got=forest.query(); want=reference_tree([seed]+history,operation)
        assert got==want,{'history':history,'seed':seed,'got':got,'want':want}
        assert forest.count==len(history)+1
        assert len(forest.levels)==forest.count.bit_length()
        assert sum(v is not None for v in forest.levels)==forest.count.bit_count()
        assert forest.merges==forest.count-forest.count.bit_count()
        prefixes+=1; max_span=max(max_span,len(forest.levels)); max_blocks=max(max_blocks,forest.count.bit_count())
        digest.update(bytes([t.INDEX[got]]))
        if len(history)<4:
            for value in t.WORDS:
                nxt=forest.clone(); nxt.append(value); visit(nxt,history+[value])
    visit(Forest(operation,seed),[])
    return {'prefix_cases':prefixes,'alphabet_size':len(t.WORDS),'max_append_length':4,
            'max_allocated_level_span':max_span,'max_active_blocks':max_blocks,
            'output_digest':digest.hexdigest(),'passed':True}


def kernel_campaign(name,alphabet,depth):
    prefixes=0; comparisons=0; digest=hashlib.sha256(); max_span=0; max_blocks=0
    def visit(cache,history):
        nonlocal prefixes,comparisons,max_span,max_blocks
        shape=cache.shape(); count=len(history)+1; params=cache.parameters()
        assert cache.count==count
        assert shape['allocated_word_slots']==params*count.bit_length()
        assert shape['live_numeric_words']==params*count.bit_count()
        assert cache.merges==params*(count-count.bit_count())
        prefixes+=1; max_span=max(max_span,shape['level_span']); max_blocks=max(max_blocks,shape['active_blocks'])
        for qi,q in enumerate(t.QUERIES):
            got=cache.query(q); want=literal_kernel(history,q)
            assert got==want,{'history':history,'q':q,'cache':got,'reference':want}
            assert got!=t.ERR
            digest.update(bytes([qi,t.INDEX[got]])); comparisons+=1
        if len(history)<depth:
            for record in alphabet:
                nxt=cache.clone(); nxt.append(*record); visit(nxt,history+[record])
    visit(TreeCache(),[])
    return {'name':name,'alphabet_size':len(alphabet),'max_append_length':depth,
            'prefix_cases':prefixes,'query_comparisons':comparisons,
            'max_allocated_level_span':max_span,'max_active_blocks':max_blocks,
            'output_digest':digest.hexdigest(),'passed':True}


def run(path):
    started=time.perf_counter()
    generic={name:generic_campaign(op,seed) for name,op,seed in
             [('saturating_add',t.add,0),('saturating_sub',t.sub,0),('max_with_error',t.maximum,t.LOW)]}
    campaigns=[kernel_campaign('full KV grid through length 2',list(itertools.product(t.F,t.F)),2),
               kernel_campaign('4 extreme records through length 5',list(itertools.product((-2,2),(-4,4))),5)]
    cache=TreeCache(); history=[]; rng=random.Random(2026110503)
    alphabet=list(itertools.product(t.F,t.F)); comparisons=0; max_span=0; max_blocks=0
    for _ in range(512):
        record=rng.choice(alphabet); history.append(record); cache.append(*record)
        shape=cache.shape(); params=cache.parameters()
        assert shape['allocated_word_slots']==params*cache.count.bit_length()
        assert shape['live_numeric_words']==params*cache.count.bit_count()
        assert cache.merges==params*(cache.count-cache.count.bit_count())
        max_span=max(max_span,shape['level_span']); max_blocks=max(max_blocks,shape['active_blocks'])
        for q in t.QUERIES:
            assert cache.query(q)==literal_kernel(history,q); comparisons+=1
    long_stream={'length':512,'query_comparisons':comparisons,'final_shape':cache.shape(),
                 'max_allocated_level_span':max_span,'max_active_blocks':max_blocks,'passed':True}
    # The seed is a real leaf: rebuilding a shorter tree can change brackets
    # even when zero is a strict two-sided identity for this toy addition.
    with_seed=reference_tree([0,4,4,-4],t.add)
    without_seed=reference_tree([4,4,-4],t.add)
    assert with_seed!=without_seed
    history_control=[(-2,4)]*4+[(-2,-4)]
    tree_value=literal_kernel(history_control,0); left_value=t.literal(history_control,0)
    assert tree_value!=left_value
    # Primitive-level padding counterexample, not a claim about all full rows.
    def add32(a,b): return struct.unpack('!f',struct.pack('!f',a+b))[0]
    no_pad=struct.pack('!f',reference_tree([-0.0],add32)).hex()
    pad=struct.pack('!f',reference_tree([-0.0,0.0],add32)).hex()
    assert no_pad!=pad
    controls={'seed_omission_rebalances_nonassociative_tree':{'with_seed_code':with_seed,'without_seed_code':without_seed},
              'left_fold_is_not_this_tree':{'history':history_control,'q':0,'tree_code':tree_value,'left_fold_code':left_value},
              'zero_padding_not_primitive_bit_identity':{'without_padding_hex':no_pad,'with_padding_hex':pad,
                 'scope':'primitive signed-zero example, not a universal full-attention failure'}}
    report={'passed':True,'scope':'specific B-tree, toy finite word kernel; not arbitrary GPU reduction',
            'reference_tree':'seed is leaf0; split by largest power of two strictly less than length; combine old-left/new-right',
            'generic_forests':generic,'kernel_campaigns':campaigns,'long_stream':long_stream,
            'negative_controls':controls,'parameter_forests':cache.parameters(),
            'seconds':time.perf_counter()-started,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'toy_primitives_sha256':hashlib.sha256((HERE/'tiny_query_summary.py').read_bytes()).hexdigest(),
            'harness_note':'Reference/DFS hold histories and clones. TreeCache stores only level arrays and shared count. Word-slot counts are not process RSS.',
            'not_claimed':['all GPU balanced trees','actual IEEE32/GPU/200B model equivalence','polynomial model-size constants','full API or multi-layer coverage']}
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'generic_prefix_comparisons':sum(x['prefix_cases'] for x in generic.values()),
                      'kernel_query_comparisons':sum(x['query_comparisons'] for x in campaigns)+comparisons,
                      'parameter_forests':cache.parameters(),'final_level_span':cache.count.bit_length(),
                      'report':str(path)},ensure_ascii=False))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=HERE.parent/'reports/prefix-forest-tests-v1.json')
    raise SystemExit(run(parser.parse_args().report))
