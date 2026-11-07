"""B56 research-only dynamic OR: explicit bit cells and lifecycle counters.
No physical RAM/time claim; Python execution is a semantic reference.
"""
from dataclasses import dataclass, field
from itertools import combinations, product
from math import comb
import json
import unittest

@dataclass
class Ledger:
    input_reads:int=0
    raw_reads:int=0
    raw_writes:int=0
    counter_reads:int=0
    counter_writes:int=0
    queries:int=0
    updates:int=0
    rejected_updates:int=0

class PackedBits:
    def __init__(self,n): self.n=n; self.data=bytearray((n+7)//8)
    def read(self,i): return (self.data[i//8]>>(i%8))&1
    def write(self,i,b):
        mask=1<<(i%8)
        if b: self.data[i//8]|=mask
        else: self.data[i//8]&=~mask

class DynamicOR:
    def __init__(self,bits):
        self.n=len(bits)
        if self.n<1: raise ValueError('invalid dataset')
        self.ledger=Ledger()
        self.raw=PackedBits(self.n)
        self.width=self.n.bit_length() # ceil(log2(N+1)), includes the all-ones count N
        self.count=PackedBits(self.width)
        self.version=0
        self.ledger.counter_writes+=self.width # initialization is not free
        self.ledger.raw_writes+=self.n # charge logical zero-initialization too
        for i,b in enumerate(bits):
            self.ledger.input_reads+=1
            if b not in (0,1): raise ValueError('invalid dataset bit')
            self.raw.write(i,b); self.ledger.raw_writes+=1
            if b: self._change_count(1)
    def _change_count(self,delta):
        for j in range(self.width):
            old=self.count.read(j); self.ledger.counter_reads+=1
            self.count.write(j,1-old); self.ledger.counter_writes+=1
            if (delta==1 and old==0) or (delta==-1 and old==1): return
        raise AssertionError('counter overflow/underflow')
    def query(self):
        self.ledger.queries+=1
        answer=0
        for j in range(self.width):
            answer|=self.count.read(j); self.ledger.counter_reads+=1
        return bool(answer)
    def update(self,i,new,expected_version):
        if not 0<=i<self.n or new not in (0,1) or expected_version!=self.version:
            self.ledger.rejected_updates+=1
            raise ValueError('invalid update or stale version')
        old=self.raw.read(i); self.ledger.raw_reads+=1
        if new!=old: self._change_count(1 if new else -1)
        self.raw.write(i,new); self.ledger.raw_writes+=1
        self.version+=1; self.ledger.updates+=1
    def decoded_count(self):
        # Diagnostic, NOT a charged Query operation or a production escape hatch.
        return sum(self.count.read(i)<<i for i in range(self.width))
    def packed_payload_bytes(self): return len(self.raw.data)+len(self.count.data)

@dataclass(frozen=True)
class BoundedSummary:
    n:int
    remaining:int
    support:frozenset=field(default_factory=frozenset)
    always_one:bool=False
    @staticmethod
    def build(bits,U):
        if not 0<=U<len(bits): raise ValueError('U must be below N')
        S=frozenset(i for i,b in enumerate(bits) if b)
        return BoundedSummary(len(bits),U,frozenset() if len(S)>U else S,len(S)>U)
    def query(self): return self.always_one or bool(self.support)
    def update(self,i,b):
        if self.remaining==0 or not 0<=i<self.n or b not in (0,1): raise ValueError('outside contract')
        if self.always_one: return BoundedSummary(self.n,self.remaining-1,frozenset(),True)
        S=(self.support|{i}) if b else (self.support-{i})
        r=self.remaining-1
        return BoundedSummary(self.n,r,frozenset() if len(S)>r else frozenset(S),len(S)>r)

def class_count(N,U): return sum(comb(N,k) for k in range(U+1))+1

def reset_signature(mask,N,U):
    vals=[]
    for k in range(U+1):
        for R in combinations(range(N),k):
            clear=sum(1<<j for j in R)
            vals.append(bool(mask&~clear))
    return tuple(vals)

class DynamicTests(unittest.TestCase):
    def test_exact_initial_equivalence_classes(self):
        for N in range(1,8):
            for U in range(N):
                signatures={reset_signature(x,N,U) for x in range(1<<N)}
                self.assertEqual(len(signatures),class_count(N,U))
    def test_bounded_summary_all_short_histories(self):
        N=4
        for U in range(N):
            for x in range(1<<N):
                bits=[(x>>i)&1 for i in range(N)]
                def walk(s,raw,r):
                    self.assertEqual(s.query(),any(raw))
                    if not r: return
                    for i,b in product(range(N),(0,1)):
                        new=raw.copy(); new[i]=b
                        walk(s.update(i,b),new,r-1)
                walk(BoundedSummary.build(bits,U),bits,U)
    def test_raw_plus_counter_all_transitions(self):
        for N in range(1,8):
            for x in range(1<<N):
                initial=[(x>>i)&1 for i in range(N)]
                for i,b in product(range(N),(0,1)):
                    a=DynamicOR(initial); raw=initial.copy(); raw[i]=b
                    a.update(i,b,0)
                    self.assertEqual(a.query(),any(raw))
                    self.assertEqual(a.decoded_count(),sum(raw))
    def test_full_ones_counter_width(self):
        a=DynamicOR([1]*16)
        self.assertEqual(a.width,5) # log2 N bits alone would overflow at count N
        self.assertEqual(a.decoded_count(),16)
        for j in range(16): a.update(j,0,j)
        self.assertFalse(a.query())
    def test_boolean_summary_failure(self):
        x=[1,0]; y=[1,1]
        self.assertEqual(any(x),any(y))
        x[0]=0; y[0]=0
        self.assertNotEqual(any(x),any(y))
    def test_stale_rejected_before_mutation(self):
        a=DynamicOR([1,0]); a.update(1,1,0)
        before=(bytes(a.raw.data),bytes(a.count.data),a.version)
        with self.assertRaises(ValueError): a.update(0,0,0)
        self.assertEqual(before,(bytes(a.raw.data),bytes(a.count.data),a.version))
    def test_cold_cost_and_retained_data(self):
        a=DynamicOR([1,0]*32)
        self.assertEqual(a.ledger.input_reads,64)
        self.assertEqual(a.ledger.raw_writes,128)
        self.assertEqual(a.packed_payload_bytes(),9)
        self.assertGreaterEqual(a.ledger.counter_writes,a.width)

if __name__=='__main__': unittest.main(verbosity=2)
