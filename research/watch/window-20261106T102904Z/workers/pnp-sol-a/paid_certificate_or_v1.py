"""Semantic smoke tests; enumeration is NOT nondeterministic execution time."""
import hashlib
import itertools
import json
from pathlib import Path
from bounded_vm_v1 import Envelope, canonical, run, SUM
from bounded_vm_nd_v1 import run as run_nd

CERT_OR = [
    ["CONST", 0, 0], ["INPUT", 1, 0], ["DATA", 2, 0],
    ["LT", 3, 2, 1], ["JZ", 3, 10], ["CONST", 4, 1],
    ["ADD", 2, 2, 4], ["INPUT", 5, 2], ["OUT", 5], ["HALT"],
    ["OUT", 0], ["HALT"]
]
OR_SCAN = [
    ["CONST", 0, 0], ["INPUT", 1, 0], ["CONST", 2, 1],
    ["CONST", 3, 0], ["LT", 5, 3, 1], ["JZ", 5, 13],
    ["ADD", 6, 3, 2], ["INPUT", 7, 6], ["JZ", 7, 10],
    ["JMP", 15], ["ADD", 3, 3, 2], ["JMP", 4], ["HALT"],
    ["OUT", 0], ["HALT"], ["OUT", 7], ["HALT"]
]


ND_OR = [
    ["CONST", 9, 0], ["CONST", 10, 1], ["CONST", 11, 2],
    ["GUESSBIT", 12], ["MUL", 9, 9, 11], ["ADD", 9, 9, 12],
    ["MUL", 10, 10, 11], ["JZ", 10, 9], ["JMP", 3],
] + [list(ins) for ins in CERT_OR]
ND_OR[11] = ["MOV", 2, 9]
ND_OR[13] = ["JZ", 3, 19]


def test():
    cases = 0
    witnesses_checked = 0
    for n in range(9):
        w = max(5, (n + 1).bit_length())
        env = Envelope(10, 0, 10000, 1, w)
        for bits in itertools.product((0, 1), repeat=n):
            accepted = False
            # All w-bit certificates, including out-of-range and maximal word.
            for j in range(1 << w):
                result = run(CERT_OR, [n, *bits], env, [j])
                ok = result["status"] == "halt" and result["output"] == [1]
                accepted = accepted or ok
                if result["stats"]["steps"] > 10:
                    raise AssertionError("verifier fuel")
                if ok != (j < n and bits[j] == 1):
                    raise AssertionError((n, bits, j, result))
                nd = run_nd(ND_OR, [n, *bits], Envelope(6*w+12, 0, 10000, 1, w),
                            choices=[(j >> b) & 1 for b in range(w-1,-1,-1)])
                nd_ok = nd["status"] == "halt" and nd["output"] == [1]
                if nd_ok != ok or nd["stats"]["choice_bits"] != w:
                    raise AssertionError(("nd",n,bits,j,nd))
                if j < n and nd["stats"]["steps"] != 6*w+12:
                    raise AssertionError("paid generation fuel")
                witnesses_checked += 1
            if accepted != any(bits):
                raise AssertionError("existential semantics")
            scan = run(OR_SCAN, [n, *bits], Envelope(7*n+8, 0, 10000, 1, w))
            if scan["status"] != "halt" or scan["output"] != [int(any(bits))]:
                raise AssertionError(("scan", n, bits, scan))
            cases += 1
    n = 64
    w = max(5, (n + 1).bit_length())
    zero = run(OR_SCAN, [n, *([0] * n)], Envelope(7*n+8, 0, 10000, 1, w))
    if zero["stats"]["steps"] != 7*n+8:
        raise AssertionError("worst-case scan formula")
    return {"status": "pass", "input_cases": cases,
            "witness_paths_checked": witnesses_checked,
            "generation_steps_per_path": "6w+2, including w GUESSBIT instructions and packing/loop",
            "certificate_storage_bits": "w in register 9, within charged 16w-bit register file; direct verifier variant additionally charges data bytes",
            "max_verifier_steps": 10,
            "nd_code_bytes": len(canonical(ND_OR)),
            "nd_total_steps_per_valid_path": "6w+12",
            "existential_not_physical_solver": True,
            "reality_coverage": False,
            "source_vm_sha256": hashlib.sha256(Path('bounded_vm_v1.py').read_bytes()).hexdigest(),
            "certificate_code_bytes": len(canonical(CERT_OR)),
            "scan_code_bytes": len(canonical(OR_SCAN)),
            "sum_code_bytes": len(canonical(SUM)),
            "zero_scan_trace": zero}


if __name__ == "__main__":
    print(json.dumps(test(), indent=2))
