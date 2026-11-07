"""B54 finite sanity and adaptive-memorization negative control."""
import math
import itertools
import unittest

def prior_radius(n, alpha, length_bits):
    if n<=0 or not 0<alpha<1 or length_bits<0:
        raise ValueError('invalid inputs')
    return math.sqrt((length_bits*math.log(2)+math.log(1/alpha))/(2*n))

class SelectionTests(unittest.TestCase):
    def test_adaptive_memorization(self):
        universe=10000
        sample=[2,7,7,19,100,887,2,42]
        seen=set(sample)
        # Target is zero. Policy emits zero only on previously seen tasks.
        policy=lambda x:0 if x in seen else 1
        self.assertEqual(sum(policy(x)==0 for x in sample)/len(sample),1)
        self.assertLessEqual(sum(policy(x)==0 for x in range(universe))/universe,len(sample)/universe)
    def test_prior_penalty(self):
        self.assertGreater(prior_radius(100,.05,10000),1)
        self.assertLess(prior_radius(10000,.05,10),.03)
    def test_uniform_bound_exact_finite(self):
        # Universe 2, all 4 deterministic indicator functions; n=8 iid draws.
        n=8; alpha=.2; K=4
        radius=math.sqrt(math.log(K/alpha)/(2*n))
        policies=list(itertools.product((0,1),repeat=2))
        bad=0
        for sample in itertools.product((0,1),repeat=n):
            if any(sum(p[x] for x in sample)/n-sum(p)/2>radius for p in policies):
                bad+=1
        self.assertLessEqual(bad/(2**n),alpha)
    def test_nonprefix_fixed_width_prior(self):
        # N-bit truth tables all have same fixed width: Kraft mass exactly 1.
        N=6
        self.assertEqual(sum(2**(-N) for _ in range(2**N)),1)

if __name__=='__main__':
    unittest.main(verbosity=2)
