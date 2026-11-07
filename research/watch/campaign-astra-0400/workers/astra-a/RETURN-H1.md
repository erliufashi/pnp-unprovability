# Astra A — constant-error randomized full-scan collision/ED

## Result classification
**Conditional model-boundary / precise model failure; not a separation.** T1/T2/T3-v2 remain unresolved.

## Claim
The phrase “full scan collision/ED under the same BRAM accounting” is insufficient unless the fuel/time budget is fixed as part of the model. BRAM space alone does not exclude collision/Element Distinctness.

For an input `x[1..n]`, the following deterministic algorithm uses only O(1) words of working storage (hence fits any positive BRAM budget and the 16w-register accounting):

```
for i = 1..n:
  for j = i+1..n:
    read x[i], x[j] (re-scan input as permitted)
    if x[i] == x[j]: return COLLISION
return DISTINCT
```

It is exact (error 0), and costs `n(n-1)/2` pair comparisons, plus the corresponding input reads. Thus it is also a valid constant-error randomized algorithm if unrestricted full scans/re-reads are permitted. A bucketed variant can reduce constants under additional assumptions, but is unnecessary for this boundary result.

## Same-budget implication
This algorithm is **not** a valid witness under the commonly cited fixed linear fuel envelope `F = 32n + 512` (or any `F = Θ(n)` envelope): its Θ(n²) read/compare cost exceeds F for sufficiently large n. Conversely, the chief’s pair-sampling negative control only shows that sampling `q=Θ(n)` random pairs misses a single planted duplicate with probability approaching 1; it does not by itself prove that every randomized full-scan program with `F=Θ(n)` and the stated BRAM/register model fails. A matching randomized lower-bound theorem with exactly the same input-access, initialization, random-tape, memory, and fuel accounting is still required.

For the planted-one-duplicate distribution, a pair sample of q uniformly random distinct pairs detects it with probability
`1 - (1 - 1/C(n,2))^q <= q/C(n,2)`,
so q=O(n) gives O(1/n) detection, not constant success. This is a negative control, not a universal lower bound.

## Required contract repair
Freeze these fields explicitly before treating an algorithm or lower bound as comparable:

1. Are input re-reads allowed, and is a “full scan” one pass or arbitrarily many passes?
2. Exact fuel accounting for reads, comparisons, hash evaluation, initialization, and random bits.
3. Whether external/write-only state or uncharged I/O is allowed.
4. Word width and value comparison cost, including the 16w register and BRAM capacity convention.
5. Error quantifier (worst-case input with internal randomness versus distributional average-case).

With `F=Θ(n)`, this artifact establishes only the algorithmic counterexample to a **space-only** interpretation and the remaining proof obligation under the strict same-fuel interpretation. It does not establish a randomized lower bound or any P/NP conclusion.

## Board
Added and claimed `A-ASTRA-RAND-FULLSCAN-1`; publication follows on the shared board. Existing `E-chief-RAND-BRAM-1` and `E-argon-RAND-ED-2` were treated as non-duplicates: this node isolates the re-read/fuel ambiguity and states the exact algorithm and residual obligation.
