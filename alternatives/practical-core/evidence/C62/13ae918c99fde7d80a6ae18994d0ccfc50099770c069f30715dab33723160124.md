# C62 — Explicit enormous finite dimension for the full-scan COLL candidate

pnp-sol-c, 2026-11-06. Conditional local numerical/theorem candidate, awaiting independent source/model proof review. **Not physically feasible, not realistic coverage, not a new P/NP/ZFC result.** The point is to pay the asymptotic hidden-constant gap identified in FNS, not to pretend the result is practical.

## 1. Concrete outcome
Under the original-source finite rectangle statement and the explicit BRAM configuration accounting below, the full-scan Γ profile from FNS has a deterministic/nondeterministic separation at the single explicitly named dimension

`n = 2^3,315,164`.

At this dimension:
- `w=6,630,329` bits per word;
- mutable array words `M=2^1,657,582`;
- total word fuel `F=32*2^3,315,164+512`;
- code+static data bound4096 bytes;
-16 word registers, one output word;
- paid zero initialization AND full raw-input acquisition pass;
- the same conservative bit-work cap as FNS.

The fixed512-byte ND collision program and190-byte SUM program still fit the SAME resource vector by their all-n inequalities; nothing was actually executed on an n-word input of this size. This dimension is astronomically outside any practical regime. It resolves only the missing *mathematical finite instantiation* for the candidate, conditional on the cited technical lemma/model mapping; it does not supply a reasonable engineering envelope.

## 2. Original finite source premise, visually checked
BSSV author manuscript2002-10-24,40 pages, SHA256 of original PostScript `38f9bf0da43a21b4073278a24a4e9fade560562544a597818629383c1dc1295a`; URL https://www.cs.washington.edu/homes/beame/papers/randomts.ps . The FNS report records acquisition and scope. Original p23 was rendered to `bssv-page23.png` and read directly to disambiguate all exponent signs.

**Corollary5.4(i):** let k>=8, q<=2^-40*k^-8, and n>=r>=q^(-5k²). For an n-variate D-way deterministic BP of length at most(k-2)n and total size2^S, there is an embedded rectangle R in its accepted inputs, with balanced feet of size

`m>=q^(2k²)*n/2`

and leg density

`alpha(R)>=2^(-sqrt(q)*m-S*r) * accepted_input_fraction`.

This finite statement, not an unspecified Omega constant, is the sole deep literature premise used below. Its full combinatorial proof earlier in the source is not independently certified here. We derive the remaining ED rectangle bound and arithmetic explicitly.

## 3. Elementary ED facts
Work over domain D={0,...,n²-1}. ED accepts exactly all-distinct n-tuples. Under uniform input, collision probability is at most `(n choose2)/n²<1/2` by union bound, so ED's accepted fraction is greater than1/2, in particular greater than1/4.

An embedded rectangle with balanced feet A1,A2 of size m and fixed outside coordinates, containing ONLY distinct arrays, has leg density at most2^-m. Proof: let V_j be the set of ALL values appearing in ANY coordinate in ANY allowed point of leg j. V1 and V2 must be disjoint; otherwise combining the two respective leg assignments yields a duplicate across feet, contrary to every rectangle point being distinct. At least one V_j has at most half of D. That leg has at most(|D|/2)^m assignments, hence its relative density is at most2^-m. Minimum leg density obeys the same bound.

Apply Corollary5.4 to ED. Its rectangle satisfies

`2^-m >=alpha(R)>2^(-sqrt(q)*m-S*r-2)`.

Thus `S*r>m*(1-sqrt(q))-2`. If q<=1/16 and m>=8, this is at least m/2. Therefore

`S > q^(2k²)*n/(4r)`.

A deterministic program for COLL (has a repeated entry) would give an ED BP by flipping sink labels, without increasing depth/size. This is a D lower bound, not a claim that ED itself has the short existential duplicate witness.

## 4. Completely explicit integer parameters
Set

`k=38`,
`Q0=2^40 *38^8 =4,780,448,011,429,432,992,464,896`,
`q=1/Q0`,
`r=Q0^(5k²)`,
`D0=4*Q0^(7k²)`,
`d=ceil(log2 D0)=828,691`,
`E=4*(d+100)=3,315,164`,
`n=2^E`.

Then q exactly meets the Corollary's upper bound; r exactly meets its finite threshold. The additional finite Theorem5.3 precursor threshold `r>=200k²*Q0^(4k²)` is also checked rather than assumed. Since n>=r and `n>=16*Q0^(2k²)`, the resulting rectangle has m>=8. Also Q0>=16 gives sqrt(q)<=1/4.

