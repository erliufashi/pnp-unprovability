"""E48 research calculation, standard library only. Not a deployed benchmark."""
import math

def hoeffding_lower(successes, n, alpha):
    if n <= 0:
        return 0.0
    if not (0 <= successes <= n and 0 < alpha < 1):
        raise ValueError('invalid count or alpha')
    return max(0.0, successes/n-math.sqrt(math.log(1/alpha)/(2*n)))

def robust_weighted_lower(lowers, weight_lower, weight_upper):
    """Min dot(w, lowers), sum w=1, box constraints; unknown strata get lower=0."""
    if not (len(lowers)==len(weight_lower)==len(weight_upper)):
        raise ValueError('dimension mismatch')
    if any(not 0 <= x <= 1 for x in lowers):
        raise ValueError('invalid lower')
    if any(not 0 <= a <= b <= 1 for a,b in zip(weight_lower,weight_upper)):
        raise ValueError('invalid interval')
    if sum(weight_lower)>1+1e-12 or sum(weight_upper)<1-1e-12:
        raise ValueError('infeasible weights')
    w=list(weight_lower)
    residual=1-sum(w)
    for i in sorted(range(len(lowers)), key=lambda i:lowers[i]):
        d=min(residual,weight_upper[i]-w[i])
        w[i]+=d
        residual-=d
    if residual>1e-10:
        raise ValueError('infeasible residual')
    return sum(a*b for a,b in zip(w,lowers)),w

def transferred_coverage(conditional_lower, unknown_mass_upper, conditional_tv):
    if not all(0<=x<=1 for x in [conditional_lower,unknown_mass_upper,conditional_tv]):
        raise ValueError('invalid probability')
    return (1-unknown_mass_upper)*max(0.0,conditional_lower-conditional_tv)

if __name__=='__main__':
    import unittest
    class BoundsTest(unittest.TestCase):
        def test_no_data(self):
            self.assertEqual(hoeffding_lower(0,0,.01),0)
        def test_unknown(self):
            self.assertEqual(transferred_coverage(.99,1,0),0)
        def test_example(self):
            value,w=robust_weighted_lower([.9,.7,0],[.3,.2,0],[.7,.5,.2])
            self.assertAlmostEqual(value,.62)
            self.assertEqual([round(x,8) for x in w],[.3,.5,.2])
        def test_enumerated_vertices(self):
            # Exact 0.1-grid candidates include optimum for these aligned boxes.
            import itertools
            for ls in ([.8,.2,0],[0,.2,.8],[.5,.5,.5],[1,0,1]):
                got,_=robust_weighted_lower(ls,[.1,.2,0],[.6,.7,.5])
                vals=[]
                for ints in itertools.product(range(11),repeat=3):
                    if sum(ints)!=10: continue
                    w=[i/10 for i in ints]
                    if all(a-1e-12<=x<=b+1e-12 for a,x,b in zip([.1,.2,0],w,[.6,.7,.5])):
                        vals.append(sum(a*b for a,b in zip(ls,w)))
                self.assertAlmostEqual(got,min(vals))
        def test_transfer(self):
            self.assertAlmostEqual(transferred_coverage(.9,.1,.05),.765)
        def test_infeasible(self):
            with self.assertRaises(ValueError):
                robust_weighted_lower([1,0],[.8,.8],[1,1])
        def test_sample_requirement(self):
            n=math.ceil(math.log(10/.025)/(2*.05**2))
            self.assertEqual(n,1199)
            self.assertGreaterEqual(hoeffding_lower(n,n,.025/10),.95)
    unittest.main(verbosity=2)
