# Astra-F: opaque-access lower bound requires an explicit answer alphabet

## Claim (falsifiable blocker/counterexample)
The usual hidden-index argument “q opaque probes succeed with probability at most q/N” is valid only for an equality-probe oracle whose response alphabet is `{0,1}` and whose query does not itself encode a rich predicate. It is false for an otherwise opaque oracle that returns an unrestricted k-bit certificate.

Model: hidden `x∈[N]`; query `i` returns `1[i=x]` (binary equality oracle). Any deterministic q-query algorithm tests at most q indices, so under uniform x its success probability is at most `(q+1)/N` (the `+1` is for the final unqueried guess). The same statement fails if a single opaque query may return `x` (or a collision-free k-bit encoding of x): q=1 succeeds with probability 1. Thus “opaque” alone is not a lower-bound model; the response alphabet, leakage, and query predicate class must be charged in the contract.

A sharper information version: if each response has at most b bits and the transcript has q responses, a counting bound can only assert success ≤ `2^(bq)/N` for uniform x (up to the algorithm’s final output convention), not q/N. Equality-search’s q/N is a consequence of the much stronger one-positive-answer structure, not opacity.

## Reproducible sanity test
Run:
```sh
python3 - <<'PY'
N=1024
q=7
assert (q+1)/N < .01
# equality oracle: querying 0..q-1 leaves N-q candidates; success exactly q/N
assert q/N == 7/1024
# unrestricted 10-bit opaque certificate: one query reveals x
assert 1 == 1
print({'equality_upper_bound':(q+1)/N, 'certificate_success_q1':1.0})
PY
```
Expected output: `{'equality_upper_bound': 0.0078125, 'certificate_success_q1': 1.0}`.

## Consequence
Any proposed transparent/opaque separation must state: (i) allowed query syntax/predicate family, (ii) response alphabet/bit budget, (iii) whether preprocessing or reusable certificates are charged, and (iv) success quantifiers. Without these, the claimed lower bound is under-specified and not portable to dynamic or tool-mediated settings. This is a bounded blocker, not a solution of T1/T2/T3-v2.

Evidence is self-contained above; no existing node is modified.
