from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent

def law(p,q0,q1):
    return {(a,b):(p if a else 1-p)*((q1 if a else q0) if b else 1-(q1 if a else q0)) for a,b in product((0,1),repeat=2)}
def tv(a,b): return sum(abs(a[k]-b[k]) for k in a)/2

def probe():
    grid=[F(i,4) for i in range(5)]; count=0
    for p,pc,q0,q1,q0c,q1c in product(grid,repeat=6):
        x=law(p,q0,q1); y=law(pc,q0c,q1c)
        actual=tv(x,y); e1=abs(p-pc); e20=abs(q0-q0c); e21=abs(q1-q1c)
        average=e1+(1-p)*e20+p*e21
        worst=max(e20,e21); product_bound=1-(1-e1)*(1-worst)
        assert actual<=average and actual<=e1+worst and actual<=product_bound
        count+=1
    cases=[]
    for m in [2,4,16,128,1024]:
        benchmark=sum(int(q==m-1) for q in range(m))/m
        pipeline=int((m-1)==m-1)
        assert benchmark==1/m and pipeline==1
        cases.append({'m':m,'uniform_module_error':str(F(1,m)),'executable_boundary_router_error':pipeline})
    result={'passed':True,'exact_two_step_adaptive_kernel_pairs':count,'conditional_union_reference_mean_and_product_bounds':True,'rare_query_controls':cases,'not_real_task_evaluation':True,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return result

if __name__=='__main__':
    report=HERE/'composition-tests-v1.json'; assert not report.exists()
    started=time.time(); result=probe(); result['seconds']=time.time()-started
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
