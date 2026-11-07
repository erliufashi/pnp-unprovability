# Campaign Astra C — H1 return

## Scope and board action
Read `research/current-contract-v2.json` (revision 2): T1/T2 remain UNRESOLVED and T3-v2 requires a same-budget model, capability preservation, real-distribution coverage, and resources. The shared board was at round 82 with C62 and E-chief-OPAQUE-1 already done; no result was treated as solved. I added and published the new leaf `ASTRA-C-CLOSURE-1` (round 90), linked to M22/M23, to make this protocol-closure audit explicit.

## Main audit result: opaque comparator is not a transparent raw-word theorem
The CMP-only argument is sound only under a frozen interface: private keys are inaccessible except through `CMP(i,j)`, all key-dependent replies are charged, and no input-dependent preprocessed state, timing, labels, or retained raw representation is available. On all-distinct inputs, deterministic correctness requires distinguishing the relevant order types, giving a comparison-tree leaf count of at least `n!` and depth `ceil(log2(n!))`; a nondeterministic witness can name a pair and verify equality with one CMP. This is a useful *black-box protocol lemma*.

It does not transfer to raw-word BRAM/RAM. If `INPUT(i)` reveals a w-bit value, the algorithm may bucket/direct-address when the domain is small enough, or hash/radix-sort under the declared word operations. For values in `[0,n-1]` and O(n) workspace, one scan plus a bitmap decides collision in O(n), contradicting any claimed Omega(n log n) comparison lower bound. If `w < log2 n`, collision follows from pigeonhole without reading elements (assuming n and w are public). If CMP and INPUT are both exposed, the theorem must charge and analyze both channels; CMP-only lower bounds cannot be pasted onto the union model.

Therefore the rigorous distinction is observational, not a P-vs-NP separation: opaque protocol = restricted information channel; transparent raw-word model = arithmetic/addressing channel. A claimed transfer is refuted by the explicit bitmap algorithm, not merely by a terminology objection. SUM/DOT also expose the incompatibility: if raw values are needed to define them, the raw channel is present and comparator-only conclusions no longer apply.

## C62 finite-threshold audit
C62's finite threshold can close only the quantifier “there exists n0 such that the asymptotic deterministic BRAM bound wins” for its *declared* Gamma envelope and task family. It cannot repair a model mismatch. The threshold proof must list, at the selected n=2^E, every word width, time/depth, workspace, output/trap convention, input instruction semantics, and the full state (including counters and addressing). It also must not silently exclude a raw scan, arithmetic hash, mutable input, or external index that the competing model receives. A finite n certificate is thus conditional on the frozen interface; it is not evidence that CMP-only opacity holds for transparent words, nor a certificate for T3-v2.

## Preprocessing/index escape routes
A valid indexed protocol needs a lifecycle ledger:
`T_build + sum(T_query) + sum(T_update) + serialization/reset`, peak live state, index size, versioning, and cold first request. Both competitors must receive the same preprocessing privilege and denominator. Retaining the original raw input (even read-only or on an “external” file) is information-bearing state and must be charged or declared as an input channel. If query q is known before Build, precomputing only that answer is a different protocol from late-query indexing.

Computability or uniformity of Build is insufficient: a fixed Build can read an undeclared grader/answer database and materialize labels. The mechanical guard is provenance/non-interference: holding the permitted observation view fixed while changing forbidden label sources must leave the index unchanged. Only permitted-data computation may be included, with its work charged. For a query family of size K, an index with enough answer bits can legitimately defeat online lower bounds; that is amortization, not a contradiction. Dynamic updates likewise carry information: trusted old bits, mutable raw records, persistent logs, and verifier feedback must be counted symmetrically. Otherwise a “small local workspace” comparison is not same-budget.

## Verdict and next test
`E-chief-OPAQUE-1` is accepted as a conditional CMP-only protocol lemma and rejected as evidence of a transparent raw-word separation. C62 is a conditional finite-envelope closure, not a universal escape from the interface objection. The decisive next test is a frozen matrix with rows CMP-only, raw INPUT, CMP+INPUT, indexed-late-query, and indexed-known-query, recording channels, lifecycle costs, retained state, and update semantics; any surviving gap must hold in the same row for both sides. No T1/T2/T3-v2 claim is made.

Evidence basis: `E-chief-OPAQUE-1`, `C62`, `E-argon-FNS-audit1`, `E-argon-IDX-audit1`, and the current contract/board. Old evidence was not modified.
