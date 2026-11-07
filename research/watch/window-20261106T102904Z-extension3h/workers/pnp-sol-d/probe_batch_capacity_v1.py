#!/usr/bin/env python3
"""Exact finite decision-tree optimization; stdlib only, no hidden inputs."""
from functools import lru_cache
from itertools import combinations
import json

def capacity(k,l):
    return 1+sum(min(l,1<<j) for j in range(k))

def optimum(weights,k,l):
    n=len(weights)
    @lru_cache(None)
    def solve(mask,rounds):
        ids=[i for i in range(n) if (mask>>i)&1]
        if not ids: return 0
        if not rounds: return max(weights[i] for i in ids)
        best=solve(mask,rounds-1)
        for size in range(1,min(l,len(ids)-1)+1):
            for group in combinations(ids,size):
                a=sum(1<<i for i in group)
                best=max(best,solve(a,rounds-1)+solve(mask^a,rounds-1))
        return best
    return solve((1<<n)-1,k)

checks=0
for n in range(1,9):
    for weights in ([1]*n,list(range(1,n+1)),[1+(i*i+3*i)%7 for i in range(n)]):
        for k in range(5):
            for l in range(0,min(4,n)+1):
                actual=optimum(tuple(weights),k,l)
                expected=sum(sorted(weights,reverse=True)[:capacity(k,l)])
                assert actual==expected,(n,weights,k,l,actual,expected)
                checks+=1
# Generic binary capacity need not be attainable by batch verification.
assert capacity(10,1)==11 and capacity(10,2)==20
assert capacity(10,3)==28 and capacity(10,1024)==1024
# No-query reconstruction permits one guess; verified-hit-only does not.
assert capacity(0,5)==1
# Independently optimize scheduled caps; branch budgets use the same suffix.
def scheduled_optimum(n,caps):
    @lru_cache(None)
    def solve(mask,i):
        if not mask: return 0
        if i==len(caps): return 1
        ids=[j for j in range(n) if mask>>j&1]
        best=solve(mask,i+1)
        for size in range(1,min(caps[i],len(ids)-1)+1):
            for group in combinations(ids,size):
                a=sum(1<<j for j in group)
                best=max(best,solve(a,i+1)+solve(mask^a,i+1))
        return best
    return solve((1<<n)-1,0)
from itertools import product
scheduled_checks=0
for caps in product(range(4),repeat=3):
    c=1
    for l in reversed(caps): c+=min(l,c)
    for n in range(1,9):
        assert scheduled_optimum(n,caps)==min(n,c),(n,caps,c)
        scheduled_checks+=1
print(json.dumps({'ok':True,'exact_tree_checks':checks,'scheduled_cap_checks':scheduled_checks,
 'cases':'n=1..8, three integer prior families, K=0..4, L=0..min(4,n)',
 'capacity_examples_K10':{str(l):capacity(10,l) for l in [0,1,2,3,4,16,1024]},
 'limits':'finite model verification, not real-world coverage or standard P/NP separation'},sort_keys=True))