The elementary lower bound in section3 becomes

`S>n/D0`.

Because n>=128, the common profile fuel satisfies `32n+512<=36n=(k-2)n`, exactly matching the source length hypothesis. No 'large enough' constant is left unspecified in these parameter conditions.

## 5. Explicit complete-state cap for the abstract BRAM
This section concerns ABSTRACT VM configurations, not Python physical RAM. As in FNS, the source BP may have arbitrary static transitions and n-dependent advice independent of the actual x; the lower bound therefore overapproximates every allowed B4096-byte deterministic BRAM program.

For common profile parameters define

`I=16+M`,
`Qbits=I*w+F*(8*4096+8w+w²)`.

Use the conservative BP total-size logarithm upper bound

`S_cap=(M+32)w+2^20`
`      +4*ceil(log2(F+1))`
`      +2*ceil(log2(n+M+32))`
`      +2*ceil(log2(Qbits+1))`.

Accounting justification:
- ALL M mutable words and16 data registers count. An additional16 words overbound current operands, arithmetic temporary results, output/validity word flags and bounded instruction-level scratch. The model does not provide any additional readable host log or arbitrary external workspace.
-2^20 fixed bits grossly overbound PC/dispatch/control, finite code/data-description-dependent constants and trap/status encoding. Valid PC positions are bounded by the code description; an out-of-range static target immediately becomes a rejecting trap. Even if represented as the literal integer, its magnitude is encoded in at most4096 bytes and is covered by this generous constant. No claim that an arbitrary malformed integer target fits only log4096 bits is needed.
- The logarithmic terms overbound remaining fuel, initialization/acquisition progress, memory limits/address bookkeeping beyond register fields and any enforcement counters for the declared bit charge. The original raw input is read-only, separately resident and accessible only by the INPUT instruction; cached input-dependent data are included in M/registers.
- A one-word write-only output can be reduced to a constant number of acceptance/status flags for this decision predicate (halt and output[1]); the extra16 words already overbound keeping the whole word if desired.
- Unfolding through F time levels costs another ceil(log2(F+1))+constant in the logarithm of TOTAL node count. The coefficient4 on the F term already includes this; per-level width is not silently substituted for total BP size.

More explicitly, a configuration has a finite tuple of the listed fields; its possibilities multiply, so their bit lengths add. Each data-read node is labelled by the address already fixed in that tuple and branches on all n² values. Internal arithmetic/static ROM operations are composed into transitions between queries or unrolled along the already-counted clock. Time-dependent behavior has no hidden clock: all future-relevant control appears in the tuple. This gives a BP of depth<=F and total-size logarithm<=S_cap for EVERY deterministic program in the profile. Unobservable harness statistics are omitted because they cannot affect the decision; exposing them would change the ISA and need new accounting.

At this explicit E, w=2E+1 and M=2^(E/2). Direct exact integer checks establish

`S_cap <=64E*2^(E/2)`

and

`S_cap*D0 < n`.

So the mapped BP has `S<=S_cap<n/D0`, contradicting section4's required `S>n/D0`.

The numeric cap is deliberately loose. It is a model-configuration upper bound, not measured resident memory. Independent review should verify the modeled ISA has no additional observation/state primitive; it should not import Python's actual interpreter heap into this abstract claim and then misreport physical feasibility.

## 6. Same finite profile's ND and full-SUM members
FNS froze the38-instruction,512-byte ND program. It generates exactly2w bits one by one, retains i,j in normal registers, bounds-checks both and their inequality before raw data access, and accepts iff the two selected entries agree. Valid distinct-index paths cost12w+21 opcode steps. Initialization costs16+M word units and input acquisition costs n+1. The verified inequality is

`12w+21+(16+M)+(n+1)<=F`.

SUM has190-byte code and7n+9 opcode steps. It also satisfies

`7n+9+(16+M)+(n+1)<=F`.

Bit-work, raw input residency, output size and description bounds are the SAME for D and ND. No free read-only witness and no side-specific uncharged index is supplied. Deterministic preprocessing within F and M is allowed and already covered by the universal BP mapping.

Thus, CONDITIONAL on the original finite rectangle theorem and this model mapping, at the explicitly named single n there is a function COLL computable by a Γ nondeterministic program but no Γ deterministic program, while the same Γ retains the full-array SUM reference. This is stronger than the old OR witness's missing full-scan ability, but far from broad realistic adequacy.

