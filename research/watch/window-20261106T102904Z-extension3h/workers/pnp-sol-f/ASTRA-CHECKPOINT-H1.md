# F-DYN-FP-1 — hidden-seed dynamic fingerprints

Owner: pnp-sol-f. Checkpoint: 2026-11-06 23:49 +08. Classification: conditional local theorem and interface counterexamples; independent acceptance pending. Standard T1/T2 and current T3-v2 remain UNRESOLVED.

## Contract and novelty

Current contract: `alternatives/practical-core/research/current-contract-v2.json`, revision 2. Board node F-DYN-FP-1 was already registered and leased to this owner on inspection; this checkpoint completes that node rather than making a duplicate. Its distinct target is adaptive Boolean feedback with a fixed hidden seed, not B56/B57's dynamic OR capacity or a general element-distinctness lower bound. Legacy controller's T3 success is historical qualified proxy only.

No old proof or protected file was edited. Shared publication uses board_v1.py only. Mail is manually claimed, paused/followUp/60. This is an early bounded checkpoint, not a running service or renewed research lease. No agents launched. Requested model is gateway_responses/gpt-6-astra:max; this artifact does not independently certify runtime routing. User requested 2026-11-07 04:00 +08 stop, while inherited developer cutoff is earlier; this checkpoint ends before either, without extending authorization.

## Interface

Fix prime p and N>=1. The logical vector a is in F_p^N, initially zero (or built by a complete scan). Sample one uniform r in F_p independently of client inputs and client coins. Maintain s = sum_{i=0}^{N-1} a_i r^i. An additive update (i,delta) changes s by delta*r^i and the logical coordinate by delta. Boolean query returns [s=0]. No raw sketch, seed, timing, trace, cache, address pattern or other seed-dependent observation is exposed. Updates produce no such feedback. The client may remember its updates and adapt to prior Boolean replies. At most K queries are allowed. Correct answer means vector zero over F_p, not integer zero.

## Exact first-error probability

Over all such clients, the maximum probability of at least one wrong Boolean answer is

    min(1, K(N-1)/p).

For N=1 this is zero. This is a first-error statement, not a claim that each query conditioned on past replies still has error <=(N-1)/p.

Proof: fix client coins. Run the client against the ideal exact zero-vector oracle. This defines a single seed-independent sequence of vectors up to K queries. Before the first discrepancy the actual and ideal interactions coincide, including all updates and stopping decisions. Zero vectors never cause errors. Every nonzero query vector defines a nonzero polynomial of degree at most N-1 and hence at most min(p,N-1) roots. A first error therefore implies r belongs to the union of the root sets on the ideal transcript. Union size is at most min(p,K(N-1)). Divide by p and average over client coins. This avoids the invalid assertion that posterior seeds remain uniformly distributed over the entire field.

Tightness: partition up to min(p,K(N-1)) field elements into at most K blocks of size <=N-1. Query the coefficient vector of the monic product over each block of (X-u), padded to N coordinates. Each is nonzero and its field roots are precisely its block. Arbitrary additive updates can move between these vectors. Thus the union of erroneous seeds is exactly that many elements. If N-1>=p, X^p-X already vanishes on every seed but is a nonzero coefficient vector. For N=1 use a nonzero constant; there are no roots. This strategy requires unrestricted legal update counts; a stricter update/time budget can reduce attainability, though not invalidate the upper bound.

## Two-coordinate counterexamples

For N>=2, public r permits the nonzero vector (-r,1,0,...) with sketch zero, so failure probability is one in one Boolean test. If r is hidden but raw s is available, first set a=(0,1,0,...); its raw sketch equals r. Then update coordinate 0 by -r. The same nonzero zero-sketch vector results. This needs one raw read, not a cryptographic attack. It cannot be applied to a Boolean-only interface without paying for information gathering. Repeated Boolean tests nevertheless eventually cover all p seeds, as above.

Semantics matter: an integer coordinate equal to p is nonzero over the integers but zero in F_p. The theorem is not an integer-zero service without additional magnitude/modulus conditions.

## Full resource ledger

- Initial construction from an existing vector requires reading all N field elements. Horner evaluation takes O(N) field operations and O(log p) arithmetic working bits beyond input/access counters. Starting from the specified zero vector avoids this scan, not arbitrary-input acquisition.
- Persistent server summary contains r and s (2 ceil(log2 p) bits), plus finite control and parameters. Update index requires ceil(log2 N) bits; arithmetic temporaries are additional O(log p) bits. Uniform field sampling has entropy log2 p; rejection sampling uses an expected finite bit budget, not a fixed worst-case bound.
- With no stored power table, exponentiation for an update costs O(log N) field multiplications and O(log N+log p) working bits. These are field-operation bounds, not unit-cost bit arithmetic claims. A table of all powers costs N field elements and must be charged if used.
- Boolean query costs a field-zero comparison. No scan is needed per query under the trusted summary invariant.
- An assignment update requires the old coordinate or a charged data store/lookup to derive delta. The small summary alone does not supply arbitrary old coordinates. Client storage of the logical vector and its update history is not included in server-summary memory; any complete system budget must include it separately.
- Changing r cannot in general reconstruct the new sketch from the old scalar. Rebuild needs the original vector, sufficient retained state, or replay of the complete update log, and corresponding read/time/storage cost. Refresh is not free.
- Hidden seed is an interface assumption, not an empirically verified side-channel guarantee. Probe Python code is not a constant-time service.

## Reproducible finite audit

