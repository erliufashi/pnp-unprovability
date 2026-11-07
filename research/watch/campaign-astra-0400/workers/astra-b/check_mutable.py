#!/usr/bin/env python3
"""Standard-library exhaustive checks. Emits JSON, assertion failure exits nonzero."""
import itertools,json

def collision(a):
    n=len(a); i=0; swaps=reads=writes=loops=0
    while i<n:
        loops+=1; v=a[i]; reads+=1
        if v==i+1:
            i+=1; continue
        j=v-1; z=a[j]; reads+=1
        if z==v:
            return True,dict(swaps=swaps,reads=reads,writes=writes,loops=loops)
        a[i]=z; a[j]=v; writes+=2; swaps+=1
    return False,dict(swaps=swaps,reads=reads,writes=writes,loops=loops)

def main():
    cases=0; maxima={}
    for n in range(1,8):
        mx={k:0 for k in ['swaps','reads','writes','loops']}
        for x in itertools.product(range(1,n+1),repeat=n):
            a=list(x); ans,c=collision(a)
            assert ans==(len(set(x))<n)
            assert sorted(a)==sorted(x)
            assert c['swaps']<=n and c['reads']<=4*n+2 and c['writes']<=2*n and c['loops']<=2*n+1
            for k in mx: mx[k]=max(mx[k],c[k])
            cases+=1
        maxima[n]=mx
    x=[2,1]; canonical=x.copy(); collision(canonical)
    x[0]=1; canonical[0]=1
    assert len(set(x))==1 and len(set(canonical))==2
    print(json.dumps({'ok':True,'cases':cases,'maxima':maxima,'update_counterexample':{'original_then_update':x,'canonical_then_update':canonical}},sort_keys=True))
if __name__=='__main__': main()
