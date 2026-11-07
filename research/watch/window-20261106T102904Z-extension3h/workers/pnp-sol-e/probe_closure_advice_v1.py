#!/usr/bin/env python3
"""Finite negative controls for E-CLOSURE-ADVICE-1. Stdlib only; fail nonzero."""
import json
from collections import Counter
from fractions import Fraction
from itertools import product


def pguess(rows, obs):
    counts = Counter((tuple(row[i] for i in obs), row[0]) for row in rows)
    groups = {}
    for (v, y), count in counts.items():
        groups[v] = max(groups.get(v, 0), count)
    return Fraction(sum(groups.values()), len(rows))


def main():
    xor = []
    for m in range(1, 9):
        n = 1 << m
        rows = [(y, r, y ^ r) for y in range(n) for r in range(n)]
        base = pguess(rows, [])
        assert base == pguess(rows, [1]) == pguess(rows, [2]) == Fraction(1, n)
        assert pguess(rows, [1, 2]) == 1
        xor.append({'m': m, 'rows': len(rows), 'single_guess': str(base), 'joint_guess': '1'})
    # Enumerate ALL deterministic leaks of alphabet K, not just one chosen function.
    capacity_cases = 0
    for n in range(1, 6):
        for k in range(1, 4):
            for weights in (tuple(range(1, n + 1)), (1,) * n):
                base = Fraction(max(weights), sum(weights))
                for f in product(range(k), repeat=n):
                    rows = [(y, f[y]) for y in range(n) for _ in range(weights[y])]
                    assert pguess(rows, [1]) <= min(1, k * base)
                    capacity_cases += 1
    # Tight d-bit selective-code/advice example, including d=0 and full disclosure.
    tight_cases = 0
    for m in range(1, 9):
        n = 1 << m
        for d in range(m + 1):
            rows = [(y, y >> (m - d)) for y in range(n)]
            assert pguess(rows, [1]) == Fraction(1 << d, n)
            tight_cases += 1
    # Finite semantic constant class: all bitstrings length <= b. Each component
    # is admitted, but concatenating two length-b outputs exits for every b>=1.
    closure = []
    for b in range(1, 13):
        a = '0' * b
        assert len(a) <= b and len(a + a) > b
        # Generic finite code-count obstruction: <=d-bit raw codes have <2^(d+1)
        # possibilities, whereas strings of exact length d+1 have 2^(d+1).
        assert sum(1 << i for i in range(b + 1)) < 1 << (b + 1)
        closure.append(b)
    # Adaptive safe kernel: outputs depend on public v and fresh coins only.
    safe = [(y, v, v ^ r, (v ^ r) ^ s)
            for y, v, r, s in product(range(2), repeat=4)]
    assert pguess(safe, [1, 2, 3]) == pguess(safe, [1])
    print(json.dumps({'status': 'pass', 'xor_cases': xor,
                      'capacity_exhaustive_maps': capacity_cases,
                      'tight_code_selection_cases': tight_cases,
                      'finite_closure_cases': closure,
                      'safe_kernel_rows': len(safe),
                      'limits': 'finite controls only; no implementation compiler, physical budget or real coverage certification'}, indent=2))


if __name__ == '__main__':
    main()
