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




# Standalone full-scan collision experiment (host harness is not VM budget).
"""Research-only charged ND collision witness on the frozen abstract BRAM."""
import sys,itertools,json,math,hashlib
from pathlib import Path

def append_guess(code,target=9):
    b=len(code)
    code += [['CONST',target,0],['CONST',10,1],['CONST',11,2],
             ['GUESSBIT',12],['MUL',target,target,11],['ADD',target,target,12],
             ['MUL',10,10,11],['JZ',10,b+9],['JMP',b+3]]

ND_COLLISION=[]
append_guess(ND_COLLISION)
ND_COLLISION.append(['MOV',14,9])
append_guess(ND_COLLISION)
b=len(ND_COLLISION)
ND_COLLISION += [
 ['CONST',0,0],['INPUT',1,0],['LT',3,14,1],['JZ',3,b+17],
 ['LT',3,9,1],['JZ',3,b+17],['EQ',3,14,9],['JZ',3,b+9],['JMP',b+17],
 ['CONST',2,1],['ADD',4,14,2],['INPUT',5,4],['ADD',4,9,2],['INPUT',6,4],
 ['EQ',7,5,6],['OUT',7],['HALT'],['OUT',0],['HALT']]

def profile(n,small_test=False):
    w=(n*n+1).bit_length()
    if small_test:w=max(6,w)
    return Envelope(32*n+512,math.isqrt(n),4096,1,w)

def paid_run(code,inputs,e,choices=()):
    # Reserve zero initialization AND one full raw-input acquisition pass.
    # These are declared abstract word-work charges, not host CPU measurements.
    initialization=16+e.memory_words
    acquisition=len(inputs)
    execution=Envelope(e.steps-initialization-acquisition,e.memory_words,e.description_bytes,e.output_words,e.word_bits)
    return run(code,inputs,execution,choices=choices)

def branch(xs,i,j,small=False):
    n=len(xs);e=profile(n,small);w=e.word_bits
    choices=[(v>>b)&1 for v in (i,j) for b in range(w-1,-1,-1)]
    r=paid_run(ND_COLLISION,[n,*xs],e,choices=choices)
    expected=(i<n and j<n and i!=j and xs[i]==xs[j])
    assert (r['status']=='halt' and r['output']==[1])==expected,(n,i,j,r)
    assert r['stats']['choice_bits']==2*w
    if i<n and j<n and i!=j:assert r['stats']['steps']==12*w+21,r
    init_words=16+e.memory_words
    assert r['stats']['steps']+init_words+n+1<=e.steps
    bit_bound=init_words*w+e.steps*(8*e.description_bytes+8*w+w*w)
    assert r['stats']['init_write_bits']+r['stats']['bit_charge']+(n+1)*w<=bit_bound
    return expected

def test():
    checks=0;arrays=0
    for n in range(2,5):
        e=profile(n,True);addresses=list(range(n))+[n,(1<<e.word_bits)-1]
        for xs in itertools.product(range(3),repeat=n):
            accepted=False
            for i,j in itertools.product(addresses,repeat=2):
                accepted=branch(xs,i,j,True) or accepted;checks+=1
            assert accepted==(len(set(xs))<n)
            arrays+=1
    big=[]
    for n in (128,129,255,256,1024):
        e=profile(n);mask=(1<<e.word_bits)-1
        distinct=list(range(n));last_duplicate=distinct.copy();last_duplicate[-1]=0
        all_same=[0]*n
        addresses=sorted(set([0,1,n//2,n-1,n,mask]))
        for xs in (distinct,last_duplicate,all_same):
            for i,j in itertools.product(addresses,repeat=2):
                branch(xs,i,j);checks+=1
            r=paid_run(SUM,[n,*xs],e)
            assert r['status']=='halt' and r['output']==[sum(xs)&mask]
            assert r['stats']['steps']==7*n+9
            assert r['stats']['steps']+16+e.memory_words+n+1<=e.steps
            arrays+=1
        big.append({'n':n,'w':e.word_bits,'memory_words':e.memory_words,'fuel':e.steps,'valid_nd_steps':12*e.word_bits+21,'sum_steps':7*n+9})
    return {'status':'pass','arrays':arrays,'branch_runs':checks,'nd_code_bytes':len(canonical(ND_COLLISION)),'nd_instruction_count':len(ND_COLLISION),'nd_code_sha256':hashlib.sha256(canonical(ND_COLLISION)).hexdigest(),'fullscan_SUM_same_profile':True,'initialization_reserved_in_total_fuel':True,'full_input_acquisition_pass_reserved':True,'small_test_width_floor_6_not_asymptotic_claim':True,'large_profiles':big,'coverage_certified':False}

if __name__=='__main__':print(json.dumps(test(),indent=2))
