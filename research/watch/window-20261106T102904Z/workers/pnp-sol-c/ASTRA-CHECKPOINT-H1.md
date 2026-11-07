# Astra C checkpoint H1 — C63 opaque Las Vegas bound

Owner: pnp-sol-c. Date: 2026-11-06. Status: conditional local theorem candidate, not independently accepted. Standard P/NP and current T3-v2 remain UNRESOLVED.

## Scope and nonduplication

Read ACTIVE/state, TEAM-CONTRACT-v1, current-contract-v2, OPAQUE-v2 and shared-board titles. `next` returned no available leaf; created and claimed C63 via transactional board CLI. This is a new zero-error expected-query extension of OPAQUE, not a rerun of FNS/C62/C56 or a transparent BRAM randomized lower bound. Mail manually claimed and configured paused/followUp/60, roomWake none.

The user and supervisor report a revised 04:00 cutoff, while this child developer contract retains a hard 01:29:04 cutoff. No historical contract was overwritten, and this checkpoint is completed before either cutoff. No renewal or background process is introduced.

## Theorem: zero-error randomness does not remove the opaque comparison bottleneck

Fix n and the protocol of OPAQUE-v2: n public handles, private keys in {0,...,n−1}, only CMP leaks key-dependent information. No raw key access, input-dependent summary, timing leakage, semantic hash or uncharged preprocessing. All actual CMP calls count. Input-independent advice and arbitrary internal computation/storage are allowed for this query lower bound.

Let A be a randomized algorithm that, for every assignment of private keys, halts almost surely and answers duplicate existence correctly with probability one. Let Q_A(x,R) be its actual comparison count, possibly with infinite expectation. Then

    max_{π permutation} E_R Q_A(π,R) ≥ log2(n!).

Consequently a uniform expected query budget c*n+q0 cannot solve this task for all sufficiently large n, even with Las Vegas randomness. This is an expected-query claim, not a RAM-time or practical-resource claim.

### Proof

1. The full assignment universe has n^n elements, hence is finite. For each assignment, the set of random tapes on which A halts correctly has measure one. Intersect those finitely many sets. The resulting set G still has measure one. This step requires correctness on duplicate assignments too, not merely on permutations.
2. Fix R in G. A becomes a deterministic correct halting protocol on every assignment. On a permutation, all comparisons between distinct handles are strict; self-comparisons are deterministic and may be omitted from the decision transcript without increasing its length. If the resulting strict partial order is not total, merge incomparable handles and topologically label the quotient DAG by distinct integers in {0,...,n−1}. This produces a duplicate assignment preserving every observed strict answer. The fixed algorithm would follow the same path and output no duplicate, a contradiction.
3. Thus each permutation's negative terminal path fixes a unique total order. The n! permutation transcripts are distinct binary prefix-free codewords. If their informative lengths are d_π, Kraft gives Σ_π 2^(−d_π)≤1. Jensen yields (Σ_π d_π)/n!≥log2(n!). Actual CMP counts are at least these informative lengths.
4. Average over random tapes. Finite summation and nonnegative expectations commute, including infinite expectations. Hence the average over permutations of E_R Q_A(π,R) is at least log2(n!), and at least one permutation attains that lower bound.

This argument fixes the random tape externally; it does not pretend its cursor, seed, or random storage is free in a physical implementation. Since the lower bound allows arbitrary internal resources already, charging those cannot weaken it.

## What this does not establish

- It does not show every input has expected cost ≥log2(n!). The hard permutation may depend on the algorithm.
- It does not justify rounding the expectation up to ceil(log2(n!)); expected costs need not be integers. At n=9 it still excludes expected Q≤18 because 9!>2^18.
- It does not extend by fixing coins to Monte Carlo algorithms with error 1/3: correctness sets now need not have a measure-one intersection, and a particular tape may misclassify merged duplicate assignments. A bounded-error comparison lower bound would need a separate distributional/adversary argument.
- It does not turn an ND existential witness into a fast randomized search strategy. ND can guess a colliding pair and verify with one CMP, with address/CPU/state costs charged separately; uniformly random guesses may miss a unique colliding pair with probability 1−1/binom(n,2).
- Raw integer keys invalidate the information-interface premise. In the specified bounded universe a deterministic seen-bitset uses n bits plus indexing state and O(n) word operations, if those resources and word access are allowed. This is a protocol escape, not a contradiction to the theorem. The model must not hide reference-visible raw keys just to preserve a lower bound.
- No empirical reality-coverage, uniform reference domination, numerical full Γ profile, standard P/NP separation, or ZFC unprovability has been established.

## Actual finite checks

`probe_c63.py` uses only the Python standard library. Clean environment execution with `/run/current-system/sw/bin/python3` returned exit 0; results are in `c63-tests.json`. For insertion-sort-with-early-duplicate-detection, n=1..6 gave exactly n! distinct prefix-free negative transcripts, exact rational Kraft sum 1, and mean comparisons respectively 0, 1, 8/3, 59/12, 463/60, 221/20. The entropy inequality was checked by exact integer exponentiation, not floating-point tolerance. All key assignments at n=1..4 (1+4+27+256=288 cases) matched duplicate truth.

Probe SHA256: `4fac9a2921f8b485c84137134f0022429c2ffb287d6d570976ddd3c3fa4642a2`.

These tests sanity-check a finite implementation, not all randomized algorithms or the general theorem. They do not constitute independent review. Stable shared consumption is through board node C63 and its immutable published evidence, not this worker's mutable development directory.

## Remaining concrete obligations

1. Independent review of the finite-universe measure-one intersection and prefix-code argument.
2. A separate bounded-error opaque comparison proof if that stronger class is desired; do not infer it from this checkpoint.
3. A pre-frozen real task interface showing that CMP-only access is native rather than an artificial removal of raw/reference capabilities.
4. Full same-budget CPU/storage/address accounting and real-distribution evidence before any T3-v2 acceptance.
