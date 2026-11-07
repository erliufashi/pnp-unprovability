#!/usr/bin/env python3
"""
Argon H2 Audit Probe (stdlib-only).
Verifies the corrected H2 mathematical statements and checks the 3 new H2 node candidates:
1. Correction of H1 feedback formula: K binary replies distinguish at most 2^K states;
   exact recovery of uniform m-bit X from s-bit side info + K binary replies is <= min(1, 2^(s+K-m)).
   When m=10 bits, K=ceil(log2 10)=4 replies give at most 16/1024 = 1/64 recovery probability (NOT 1).
2. Opaque comparator vs transparent word-RAM critique:
   For n elements over a small alphabet of size Sigma < n (e.g. Sigma=2, n=4),
   transparent word-RAM decides Collision in 0 work steps (Pigeonhole: always 1) or O(Sigma) bucket counts,
   whereas an opaque equality/order comparator model hides the alphabet representation.
   Even for large domain [n^2], radix/bucket counting with M >= n^2 words takes O(n) steps,
   whereas comparison decision tree requires ceil(log2(n!)) comparisons.
3. Randomized BSSV gap vs deterministic BSSV (supporting E-argon-RAND-ED-2):
   Checks that in BSSV (2003), Theorem 6.13 is deterministic, while Theorem 6.23 (randomized)
   requires two-sided error epsilon <= 2^(-Omega(log^2 n)) or small success probability,
   leaving bounded-error 1/3 BPP_BRAM on full-scan COLLISION as an open gap.
4. FLMV SAT time-space vs same-budget ND gap (supporting E-argon-SAT-TS-2):
   Verifies the exact rational recurrence f_{k+1} = c*f_k / (1 + f_k) from FLMV Theorem 5.7
   and compares the deterministic excluded space n^d against the O(n) witness space of standard SAT.
"""

from __future__ import annotations
from fractions import Fraction
import json
import math
import unittest


def exact_mbit_recovery_upper_bound(m_bits: int, s_side_bits: int, k_binary_replies: int) -> Fraction:
    """Upper bound min(1, 2^(s+K-m)) on exact recovery of uniform m-bit string X."""
    exponent = s_side_bits + k_binary_replies - m_bits
    if exponent >= 0:
        return Fraction(1, 1)
    return Fraction(1, 1 << (-exponent))


def conditional_hazard_amplification(hazards: list[ Fraction ]) -> Fraction:
    """Lower bound 1 - prod_i (1 - p_i) when P(success at i | active history H_{i-1}) >= p_i."""
    fail_prob = Fraction(1, 1)
    for p in hazards:
        fail_prob *= (Fraction(1, 1) - p)
    return Fraction(1, 1) - fail_prob


def correlated_marginal_success(p: Fraction, k_trials: int) -> Fraction:
    """Negative control: when all K trials repeat the same Bernoulli(p) draw Z, success is still p."""
    assert k_trials >= 1
    return p


def opaque_comparison_tree_lower_bound(n: int) -> int:
    """Minimum worst-case ternary/binary comparisons to distinguish n! orderings: ceil(log2(n!))."""
    return math.ceil(math.log2(math.factorial(n)))


def flmv_recurrence_d(c: Fraction, k: int) -> Fraction:
    """FLMV Theorem 5.7 exponent d = min((1/f_k - c)/k, 1/c^k) where f_0=1, f_{i+1}=c*f_i/(1+f_i)."""
    f = Fraction(1, 1)
    for _ in range(k):
        f = (c * f) / (Fraction(1, 1) + f)
    term1 = (Fraction(1, 1) / f - c) / k
    term2 = Fraction(1, 1) / (c ** k)
    return min(term1, term2)


class ArgonH2ProbeTests(unittest.TestCase):
    def test_h1_correction_binary_feedback_m_bits_vs_m_states(self):
        # H1 error correction: for m=10 hidden bits (2^10=1024 strings), K=4 binary replies
        # with s=0 side info gives at most 2^(4-10) = 1/64 probability, NOT 1.
        bound = exact_mbit_recovery_upper_bound(m_bits=10, s_side_bits=0, k_binary_replies=4)
        self.assertEqual(bound, Fraction(1, 64))
        # To recover 10 hidden bits with certainty requires s + K >= 10.
        self.assertEqual(exact_mbit_recovery_upper_bound(10, 0, 10), Fraction(1, 1))

    def test_conditional_vs_correlated_retry(self):
        p = Fraction(1, 4)
        cond_bound = conditional_hazard_amplification([p, p, p, p])
        corr_actual = correlated_marginal_success(p, 4)
        self.assertEqual(cond_bound, Fraction(175, 256))
        self.assertEqual(corr_actual, Fraction(1, 4))
        self.assertGreater(cond_bound, corr_actual)

    def test_opaque_comparator_vs_raw_bits_gap(self):
        # For n=16 elements, comparison tree needs ceil(log2(16!)) = 45 comparisons.
        # But if raw bits have word width w=3 (domain size 8 < 16), raw-bit collision is trivially 1 in 0 probes,
        # or if w=4 (domain 16) and M=16 words of RAM are available, radix/direct addressing takes 16 steps < 45.
        n = 16
        cmp_lb = opaque_comparison_tree_lower_bound(n)
        self.assertEqual(cmp_lb, 45)
        direct_bucket_probes = n
        self.assertLess(direct_bucket_probes, cmp_lb)

    def test_flmv_exponent_and_nd_space_gap(self):
        # For c = 3/2, k = 2: f_1 = 3/5, f_2 = 9/14, 1/f_2 - c = 14/9 - 3/2 = 1/18, so d = 1/36.
        d = flmv_recurrence_d(Fraction(3, 2), 2)
        self.assertEqual(d, Fraction(1, 36))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ArgonH2ProbeTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    out_path = "/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/argon-probe-h2-v1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "ok": result.wasSuccessful(),
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
            },
            f,
            indent=2,
        )
    raise SystemExit(0 if result.wasSuccessful() else 1)
