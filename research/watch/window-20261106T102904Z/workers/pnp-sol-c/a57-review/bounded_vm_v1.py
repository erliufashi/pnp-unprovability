"""Research-only nondeterministic extension of bounded word-RAM; no benchmark coverage claim.
Run: python3 bounded_vm_v1.py --self-test
Counters specify abstract VM charges, not measured host CPU or resident memory.
"""
import argparse
import hashlib
import json
from dataclasses import dataclass


def canonical(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True).encode()


@dataclass(frozen=True)
class Envelope:
    steps: int
    memory_words: int
    description_bytes: int
    output_words: int
    word_bits: int = 32


class Trap(Exception):
    pass


def run(code, inputs, env, data=(), choices=()):
    """Input and data words must fit w; no free oversized integer operands."""
    if env.word_bits < 1 or any(v < 0 for v in (
        env.steps, env.memory_words, env.description_bytes, env.output_words
    )):
        raise ValueError("invalid envelope")
    mask = (1 << env.word_bits) - 1
    if len(code) > mask or env.memory_words > mask or len(inputs) > mask or len(data) > mask:
        raise ValueError("word address range exceeded")
    if any(type(x) is not int or not 0 <= x <= mask for x in (*inputs, *data)):
        raise ValueError("input/data not w-bit words")
    packed = canonical(code)
    data_bytes = (len(data) * env.word_bits + 7) // 8
    description = len(packed) + data_bytes
    choice_stream = iter(choices)
    stats = dict(choice_bits=0, steps=0, description_bytes=description,
                 memory_words=env.memory_words, register_words=16,
                 init_write_bits=(env.memory_words + 16) * env.word_bits,
                 input_reads=0, data_reads=0, memory_reads=0, memory_writes=0,
                 output_words=0, code_fetch_bytes=0, bit_charge=0)
    result = dict(status="", output=[], stats=stats,
                  code_sha256=hashlib.sha256(packed).hexdigest())
    if description > env.description_bytes:
        result["status"] = "description_limit"
        return result
    mem = [0] * env.memory_words
    regs = [0] * 16
    pc = 0

    def r(i):
        if type(i) is not int or not 0 <= i < 16:
            raise Trap("register")
        return regs[i]

    def put(i, value):
        r(i)
        regs[i] = value & mask

    def addr(i, size):
        a = r(i)
        if not 0 <= a < size:
            raise Trap("address")
        return a

    try:
        while True:
            if not 0 <= pc < len(code):
                raise Trap("pc")
            if stats["steps"] == env.steps:
                result["status"] = "fuel_limit"
                return result
            ins = code[pc]
            if not isinstance(ins, (list, tuple)) or not ins:
                raise Trap("instruction")
            op, *args = ins
            stats["steps"] += 1
            fetch = len(canonical(ins))
            stats["code_fetch_bytes"] += fetch
            # Conservative declared charge: instruction fetch plus all word ops.
            stats["bit_charge"] += 8 * fetch + (env.word_bits ** 2 if op == "MUL" else 8 * env.word_bits)
            pc += 1
            if op == "CONST":
                d, v = args
                if type(v) is not int or not 0 <= v <= mask:
                    raise Trap("constant")
                put(d, v)
            elif op == "GUESSBIT":
                (d,) = args
                try:
                    bit = next(choice_stream)
                except StopIteration:
                    raise Trap("choice exhausted")
                if type(bit) is not int or bit not in (0, 1):
                    raise Trap("choice bit")
                put(d, bit)
                stats["choice_bits"] += 1
            elif op == "MOV":
                d, a = args
                put(d, r(a))
            elif op in ("ADD", "SUB", "MUL", "LT", "EQ"):
                d, a, b = args
                av, bv = r(a), r(b)
                value = {"ADD": lambda: av + bv, "SUB": lambda: av - bv,
                         "MUL": lambda: av * bv, "LT": lambda: int(av < bv),
                         "EQ": lambda: int(av == bv)}[op]()
                put(d, value)
            elif op == "INPUT":
                d, a = args
                value = inputs[addr(a, len(inputs))]
                stats["input_reads"] += 1
                put(d, value)
            elif op == "DATA":
                d, a = args
                value = data[addr(a, len(data))]
                stats["data_reads"] += 1
                put(d, value)
            elif op == "LOAD":
                d, a = args
                value = mem[addr(a, len(mem))]
                stats["memory_reads"] += 1
                put(d, value)
            elif op == "STORE":
                a, s = args
                mem[addr(a, len(mem))] = r(s)
                stats["memory_writes"] += 1
            elif op == "OUT":
                (a,) = args
                if len(result["output"]) == env.output_words:
                    result["status"] = "output_limit"
                    return result
                result["output"].append(r(a))
                stats["output_words"] += 1
            elif op == "JZ":
                a, target = args
                if type(target) is not int:
                    raise Trap("target")
                if r(a) == 0:
                    pc = target
            elif op == "JMP":
                (target,) = args
                if type(target) is not int:
                    raise Trap("target")
                pc = target
            elif op == "HALT":
                if args:
                    raise Trap("arity")
                result["status"] = "halt"
                return result
            else:
                raise Trap("opcode")
    except (Trap, ValueError, TypeError) as exc:
        result["status"] = "trap:" + str(exc)
        return result


