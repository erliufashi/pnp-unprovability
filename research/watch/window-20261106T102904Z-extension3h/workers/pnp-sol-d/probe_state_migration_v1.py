#!/usr/bin/env python3
from functools import lru_cache
from itertools import combinations
import json

def f(k,l): return 1+sum(min(l,2**j) for j in range(k))
# Full exact optimization permits arbitrary extra binary observations
# interleaved with restricted batch-membership replies.
def opt(n,k,l,h):
 @lru_cache(None)
 def solve(mask,k,h):
  ids=[i for i in range(n) if mask>>i&1]
  if not ids: return 0
  best=1
  for z in range(1,len(ids)):
   for subset in combinations(ids,z):
    a=sum(1<<i for i in subset); b=mask^a
    if h: best=max(best,solve(a,k,h-1)+solve(b,k,h-1))
    if k and z<=l: best=max(best,solve(a,k-1,h)+solve(b,k-1,h))
  return best
 return solve((1<<n)-1,k,h)
checks=0
for n in range(1,9):
 for k in range(4):
  for l in range(4):
   for h in range(3):
    assert opt(n,k,l,h)==min(n,(2**h)*f(k,l)),(n,k,l,h)
    checks+=1
# 1 writable environment bit, repeatedly overwritten and explicitly read.
# Raw hidden input is not counted as that 1-bit work cell.
negative=0
for m in range(1,11):
 for x in range(1<<m):
  recovered=0
  for i in range(m):
   env_bit=(x>>i)&1
   # API read is an additional input-dependent bit transfer, NOT membership.
   recovered |= env_bit<<i
  assert recovered==x
  negative+=1
# A concrete fixed-width wire ABI and retained remote request log.
ledger_cases=0
for m in range(1,9):
 for k in range(1,5):
  for l in range(1,5):
   log=[]; writes=reads=0
   for turn in range(k):
    batch=[(turn+j)%(1<<m) for j in range(l)]
    wire=''.join(format(x,'0%db'%m) for x in batch)
    writes+=len(wire)
    parsed=[int(wire[j:j+m],2) for j in range(0,len(wire),m)]
    reads+=len(wire)
    assert parsed==batch
    log.append(wire)
   assert writes==reads==k*l*m
   assert sum(map(len,log))==k*l*m
   ledger_cases+=1
print(json.dumps({'ok':True,'interleaved_optimal_tree_cases':checks,'fixed_width_ledger_cases':ledger_cases,
 'one_bit_environment_full_recoveries':negative,
 'negative_control':'q=1 work cell, m additional reads, L=0: full recovery; q alone is not cumulative leakage',
 'limits':'finite hidden-object interface, no computational or empirical coverage claim'},sort_keys=True))
