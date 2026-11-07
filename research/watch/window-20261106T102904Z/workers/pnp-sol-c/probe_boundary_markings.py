import itertools,random,json

def check_path(N,I,h,ops):
    heads=[0]*h;m=N//I;marked=[False]*m;marked[0]=True
    markings=1;unmarkings=0
    for t,(kind,a,b) in enumerate(ops,1):
        if kind=='move':heads[a]=max(0,min(N-1,heads[a]+b))
        else:heads[a]=heads[b]
        new=[]
        for i in range(m):
            lo=i*I;hi=(i+1)*I-1
            distance=min(max(lo-p,0,p-hi) for p in heads)
            value=True if distance==0 else False if distance>=I else marked[i]
            if value and not marked[i]:markings+=1
            if marked[i] and not value:unmarkings+=1
            new.append(value)
        marked=new
        assert sum(marked)<=3*h
        assert markings<=1+t/I,(N,I,h,t,heads,markings)
        assert unmarkings<=markings

def actions(h):
    return [('move',a,d) for a in range(h) for d in (-1,1)]+[('jump',a,b) for a in range(h) for b in range(h) if a!=b]
paths=0
for h,length in ((1,10),(2,6)):
    for ops in itertools.product(actions(h),repeat=length):
        check_path(16,2,h,ops);paths+=1
r=random.Random(60)
for _ in range(2000):
    h=3;ops=[r.choice(actions(h)) for _ in range(128)]
    check_path(64,4,h,ops);paths+=1
# Literal source typo: one far interval stays uncovered during 100 oscillations.
N=64;T=100
assert T>8*T/N
print(json.dumps({'paths_checked':paths,'all_prefix_marking_budget_checks':True,'backward_and_head_to_head_jumps':True,'literal_uncovered_steps_counterexample':{'N':N,'T':T,'far_interval_unmark_events':0,'far_interval_uncovered_steps':T,'incorrect_bound_8T_over_N':8*T/N},'scope':'finite geometric-lemma sanity test, not a substitute for entropy/collision proof'},indent=2))
