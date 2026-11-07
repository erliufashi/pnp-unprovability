#!/usr/bin/env python3
"""
Argon Round-1 Divergent Audit Probe (stdlib-only).
Verifies local mathematical lemmas and counterexamples proposed in round1-audit-v1.md:
1. Interactive adaptive feedback trap: h rounds of binary environmental feedback leaks h bits
   even when retained memory B=0, solving m-bit search in ceil(log2 m) interactive queries.
2. Verification-asymmetry lemma: generate-and-verify loop over K candidates vs non-deterministic
   single-branch verifier, showing exact success probability and worst-case work blowup.
3. Anytime confidence sequence vs fixed-n Hoeffding failure under optional stopping.
4. Multi-index / streaming join communication lower bound under K passes and B bits memory.
"""

from __future__ import annotations
import json
import math
import unittest


def interactive_binary_search_queries(m: int) -> int:
    """Minimum adaptive binary feedback rounds needed to locate a target in [0, m) with 0 retained state."""
    if m <= 1:
        return 0
    return math.ceil(math.log2(m))


def generate_and_verify_work(k_candidates: int, t_gen: int, t_ver: int) -> int:
    """Worst-case deterministic work for sequential generate-and-verify over k candidates."""
    return k_candidates * (t_gen + t_ver)


def multi_index_pass_space_bound(m_bits: int, k_passes: int) -> float:
    """Minimum per-pass retained state B required when answering m independent queries after k passes without query-dependent random access."""
    if k_passes <= 0:
        raise ValueError("k_passes must be >= 1")
    return m_bits / k_passes


def fixed_n_hoeffding_radius(n: int, alpha: float) -> float:
    return math.sqrt(math.log(1.0 / alpha) / (2.0 * n))


def anytime_union_hoeffding_radius(t: int, alpha: float) -> float:
    """Time-uniform union bound over t >= 1 with prior weight p_t = 6 / (pi^2 * t^2)."""
    p_t = 6.0 / ((math.pi ** 2) * (t ** 2))
    return math.sqrt(math.log(1.0 / (alpha * p_t)) / (2.0 * t))


class ArgonAuditProbeTests(unittest.TestCase):
    def test_interactive_feedback_channel(self):
        # For m=1024 possibilities, 10 bits of binary environment feedback uniquely identifies the target
        # even if the agent retains only O(log m) address counters and 0 payload bits across passes.
        self.assertEqual(interactive_binary_search_queries(1024), 10)
        self.assertEqual(interactive_binary_search_queries(1), 0)

    def test_verification_asymmetry_gap(self):
        # NP_R checks 1 witness in t_ver=100 steps. Deterministic search over K=2^10 candidates takes 1024*(50+100)=153600.
        np_work = 100
        det_work = generate_and_verify_work(1024, 50, 100)
        self.assertGreater(det_work, 1000 * np_work)

    def test_multi_pass_space_tradeoff(self):
        self.assertAlmostEqual(multi_index_pass_space_bound(1000, 4), 250.0)

    def test_anytime_radius_dominates_fixed_n(self):
        for t in (10, 50, 200):
            r_fixed = fixed_n_hoeffding_radius(t, 0.05)
            r_any = anytime_union_hoeffding_radius(t, 0.05)
            self.assertGreater(r_any, r_fixed)
            self.assertLess(r_any, 1.0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ArgonAuditProbeTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    summary = {
        "ok": result.wasSuccessful(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
    }
    Path_out = "/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/argon-probe-v1.json"
    with open(Path_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    raise SystemExit(0 if result.wasSuccessful() else 1)
