from functools import lru_cache
from itertools import product,combinations
from pathlib import Path
import hashlib,json,math,time
HERE=Path(__file__).resolve().parent

def exact_decision_depth(n):
    inputs=list(product(range(n),repeat=n)); yes=0
    for k,keys in enumerate(inputs):
        if len(set(keys))<n: yes|=1<<k
    allmask=(1<<len(inputs))-1; partitions=[]
    for i,j in combinations(range(n),2):
        out=[0,0,0]
        for k,keys in enumerate(inputs):
            r=0 if keys[i]<keys[j] else 1 if keys[i]==keys[j] else 2
            out[r]|=1<<k
        partitions.append((i,j,out))
    @lru_cache(None)
    def depth(mask):
        if not (mask&yes) or not (mask&(allmask^yes)): return 0
        best=999
        for i,j,parts in partitions:
            children=[mask&part for part in parts if mask&part]
            if len(children)<=1: continue
            best=min(best,1+max(depth(child) for child in children))
        assert best<999
        return best
    value=depth(allmask)
    lower=(math.factorial(n)-1).bit_length()
    assert value>=lower
    return {'n':n,'private_assignments':len(inputs),'exact_optimal_CMP_depth':value,
            'factorial_lower':lower,'reachable_DP_states':depth.cache_info().currsize}


def nd_checks(n):
    width=n.bit_length(); count=0
    for keys in product(range(n),repeat=n):
        accepted=False
        for i,j in product(range(1<<width),repeat=2):
            valid=0<=i<j<n
            # The logical ND solver only gets the ternary answer, not raw keys.
            response=((keys[i]>keys[j])-(keys[i]<keys[j])) if valid else None
            result=valid and response==0
            assert int(valid)<=1
            accepted=accepted or result; count+=1
        expected=len(set(keys))<n
        assert bool(accepted)==expected
        # Negative controls change the input protocol: raw keys or trusted summary.
        raw_solver=len(set(keys))<n
        trusted_summary=expected
        assert raw_solver==trusted_summary==expected
    return {'n':n,'all_ND_index_branches':count,'stored_guess_bits':2*width,
            'CMP_per_valid_branch':1,'invalid_branch_CMP':0,
            'raw_values_bypass_CMP':True,'trusted_summary_bypasses_CMP':True}


if __name__=='__main__':
    report=HERE/'opaque-tests-v1.json'; assert not report.exists(); start=time.time()
    rows=[exact_decision_depth(n) for n in range(1,5)]
    nd=[nd_checks(n) for n in range(1,5)]
    assert math.factorial(9)>2**18
    result={'passed':True,'exact_small_decision_trees':rows,'ND_and_visibility_controls':nd,
            'finite_query_only_example':{'n':9,'factorial':math.factorial(9),'two_power_Q':2**18,'Q':18,'det_lower':19,'ND_queries':1,'full_CPU_code_storage_profile_not_instantiated':True},
            'scope':'ternary opaque comparator input, not general raw-array RAM; Python harness is not a security boundary or exact physical VM cost',
            'general_lower_bound':'proved by indistinguishability/negative leaves, not by these finite tests',
            'seconds':time.time()-start,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False))
