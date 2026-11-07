"""Finite opaque insertion-sort sanity; not a general lower-bound proof."""
import itertools,json,math
from fractions import Fraction

def solve(a):
    order=[]; transcript=[]
    for i in range(len(a)):
        pos=0
        while pos<len(order):
            j=order[pos]
            c=(a[i]>a[j])-(a[i]<a[j]); transcript.append(c)
            if c==0: return True,tuple(transcript)
            if c<0: break
            pos+=1
        order.insert(pos,i)
    return False,tuple(transcript)

out=[]
for n in range(1,7):
    paths=[solve(a)[1] for a in itertools.permutations(range(n))]
    assert len(set(paths))==math.factorial(n)
    assert all(not (len(a)<len(b) and b[:len(a)]==a) for a in paths for b in paths)
    kraft=sum((Fraction(1,2**len(p)) for p in paths),Fraction())
    mean=Fraction(sum(map(len,paths)),len(paths))
    assert kraft<=1
    # Exact exponential equivalent of mean >= log2(n!).
    assert 2**sum(map(len,paths)) >= math.factorial(n)**len(paths)
    checks=0
    if n<=4:
        for a in itertools.product(range(n),repeat=n):
            answer,_=solve(a)
            assert answer==(len(set(a))<n)
            checks+=1
    out.append(dict(n=n,negative_leaves=len(paths),kraft=str(kraft),mean=str(mean),all_assignments_checked=checks))
print(json.dumps({'status':'pass','scope':'finite sanity only','rows':out},indent=2))
