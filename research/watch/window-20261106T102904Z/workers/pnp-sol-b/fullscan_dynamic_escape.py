"""B58 finite semantic accounting: direct-address collision + dynamic updates."""
from dataclasses import dataclass
import unittest

@dataclass
class Ledger:
    reads:int=0; writes:int=0; updates:int=0; queries:int=0

def sum_full(x,L):
    total=0
    for v in x: L.reads+=1; total+=v
    return total

def collision_direct(x,sigma,L):
    counts=[0]*sigma; L.writes+=sigma # charged clear/init
    for v in x:
        if not 0<=v<sigma: raise ValueError('domain')
        L.reads+=1
        if counts[v]: return True
        counts[v]=1; L.writes+=1
    return False

class DynamicDirect:
    def __init__(self,x,sigma):
        self.raw=list(x); self.sigma=sigma; self.count=[0]*sigma
        self.L=Ledger(reads=len(x),writes=sigma+len(x))
        for v in x:
            if not 0<=v<sigma: raise ValueError('domain')
            self.count[v]+=1
    def collision(self):
        self.L.queries+=1
        return any(c>1 for c in self.count)
    def update(self,i,v):
        if not 0<=i<len(self.raw) or not 0<=v<self.sigma: raise ValueError('update')
        old=self.raw[i]; self.count[old]-=1; self.count[v]+=1; self.raw[i]=v
        self.L.reads+=1; self.L.writes+=2; self.L.updates+=1

class EscapeTests(unittest.TestCase):
    def test_sum_and_collision_same_fullscan_envelope(self):
        x=[0,2,1,3,2]; L=Ledger()
        self.assertEqual(sum_full(x,L),8)
        self.assertTrue(collision_direct(x,4,L))
        self.assertEqual(L.reads,len(x)*2)
    def test_domain_capacity_threshold(self):
        # M=sigma words is the exact direct-address capacity, not M=sqrt(n).
        self.assertTrue(collision_direct([0,3,1,3],4,Ledger()))
        with self.assertRaises(ValueError): collision_direct([0,4],4,Ledger())
    def test_dynamic_update(self):
        d=DynamicDirect([0,1,2,3],4)
        self.assertFalse(d.collision()); d.update(3,2)
        self.assertTrue(d.collision()); d.update(2,0)
        self.assertTrue(d.collision()); self.assertEqual(d.L.updates,2)
    def test_fns_profile_not_escaped(self):
        n=128; sigma=n*n; M=n
        self.assertGreater(sigma,M)
        # This does not prove no other algorithm works; only direct-address route unavailable.
        self.assertFalse(M>=sigma)

if __name__=='__main__': unittest.main(verbosity=2)