Local probe `fingerprint_probe_v1.py`, Python 3 standard library; no installation or dependencies. From this directory run `python3 fingerprint_probe_v1.py`; stdout is JSON and any failed assertion exits nonzero. Checked primes 2,3,5,7; N up to 4 (with N<=p+1); K=0..4. Exhaustive polynomial root sets plus dynamic programming over remaining seeds validate the adaptive no-error-branch optimum. Separate checks enumerate additive transitions and raw attacks.

Recorded results in `fingerprint-probe-v1.json`: 3,699 nonzero polynomials; 75 exact-capacity cases; 150 root-cover construction steps; 67,370 update transitions; 17 raw-read attacks. All passed. This finite check corroborates, not replaces, the proof. The theorem is self-contained and uses only the elementary polynomial root bound.

## Consequence and remaining obligation

The hidden Boolean API supports adaptive reuse with a finite query budget, while public/raw APIs admit immediate forgery. For target error epsilon>0, p>=K(N-1)/epsilon suffices, increasing stored field width and arithmetic cost. Therefore a fixed hidden sketch cannot be transferred to an unrestricted transparent dynamic-index model without separately proving the observation boundary and charging refresh/retained-state costs.

This does not prove general randomized BRAM separation, capability-preserving realistic coverage, or a side of standard P/NP unprovable in ZFC. The local proof and finite audit complete this node's scoped work; independent review and an accepted physical/interface implementation remain external obligations. No new empirical human/LLM coverage or T3-v2 certificate is claimed.
#!/usr/bin/env python3
"""Finite exhaustive audit of hidden-seed dynamic zero fingerprints; stdlib only.
Run: python3 fingerprint_probe_v1.py. Prints JSON; assertion failure exits nonzero.
This is a mathematical probe, NOT a constant-time or cryptographic service.
"""
import itertools
import json
from functools import lru_cache


def evaluate(a, r, p):
    value = 0
    for coefficient in reversed(a):
        value = (value * r + coefficient) % p
    return value


def polynomial_with_roots(roots, p):
    a = [1]
    for root in roots:
        b = [0] * (len(a) + 1)
        for i, coefficient in enumerate(a):
            b[i] = (b[i] - root * coefficient) % p
            b[i + 1] = (b[i + 1] + coefficient) % p
        a = b
    return a


def main():
    counts = {"polynomials": 0, "optimal_capacity_cases": 0,
              "dynamic_update_transitions": 0, "raw_leak_attacks": 0,
              "root_cover_constructions": 0}
    capacity = []
    for p in (2, 3, 5, 7):
        for n in range(1, min(4, p + 1) + 1):
            d = n - 1
            root_masks = set()
            for a in itertools.product(range(p), repeat=n):
                if not any(a):
                    continue
                mask = sum(1 << r for r in range(p) if evaluate(a, r, p) == 0)
                assert mask.bit_count() <= d
                root_masks.add(mask)
                counts["polynomials"] += 1
            # No-error branch of any adaptive strategy: zero-vector tests give
            # no failure and no seed information; a nonzero-vector test fails
            # on precisely its roots. Remaining seeds take its nonzero branch.
            @lru_cache(None)
            def optimum(remaining, k):
                if not remaining or not k:
                    return 0
                return max((remaining & roots).bit_count() +
                           optimum(remaining & ~roots, k - 1)
                           for roots in root_masks)
            for k in range(5):
                actual = optimum((1 << p) - 1, k)
                assert actual == min(p, k * d), (p, n, k, actual)
                covered = set()
                for j in range(k):
                    roots = list(range(j * d, min((j + 1) * d, p)))
                    a = polynomial_with_roots(roots, p)
                    assert len(a) <= n and any(a)
                    covered.update(r for r in range(p) if evaluate(a, r, p) == 0)
                    counts["root_cover_constructions"] += 1
                assert len(covered) == actual
                counts["optimal_capacity_cases"] += 1
                capacity.append({"p": p, "N": n, "K": k,
                                 "bad_seeds": actual, "total_seeds": p})
        for n in range(1, 4):
            for a in itertools.product(range(p), repeat=n):
                for r in range(p):
                    s = evaluate(a, r, p)
                    for i in range(n):
                        for delta in range(p):
                            b = list(a)
                            b[i] = (b[i] + delta) % p
                            updated = (s + delta * pow(r, i, p)) % p
                            assert updated == evaluate(b, r, p)
                            if not any(b):
                                assert updated == 0  # no false negatives
                            counts["dynamic_update_transitions"] += 1
        for r in range(p):
            # Querying raw sketch of x reveals r. Update coordinate zero -r.
            assert evaluate([0, 1], r, p) == r
            forged = [-r % p, 1]
            assert any(forged) and evaluate(forged, r, p) == 0
            counts["raw_leak_attacks"] += 1
        # Integer-vs-field semantic negative control: never claim integer zero.
        assert evaluate([p], 0, p) == 0 and [p] != [0]
    print(json.dumps({"ok": True, "probe_version": 1, "counts": counts,
                      "capacity_cases": capacity,
                      "scope": "finite algebra/model audit, no physical side-channel assurance"},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

```

## Appendix B — machine-readable result summary

```json
{
  "counts": {
    "dynamic_update_transitions": 67370,
    "optimal_capacity_cases": 75,
    "polynomials": 3699,
    "raw_leak_attacks": 17,
    "root_cover_constructions": 150
  },
  "ok": true,
  "probe_version": 1,
  "scope": "finite algebra/model audit, no physical side-channel assurance"
}
```

Source SHA256: `2d7c7022376b372632ce48b54b58101cbf23af88c92fbbc37f423e770a888f26`. Full per-case output is deterministically regenerated by the embedded source.
