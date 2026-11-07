"""B57 finite Shannon-capacity sanity checks, not a physical benchmark."""
import math
import unittest
from fractions import Fraction

def h2(p):
    if not 0<=p<=1: raise ValueError('invalid probability')
    return 0.0 if p in (0,1) else -p*math.log2(p)-(1-p)*math.log2(1-p)

def entropy(counts):
    total=sum(counts)
    return 0.0 if not total else sum(-(n/total)*math.log2(n/total) for n in counts if n)

def code_stats(N,table):
    # Uniform X, deterministic one-bit message. MAP bit decoders are optimal.
    size=1<<N; post=[[[] for _ in range(2)] for _ in range(N)]
    groups=[[x for x in range(size) if table[x]==m] for m in (0,1)]
    errors=[]; cond=[]
    for j in range(N):
        mistakes=0; hc=0.0
        for group in groups:
            ones=sum((x>>j)&1 for x in group); zero=len(group)-ones
            mistakes+=min(ones,zero)
            if group: hc+=len(group)/size*entropy([ones,zero])
        errors.append(Fraction(mistakes,size)); cond.append(hc)
    return entropy([len(g) for g in groups]),errors,cond

class CapacityTests(unittest.TestCase):
    def test_entropy_endpoints_and_error_units(self):
        self.assertEqual(h2(0),0); self.assertEqual(h2(.5),1)
        self.assertAlmostEqual(1-h2(1/3),.08170416594551044)
        self.assertAlmostEqual(1-h2(.1),.5310044064107188)
    def test_all_one_bit_encoders_on_three_bits(self):
        N=3
        for packed in range(1<<(1<<N)):
            table=[(packed>>x)&1 for x in range(1<<N)]
            hm,errs,hconds=code_stats(N,table)
            self.assertLessEqual(sum(1-h for h in hconds),hm+1e-12)
            self.assertLessEqual(sum(1-h2(float(e)) for e in errs),hm+1e-12)
            self.assertLessEqual(N*(1-h2(float(max(errs)))),1+1e-12)
    def test_zero_error_requires_all_bits(self):
        for N in range(1,10): self.assertEqual(N*(1-h2(0)),N)
    def test_public_random_coordinate_code(self):
        # R chooses one coordinate uniformly; message is X_R.
        # Any requested coordinate has average MAP error (N-1)/(2N).
        N=3
        eps=Fraction(N-1,2*N)
        errors=[]
        for j in range(N):
            e=Fraction(0)
            for r in range(N):
                table=[(x>>r)&1 for x in range(1<<N)]
                _,err,_=code_stats(N,table)
                e+=err[j]/N
            errors.append(e)
        self.assertEqual(errors,[eps]*N)
        self.assertLessEqual(N*(1-h2(float(eps))),1)

if __name__=='__main__': unittest.main(verbosity=2)
