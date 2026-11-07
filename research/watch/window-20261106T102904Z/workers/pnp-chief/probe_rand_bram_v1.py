from fractions import Fraction
from math import comb, ceil, log
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent

def exact_unique_collision(n,q):
    assert 0<=q<=comb(n,2)
    return Fraction(q,comb(n,2))

def dense_bound(C,d,q):
    # With-replacement pair samples: exact miss probability.
    return Fraction(1,1)-Fraction(C-d,C)**q

def run():
    rows=[]
    for n in (64,128,192,200,207,208,256,512,1024,4096):
        F=32*n+512; C=comb(n,2); q=min(F,C); p=exact_unique_collision(n,q)
        rows.append({'n':n,'F':F,'pairs':C,'q_used':q,'unique_collision_success':str(p),'success_float':float(p),'below_one_third':p<Fraction(1,3)})
    assert rows[0]['below_one_third'] is False
    assert rows[4]['below_one_third'] is False
    assert all(row['below_one_third'] for row in rows[5:])
    # Exhaustively enumerate all sampled q-subsets for small C to validate q/C.
    small=[]
    for n in range(2,8):
        C=comb(n,2)
        for q in range(C+1):
            p=exact_unique_collision(n,q)
            # every q-subset contains the unique success pair in exactly C(C-1,q-1) choices
            count=0
            import itertools
            pairs=range(C)
            for subset in itertools.combinations(pairs,q):
                count+=int(q>0 and 0 in subset)
            assert Fraction(count,comb(C,q) if q<=C else 1)==p
            small.append({'n':n,'C':C,'q':q,'p':str(p)})
    dense=[]
    for C,d,q in [(10,1,3),(10,5,2),(100,10,20),(32640,1000,100)]:
        p=dense_bound(C,d,q); assert p>=0 and p<=1
        dense.append({'C':C,'d':d,'q':q,'lower_success':str(p)})
    thresholds=[]
    for delta in (Fraction(1,100),Fraction(1,10),Fraction(1,2)):
        q=ceil(log(3)/(-log(1-float(delta))))
        # exact lower bound using rational arithmetic for recorded q
        thresholds.append({'delta':str(delta),'q_sufficient_float_ceil':q,'exact_success_lower':str(dense_bound(100000,int(delta*100000),q))})
    return {'passed':True,'F_definition':'32n+512 pair-query upper bound only','rows':rows,'small_exhaustive_cases':len(small),'dense_examples':dense,'dense_thresholds':thresholds,'scope':'pair sampling family and dense promise; not all randomized BRAM algorithms','not_claimed':['constant-error full-class lower bound','BSSV theorem transfer to epsilon=1/3','physical RAM or human coverage']}

if __name__=='__main__':
    out=run(); out['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(); out['seconds']=0
    p=HERE/'rand-bram-tests-v1.json'; assert not p.exists(); p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False))