# Input [n, x_0,...,x_(n-1)], modulo 2^w. Native re-readable input.
SUM = [["CONST", 0, 0], ["INPUT", 1, 0], ["CONST", 2, 1],
       ["CONST", 3, 0], ["CONST", 4, 0], ["LT", 5, 3, 1],
       ["JZ", 5, 13], ["ADD", 6, 3, 2], ["INPUT", 7, 6],
       ["ADD", 4, 4, 7], ["ADD", 3, 3, 2], ["JMP", 5],
       ["HALT"], ["OUT", 4], ["HALT"]]
# Input [n, a_0,b_0,...], dot product modulo 2^w.
DOT = [["CONST", 0, 0], ["INPUT", 1, 0], ["CONST", 2, 1],
       ["CONST", 3, 0], ["CONST", 4, 0], ["CONST", 8, 2],
       ["LT", 5, 3, 1], ["JZ", 5, 19], ["MUL", 6, 3, 8],
       ["ADD", 6, 6, 2], ["INPUT", 7, 6], ["ADD", 6, 6, 2],
       ["INPUT", 9, 6], ["MUL", 10, 7, 9], ["ADD", 4, 4, 10],
       ["ADD", 3, 3, 2], ["JMP", 6], ["HALT"], ["HALT"],
       ["OUT", 4], ["HALT"]]
# Copies x into charged writable memory, reads it twice and outputs x+x.
REREAD = [["CONST", 0, 0], ["INPUT", 1, 0], ["STORE", 0, 1],
          ["LOAD", 2, 0], ["LOAD", 3, 0], ["ADD", 4, 2, 3],
          ["OUT", 4], ["HALT"]]


def self_test():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    standard = Envelope(1000, 8, 20000, 8, 16)
    for xs in ([], [7], [65535, 3], list(range(25))):
        out = run(SUM, [len(xs), *xs], standard)
        check("sum:" + str(len(xs)), out["status"] == "halt" and out["output"] == [sum(xs) & 65535])
    for pairs in ([], [(2, 3)], [(65535, 5), (13, 17)], [(i, i+1) for i in range(15)]):
        inp = [len(pairs)] + [v for pair in pairs for v in pair]
        out = run(DOT, inp, standard)
        check("dot:" + str(len(pairs)), out["status"] == "halt" and out["output"] == [sum(a*b for a,b in pairs) & 65535])
    baseline = run(SUM, [3, 2, 3, 5], standard)
    exact = Envelope(baseline["stats"]["steps"], 8, len(canonical(SUM)), 1, 16)
    check("native-identical-envelope", run(SUM, [3, 2, 3, 5], exact)["output"] == [10])
    short = Envelope(exact.steps - 1, 8, exact.description_bytes, 1, 16)
    check("one-less-fuel-fails", run(SUM, [3, 2, 3, 5], short)["status"] == "fuel_limit")
    check("code-not-free", run(SUM, [0], Envelope(1000, 8, len(canonical(SUM))-1, 1, 16))["status"] == "description_limit")
    data_code = [["CONST", 0, 0], ["DATA", 1, 0], ["OUT", 1], ["HALT"]]
    code_len = len(canonical(data_code))
    check("data-not-free", run(data_code, [], Envelope(10, 0, code_len+1, 1, 16), [42])["status"] == "description_limit")
    check("data-paid", run(data_code, [], Envelope(10, 0, code_len+2, 1, 16), [42])["output"] == [42])
    rr = run(REREAD, [123], standard)
    check("external-memory-reread", rr["output"] == [246] and rr["stats"]["memory_reads"] == 2 and rr["stats"]["memory_writes"] == 1)
    check("memory-bound", run(REREAD, [123], Envelope(100, 0, 20000, 1, 16))["status"].startswith("trap:"))
    check("output-bound", run(SUM, [0], Envelope(100, 8, 20000, 0, 16))["status"] == "output_limit")
    check("word-data-bound", rejects(lambda: run(SUM, [65536], standard)))
    check("bad-register-traps", run([["OUT", 99]], [], standard)["status"].startswith("trap:"))
    # Exhaust all two-word vectors at 4-bit precision.
    for x in range(16):
        for y in range(16):
            result = run(SUM, [2,x,y], Envelope(100, 0, 20000, 1, 4))
            # A 4-bit PC cannot address this 15-instruction program? 15 <= 15 is legal.
            if result["output"] != [(x+y) & 15] or result["status"] != "halt":
                raise AssertionError((x,y,result))
    checks.append("exhaustive-256-modular-sums")
    return {"status": "pass", "checks": checks, "check_count": len(checks),
            "coverage_claim": False, "example_trace": baseline}


def rejects(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; this is a research specification, not an installed service")
    print(json.dumps(self_test(), indent=2))

