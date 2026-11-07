"""Exact finite checks of amplification and a sampled-key collision scheme.
Not an ED solver or a general randomized lower-bound experiment.
"""
from fractions import Fraction
from itertools import combinations
from math import comb, log, log2
import json

checks = 0
rows = []
for r in range(1, 42, 2):
    p = Fraction(1, 3)
    majority_error = sum((Fraction(comb(r,j))*p**j*(1-p)**(r-j)
                          for j in range((r+1)//2, r+1)), Fraction())
    assert majority_error >= p**r
    # Illustrative admissible-shaped threshold gamma=1, original T/n=32.
    # Does not supply the unknown constant of BSSV Theorem 6.23.
    neg_log_threshold = (32*r)**2 * log(32*r)
    assert r*log(3) < neg_log_threshold
    rows.append({'repeats': r, 'majority_error': float(majority_error),
                 'neg_log_threshold_gamma1': neg_log_threshold,
                 'neg_log_all_wrong': r*log(3)})
    checks += 2
sample_checks = 0
for n in range(2, 13):
    for m in range(1,n+1):
        subsets = list(combinations(range(n),m))
        hits = sum(0 in s or 1 in s for s in subsets)
        p = Fraction(hits,len(subsets))
        exact = 1-Fraction(comb(n-2,m) if m <= n-2 else 0,comb(n,m))
        formula = Fraction(m*(2*n-m-1),n*(n-1))
        assert p == exact == formula
        assert p <= Fraction(2*m,n)
        sample_checks += 2
# First theorem's error profile depends on time ratio a, not n by itself.
a = 32
assert a*a*log(a) == 1024*log(32)
checks += 1
print(json.dumps({'status':'pass','amplification_checks':checks,
                  'sample_subset_checks':sample_checks,
                  'first_threshold':'a^(-gamma*a^2), a=T/n',
                  'linear_profile_neg_log_threshold_per_gamma':a*a*log(a),
                  'majority_rows':rows,
                  'not_a_BPP_separation_certificate':True},indent=2))
