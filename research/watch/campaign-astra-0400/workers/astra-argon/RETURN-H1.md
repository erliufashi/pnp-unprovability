# Astra divergent audit — RETURN-H1

Owner: **astra-argon**. Version: H1, 2026-11-07 +08. Authorized final stop: **2026-11-07 04:00:00 +08**; old 01:29/04:29 prose is historical and not enforced. Requested model: gateway_responses/gpt-6-astra:max; runtime routing is not independently attested here. No agents launched. Mail configured paused/followUp/60; manually checked inbox and joined-room list (both empty).

**Result:** two nonduplicate, falsifiable audit proposals and one numerical correction. No shared-board writes. T1/T2/T3-v2 remain **UNRESOLVED**. These are local mathematical/interface findings, not real-distribution coverage or independent acceptance.

## Read scope and deduplication

Read current-contract-v2.json and the entire graph (all nodes/edges) from alternatives/practical-core/research/shared-board.json; also inspected its coordination/publication history. Graph snapshot is `board-graph.json` alongside this report. Read latest six worker ASTRA-CHECKPOINT-H1 artifacts, chief RAND-BRAM-v2 and OPAQUE-v2, and prior Argon ASTRA-ARGON-H1-RETURN. Shared state is concurrent; this is a bounded audit snapshot, not a claim that later publications were reviewed.

Already covered, therefore **not new proposals**: fullscan deterministic-to-BPP gap, public-multiset Yao leakage, raw-versus-CMP distinction, Las Vegas opaque Kraft bound, joint advice leakage, GVC cumulative feedback, dynamic OR capacity, and hidden Boolean fingerprint first-error analysis. Prior Argon protocol matrix is not resubmitted.

## 1. GVC cost closure: upper bounds were used as necessary lower bounds

**Priority:** immediate formula correction. **Target:** D-GVC-COST-1, particularly the latest D checkpoint's “Generate-and-Verify” paragraph. This is distinct from its already-known missing verification/serialization costs: the issue persists after those costs are included.

The checkpoint assumes per-candidate verification time `<= c_v`, serialization time `<= c_s`, and wire length `<= m`, then states actual candidate count C **must** satisfy

    C(c_v+c_s)+overhead <= W,
    Cm+state/feedback_bits <= U.

That implication is false. Upper bounds provide a sufficient conservative reservation test, not a necessary actual-cost constraint.

**Strict counterexample:** two candidates each actually take one time unit, while their valid declared upper bound is 100. With W=2 and zero overhead, the trajectory is feasible; the alleged necessary condition says 200<=2. Likewise two one-bit candidates may each have a declared maximum width 100; U=2 suffices for actual transmission, not 200.

**Correct statements:**

- Exact feasibility is `sup_x sum_j t_j(x)+o(x) <= W`, with the appropriate legal histories included in x, and corresponding exact wire/peak-memory constraints.
- If all actual costs are bounded above as assumed, `C(c_v+c_s)+o_max <= W` and `Cm+u_max <= U` are **sufficient** reservation conditions. Failure of this conservative test does not prove infeasibility.
- Necessary cardinality bounds require actual lower bounds, e.g. `t_j(x)>=ell` for every attempted candidate on every relevant trajectory gives `C ell+o_min<=W`. Fixed-width exact m-bit payloads give `Cm+u_actual<=U`; “width at most m” does not.
- Even a sum of individual worst-case costs need not equal the worst case of their sum: `sup_x sum_j t_j(x) <= sum_j sup_x t_j(x)`, with possible strict inequality when slow paths are mutually exclusive.

**Falsifiable acceptance:** a cost checker must accept the two-candidate example using actual costs, reject it only under an explicit reservation policy, and label these as different contracts. Add a mutually exclusive slow-path test. Keep the original exact trajectory ledger and information-capacity theorem; the correction does not refute either.

**Disposition:** suggest an owner-authored erratum/new immutable evidence, retaining the published version. Existing F(1,2)=2 correction is already recorded; do not count it again as new work.

## 2. Fixed-fuel random algorithms: replace ideal uniform seeds with their implementable distribution

**Priority:** new cross-node lemma candidate, suggested ID `ARGON-DYADIC-SEED-1`. Targets random fullscan, strong-reference resource closure, and F-DYN-FP-1. This is not a repeat of public/raw seed leakage: all observations may remain perfectly Boolean-only.

F-DYN-FP correctly notes that exact uniform field sampling by rejection has expected, not bounded worst-case, random-bit cost. The next falsifiable obligation is an exact finite-fuel repair rather than treating this as a footnote.

### Impossibility under the explicit fair-bit model

