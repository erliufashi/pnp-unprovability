"""Finite checks for RETURN-H1. Python standard library only; not empirical coverage."""
import json, math
from functools import lru_cache

def parity(x): return x.bit_count() & 1
@lru_cache(None)
def depth(fiber, mask, n):
    if len({parity(x & mask) for x in fiber}) <= 1: return 0
    return 1 + min(max(depth(tuple(x for x in fiber if (x>>j)&1 == b), mask, n) for b in (0,1)) for j in range(n) if len({(x>>j)&1 for x in fiber}) == 2)
checks=0
for n in range(1,4):
    for bits in range(1,1<<(1<<n)):
        fiber=tuple(x for x in range(1<<n) if (bits>>x)&1)
        q=max(depth(fiber,m,n) for m in range(1<<n))
        assert len(fiber)<=sum(math.comb(n,i) for i in range(q+1))
        checks+=1
# [3,1] repetition-code index: cache total parity; mask or complement has weight <=1.
examples=0
for x in range(8):
    z=parity(x)
    for mask in range(8):
        use_cache=mask.bit_count()>1
        residual=mask ^ (7 if use_cache else 0)
        assert residual.bit_count()<=1
        result=(z if use_cache else 0)^parity(x&residual)
        assert result==parity(x&mask)
        examples+=1
print(json.dumps({'fiber_checks':checks,'tight_N3_s1_q1_cases':examples,'status':'passed'},indent=2))
