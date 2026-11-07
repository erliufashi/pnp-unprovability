import itertools,json
from fractions import Fraction
checks=[]
p=Fraction(1,4);K=4
correlated_success=p
independent_success=1-(1-p)**K
assert correlated_success<independent_success
checks.append('correlated marginals do not amplify')
hazards=[Fraction(1,4),Fraction(1,2),Fraction(3,4),Fraction(1,4)]
failure=Fraction(1)
for h in hazards:failure*=1-h
assert failure<=(1-p)**4
checks.append('conditional hazards multiply without identical rates')
count=0
for m in range(1,9):
 universe=list(itertools.product((0,1),repeat=m))
 for k in range(m+1):
  # Reveal the first k bits; guess all unrevealed bits are zero.
  successes=sum(x==x[:k]+(0,)*(m-k) for x in universe)
  assert Fraction(successes,len(universe))==Fraction(2**k,2**m)
  # Equality-only verified guesses cover at most one string each.
  q=min(k,len(universe));guesses=universe[:q]
  verified=sum(x in guesses for x in universe)
  assert Fraction(verified,len(universe))==Fraction(q,2**m)
  count+=1
checks.append('complete hidden-bit and equality-query universes')
# Four hypotheses (a marked index) vs sixteen hypotheses (an arbitrary 4bit array).
assert 2**2==4 and 2**4==16
checks.append('index vs full-array entropy units')
# Two-sided risk bookkeeping, exact fractions.
alpha=Fraction(1,100);q=3;h=Fraction(1,2)
bound=1-(1-h)**q-q*alpha
assert bound==Fraction(169,200)
checks.append('soundness union-bound arithmetic')
print(json.dumps({'status':'pass','checks':checks,'complete_universe_parameter_cases':count,'correlated_success':str(correlated_success),'independent_success':str(independent_success),'conditional_failure':str(failure),'risk_lower_bound':str(bound),'real_task_hazard_estimated':False},indent=2))