A sampler using at most b independent fair bits can be padded to a depth-b binary tree. Every outcome probability is an integer multiple of 2^-b. Therefore it cannot output exactly uniform r in F_p for odd prime p: 1/p is not dyadic. This does not apply if a uniform-field primitive is explicitly part of the machine; that primitive then needs its own cost/implementation contract. It also does not disallow expected-time rejection sampling.

### Exact replacement theorem for the existing fingerprint interface

Let seed distribution D on F_p be independent of the client. Keep F-DYN-FP's Boolean-only interface and arbitrary additive updates. Set

    d = min(p, K(N-1)).

The maximal first-error probability is the **sum of the d largest seed probabilities**, not generally d/p. For N=1 it is zero. Proof: the seed-independent ideal transcript's nonzero polynomials have a union of at most d roots, so its D-mass is at most top-d mass. Conversely partition the d heaviest seeds into at most K blocks of size at most N-1 and use the monic root-product vectors, exactly as in the existing tightness construction. Restricted update/time budgets preserve the upper bound but may destroy attainability.

This is a proposed local extension with a self-contained proof, not an implementation acceptance.

### Bounded-time modulo sampler, exact formulas

Take b fair bits U uniform on `{0,...,B-1}`, B=2^b, and r=U mod p. Write B=qp+a, 0<=a<p. There are a seed values of mass (q+1)/B and p-a of mass q/B. Thus

    optimal first-error probability = [d q + min(d,a)] / B,
    TV(D,Uniform(F_p)) = a(p-a)/(pB).

The probability is at most `min(1,d/p+TV)`. No independence across adaptive queries is assumed. Crucially, the one initial seed-distribution TV penalty is paid **once** for the whole transcript, not K times; the transcript is a channel applied to the initially sampled seed and independent client randomness.

Example: p=3, b=2, N=2, K=1. Seed probabilities are (1/2,1/4,1/4). The client tests polynomial X and causes error 1/2, exceeding the ideal uniform bound 1/3. Boolean-only secrecy and fixed code do not repair biased randomness.

**Falsifiable acceptance:** specify RNG as fair bits versus an atomic field/word primitive; freeze its worst-case fuel. Test the p=3 example; compute the above top-d formula; show the same resource-accounted sampler on both reference and candidate sides. For capped rejection, separately charge abort as error or an explicit output and prove its probability—never silently retry beyond fuel. Charge seed generation, modulo arithmetic, and client updates; no field-operation claim is automatically a BRAM instruction count.

**Relevance to opaque:** C63's zero-error measure-one/Kraft argument does not require an exactly uniform field seed and is not refuted. It remains a CMP-only query theorem. A bounded-error opaque extension still requires a separate proof; this RNG audit does not supply one.

## Numerical correction, not a third new node

Chief RAND-BRAM-v2 correctly derives `q/binom(n,2)` for uniform sampling of distinct pairs on a unique-collision input. Its n>=208 cutoff proves success <1/3, which is stronger than needed to reject error<=1/3. Required success is **>=2/3**. Using q<=F=32n+512, exclusion already follows from

    F/binom(n,2) < 2/3
    iff n(n-1) > 3F
    iff n^2-97n-1536 > 0.

The first integer threshold is **n=111**, and the inequality remains true thereafter. n=110 gives 11990<12096; n=111 gives 12210>12192. This sharpens only the stated optimistic pair-count envelope, not the actual charged implementation and certainly not all randomized BRAM algorithms. n>=208 is not false; it was not the earliest BPP(1/3)-failure threshold.

Also narrow “random hash sampling” language: the pair-family calculation applies only if that hash procedure really reduces to the specified uniformly sampled pair set. It is not a lower bound for arbitrary hashing algorithms.

## Actual checks and release boundary

`audit-checks.json` records executed Python-standard-library exact-rational checks: 32 modulo-seed distributions (p=3,5,7,11; b=1..8), every subset size d, the exact TV formula, and threshold 111. The cost counterexample is arithmetic, not a measured service benchmark. Checks passed; none is a general machine implementation test or independent peer review.

Minimal reproducibility of the seed formulas: enumerate residues of integers 0..2^b-1 modulo p; count each residue, sort counts descending, sum the first d and divide by 2^b; compare to `(d*q+min(d,a))/2^b`. Compute half the sum of absolute differences from 1/p for TV. All operations can use rational arithmetic.

Consumer entry is this exact RETURN-H1 path; companion JSON is optional audit evidence. Owner astra-argon; no existing evidence overwritten, no software installed, no shared entry/configuration changed, no rollback required. Future corrections should be explicit addenda preserving historical claims. Chief/owners may decide whether to add nodes; divergent role does not claim or publish on the shared board.
