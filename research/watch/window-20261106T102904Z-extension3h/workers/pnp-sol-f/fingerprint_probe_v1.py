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