## 7. Exact arithmetic reproducibility
`python3 finite_fullscan_dimension.py` uses Python standard-library arbitrary-precision integers. It builds compact symbolic-dimension integers (no n-element input array) and checks every displayed source condition, the precursor r condition, exact word width, complete BP-space cap, both lower/upper contradictions and paid ND/SUM bounds. Output reports E/d/bit lengths, not millions of decimal digits. The script completed successfully; it does NOT execute COLL or enumerate every D program at that dimension.

The original PS/PDF theorem is not replaced by this arithmetic test. Testing finite inequalities plus an assumed known structural lemma still requires independent mathematical review. The source's randomized ED error constraints remain separate; this is no standard1/3-error R_Γ lower bound. Practical coverage, reference sufficiency, standard P/NP and named ZFC-unprovability remain UNRESOLVED.


## Frozen exact-integer checker

```python
"""Exact integer checks for a huge mathematical dimension, not execution on that input."""
import json

def ceil_log2(x):
    assert x>0
    return (x-1).bit_length()

k=38
Q0=(1<<40)*k**8
r=Q0**(5*k*k)
D=4*Q0**(7*k*k)
d=ceil_log2(D)
E=4*(d+100)
n=1<<E
M=1<<(E//2)
w=2*E+1
B=4096
F=32*n+512
I=16+M
Qbits=I*w+F*(8*B+8*w+w*w)
S_cap=(M+32)*w+(1<<20)+4*ceil_log2(F+1)+2*ceil_log2(n+M+32)+2*ceil_log2(Qbits+1)
S_simple=64*E*M
checks={
 'k_at_least_8':k>=8,
 'q_bound_exact_Q0':Q0==(1<<40)*k**8,
 'r_corollary_54':r==Q0**(5*k*k),
 'r_implies_theorem_53':r>=200*k*k*Q0**(4*k*k),
 'n_at_least_r':n>=r,
 'foot_lower_bound_at_least_8':n>=16*Q0**(2*k*k),
 'sqrt_q_at_most_quarter':Q0>=16,
 'full_time_below_k_minus_2_n':F<=(k-2)*n,
 'exact_word_width':(n*n+1).bit_length()==w,
 'complete_bp_space_below_simple_bound':S_cap<=S_simple,
 'source_required_space_exceeds_complete_cap':S_cap*D<n,
 'source_required_space_exceeds_simple_bound':S_simple*D<n,
 'paid_nd_fits':12*w+21+I+n+1<=F,
 'paid_sum_fits':7*n+9+I+n+1<=F,
 'bytecode_and_address_fit':B>=512 and w>=6,
}
assert all(checks.values()),checks
print(json.dumps({'status':'pass','k':k,'Q0_decimal':Q0,'r_bit_length':r.bit_length(),'D_bit_length':D.bit_length(),'d':d,'E':E,'dimension':'n=2^E','mutable_words':'M=2^(E/2)','word_bits':w,'fuel':'F=32*2^E+512','description_bytes':B,'complete_state_formula':'(M+32)*w+2^20+4*ceil_log2(F+1)+2*ceil_log2(n+M+32)+2*ceil_log2(Qbits+1)','simple_space_cap':'64*E*2^(E/2)','checks':checks,'scope':'exact arithmetic on compact integers; no array of length n, no physical feasibility or coverage claim'},indent=2))

```

## Frozen output

```json
{
  "status": "pass",
  "k": 38,
  "Q0_decimal": 4780448011429432992464896,
  "r_bit_length": 591921,
  "D_bit_length": 828691,
  "d": 828691,
  "E": 3315164,
  "dimension": "n=2^E",
  "mutable_words": "M=2^(E/2)",
  "word_bits": 6630329,
  "fuel": "F=32*2^E+512",
  "description_bytes": 4096,
  "complete_state_formula": "(M+32)*w+2^20+4*ceil_log2(F+1)+2*ceil_log2(n+M+32)+2*ceil_log2(Qbits+1)",
  "simple_space_cap": "64*E*2^(E/2)",
  "checks": {
    "k_at_least_8": true,
    "q_bound_exact_Q0": true,
    "r_corollary_54": true,
    "r_implies_theorem_53": true,
    "n_at_least_r": true,
    "foot_lower_bound_at_least_8": true,
    "sqrt_q_at_most_quarter": true,
    "full_time_below_k_minus_2_n": true,
    "exact_word_width": true,
    "complete_bp_space_below_simple_bound": true,
    "source_required_space_exceeds_complete_cap": true,
    "source_required_space_exceeds_simple_bound": true,
    "paid_nd_fits": true,
    "paid_sum_fits": true,
    "bytecode_and_address_fit": true
  },
  "scope": "exact arithmetic on compact integers; no array of length n, no physical feasibility or coverage claim"
}

```
