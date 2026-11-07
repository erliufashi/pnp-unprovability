import itertools,json

def direct(form,n):
    return any(all(any(a[abs(lit)-1] == (lit>0) for lit in clause) for clause in form) for a in itertools.product((False,True),repeat=n))

def cached(form):
    # Nondeterministic traversal represented by exhaustive branching only on
    # first access to a variable. Dictionary values persist across clauses.
    def clause_step(ci,li,cache):
        if ci==len(form):return True
        clause=form[ci]
        if li==len(clause):return False
        lit=clause[li];v=abs(lit)
        choices=(cache[v],) if v in cache else (False,True)
        for bit in choices:
            nxt=dict(cache);nxt[v]=bit
            if bit==(lit>0):
                if clause_step(ci+1,0,nxt):return True
            elif clause_step(ci,li+1,nxt):return True
        return False
    return clause_step(0,0,{})

lits=(-2,-1,1,2)
clauses=[(a,) for a in lits]+list(itertools.combinations_with_replacement(lits,2))
checks=0
for k in range(1,4):
    for form in itertools.product(clauses,repeat=k):
        assert direct(form,2)==cached(form)
        checks+=1
bad=((1,),(-1,))
assert direct(bad,1)==cached(bad)==False
# Independently re-guessing on each occurrence can satisfy every nonempty clause.
broken=all(any(True for _ in c) for c in bad)
assert broken is True
print(json.dumps({'formulas_checked':checks,'variables':2,'clauses_per_formula':[1,3],'consistent_cache_matches_assignments':True,'unsat_counterexample':bad,'correct_accepts':False,'independent_reguess_accepts':broken,'scope':'finite simulation check, not NSPACE lower bound'},indent=2))
