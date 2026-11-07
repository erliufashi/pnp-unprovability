# E-argon-FNS-audit1 — A full-scan-compatible BRAM D/ND separation candidate

pnp-sol-c, 2026-11-06. Classification: conditional local theorem candidate using an original-source branching-program lower bound, with explicit charged ND code and ordinary SUM inclusion. Independent review and finite-threshold certification outstanding. NOT accepted T3_v2 coverage or standard P/NP.

## 1. Main result, and what changed from OR
There is an explicit common bounded-word-RAM resource FUNCTION Γ(n) that:
1. permits a full input acquisition pass and the native full-array SUM routine;
2. has ordinary rereadable random-access input and charged mutable memory;
3. admits a fixed program that nondeterministically decides whether two array entries are equal, using two addresses generated one bit at a time and retained in normal registers;
4. excludes EVERY deterministic program for that predicate at all sufficiently large dimensions, conditional on the cited established BP theorem and the complete-state mapping below.

Unlike C56/A57 OR, this does not require forbidding a full input scan. The restriction enabling the result is linear WORD fuel together with sublinear retained storage in a general RAM-access model. This is not a claim that the chosen storage profile preserves most practical abilities.

## 2. Original source actually obtained
Paul Beame, Michael Saks, Xiaodong Sun, Erik Vee, *Time-space tradeoff lower bounds for randomized computation of decision problems*, author manuscript dated2002-10-24,40 pages; corresponding article JACM50(2),2003,154–195, DOI10.1145/636865.636867.

Obtained via the original author link cited by Fortnow's2004 exposition:
https://www.cs.washington.edu/homes/beame/papers/randomts.ps

Complete PostScript473208 bytes, sha256 `38f9bf0da43a21b4073278a24a4e9fade560562544a597818629383c1dc1295a`. Converted locally with an already-installed Ghostscript and pdftotext; no installation/configuration changes. Source files `bssv-randomts.ps`, `bssv-randomts.pdf`, `bssv-randomts.txt`; image `bssv-page32.png` visually verifies formula placement because text extraction displaced the square root. Partial initial download was resumed; only the complete document was used.

Read introduction, complete model§2.3 and the relevant deterministic/randomized element-distinctness sections§6.2 including Theorem6.13, Corollary6.14, and the separate small-error limitations of Theorem6.23/Corollary6.24. I did NOT independently reprove the full earlier embedded-rectangle machinery. The known theorem is a precisely scoped source premise, not accepted merely from a search summary.

**Theorem6.13, originalp32:** any `[n²]`-way deterministic branching program computing element distinctness on `[n²]^n`, with length T and TOTAL node-count size2^S, requires

`T = Omega(n * sqrt(log(n/S) / log log(n/S)))`.

The ENTIRE ratio is under the square root. This is not a comparison-only, streaming, monotone-pass or read-k result. Source§2.3 allows each node to select any input coordinate; it reads the entire value in the domain and branches on it. Source explicitly treats branching programs as stronger than RAM. The source's separate randomized ED theorem tolerates specific small-error regimes; I do NOT promote this deterministic result to a generic1/3-error randomized lower bound.

Define ED=1 when all entries are distinct. Its complement COLL=1 when some pair repeats. A deterministic BP for COLL can flip sink labels to decide ED with unchanged size/depth, so the same lower bound applies to COLL. Relabeling `[n²]` as `{0,...,n²-1}` is an isomorphism of the input alphabet and does not change the theorem.

## 3. Frozen common model/profile
Use the abstract BRAM opcodes audited in C58/A57:16 w-bit registers, bounded mutable word array, immutable random-access input, static code/data, word ADD/SUB/MUL/EQ/LT with arithmetic modulo2^w, conditional/direct jumps, one output word and HALT. ND adds GUESSBIT, returning one nondeterministic bit and costing one ordinary instruction; no readable proof tape or retained uncharged choice transcript.

For valid input `[n,x_0,...,x_(n-1)]`, n>=128 and x_i in{0,...,n²-1}, set

- `w(n)=ceil(log2(n²+2))`;
- mutable array `M(n)=floor(sqrt(n))` words;
- total word-work/fuel `F(n)=32n+512`;
- static program+data description bound `B=4096` bytes;
- output capacity one w-bit word;
- raw input residency `(n+1)w` bits, common to both sides, not writable workspace;
- zero initialization of16+M words charged BEFORE opcode execution;
- one entire raw-input acquisition pass of n+1 words also reserved BEFORE opcode execution.

Thus the interpreter's execution fuel is `F-(16+M)-(n+1)`, not an extra F after free initialization/acquisition. This full-pass reservation is an abstract word-I/O charge; host Python validation/allocation is NOT claimed to execute in these physical resource units.

All mutable tools/files/logs/caches must fit the same M-word array plus16 registers and charged finite control. No readback from output, mutation of raw input, hidden database or input-dependent initial advice. Static data may depend on n nonuniformly for the lower-bound overapproximation but not on x; the exhibited ND and SUM programs are fixed uniform code.

Track an additional conservative bit-work cap, for example

`Q(n)=(16+M)w + F*(8B+8w+w²)`.

Initialization contributes its actual bit writes, and raw acquisition contributes(n+1)w bits. Every instruction fetch has at most B bytes, word MUL is charged w², and other declared operations have at most8w charge, so this loose common cap includes the exhibited traces. Fuel and bit-work are SEPARATE coordinates. Dropping the linear word-fuel restriction and keeping only Q does not preserve the lower-bound conclusion: it could allow many more word instructions. This is a bounded-word-RAM result, not a bit-linear-time theorem.

The complete dynamic state includes register contents, ALL M word slots, addresses, PC, fuel/initialization/acquisition counters and observable resource guards, output-valid/accept flags and any persistent tool state. Passive diagnostic Python counters/log objects are not advertised as physical small-memory implementation; if exposed to the modeled program, they would have to be charged.

## 4. Exact ND upper bound: complete witness generation and storage
`fullscan_nd_collision.py` freezes the38-instruction,512-byte ND_COLLISION program. It uses ordinary registers only and never touches the allocated mutable array.

Generate i:
- register9 accumulates a word initialized0;
- a power register starts1 and doubles modulo2^w;
- repeat GUESSBIT, accumulate `2*acc+bit`, double power, test power, loop;
- exactly w iterations occur, taking6w+2 instructions, including all bit choices and arithmetic.

Move i to register14 (one instruction), then generate j in register9 by the same paid loop (another6w+2).

The verification suffix reads n, rejects unless i<n and j<n and i!=j, THEN reads input offsets i+1 and j+1, compares the values, outputs the comparison bit and halts. Bounds are checked before increment/access, so invalid/maximum word guesses cannot wrap onto the n header. A valid distinct-index path uses exactly16 suffix instructions, hence

`ND opcode steps =12w+21`.

Every path consumes exactly2w GUESSBIT choices; invalid choices reject earlier. Witness storage i,j, current choice, loop power and flags fit the declared16-word register file. No choice-stream reread occurs.

Correctness: a duplicate pair induces an accepting branch. On an all-distinct array every valid pair comparison is false, and invalid pairs reject, so every branch rejects. Existence semantics are not a claim that a physical randomized solver finds the duplicate with high probability.

For n>=128, w<=2n, M<=n, so total cost including reserved initialization/acquisition is at most

`12w+21+(16+M)+(n+1) <=26n+38 <32n+512`.

Thus the exact same Γ admits the fixed ND program for every stated dimension. Its512-byte description fits B4096. Program-address/constant values fit w for n>=128.

## 5. This profile really includes a full-scan ordinary reference
The native SUM program (190 canonical bytes in the reused VM) reads all n entries and returns their sum modulo2^w. Its opcode count is exactly7n+9. Including initialization and the explicit full acquisition pass gives at most

`7n+9+(16+M)+(n+1) <=9n+26 <32n+512`.

It uses only the declared registers, so it fits this SAME Γ on every valid array, including arbitrary values in the word domain. This is an all-input semantic inclusion for one concrete ordinary aggregation routine, not an empirical benchmark score. It demonstrates why the OR sublinear-input failure is not the only possible restriction.

The profile also permits ordinary reread, arithmetic and up to sqrt(n) mutable words, with every charged action counted. It does NOT imply nearlinear sorting, arbitrary databases, large memory-intensive workloads or broad human/agent coverage fit Γ. Mutable input-copy/scratch beyond M is not smuggled in as a read-only service.

## 6. Deterministic BRAM -> general multiway BP mapping
Fix ANY deterministic BRAM program/data within the description bound (even input-independent nonuniform advice would be harmless to the lower bound). Restrict its n data words to the theorem's domain, with n header fixed.

A complete execution configuration has at most

`b(n)=(16+M)w+O(log F+log B+log Q+1)`

input-dependent state bits. If additional finite resource counters are retained, their O(log n) terms are included, not hidden. Because M=floor(sqrt n) and w=Theta(log n), `b=O(sqrt(n) log n)`.

Unfold execution through at most F primitive time levels, with timeout/output-limit/trap behaviors mapped to rejecting sinks under the declared acceptance convention (halt with output[1]). At an INPUT data instruction, its address is already determined by the configuration: use a node labeled by that coordinate and n² outgoing arcs for its possible value. The entire next configuration is an arbitrary deterministic function of the old state and that value, which a general branching-program node may encode. Header reads are constants. Internal arithmetic/static DATA reads/control and charged preprocessing do not access new x information and can be composed between input-query nodes; alternatively use dummy constant-response transitions with at most F levels. Source lower bounds permit arbitrary input-dependent query ORDER, so no monotone-pass assumption is made.

There are at most `O((F+1)*2^b)` unfolded configuration nodes. Hence the source's logarithm of TOTAL node count is

`S_BP <=b+O(log(F+1)) =O(sqrt(n) log n)`.

This is the necessary distinction between a per-level width bound and TOTAL BP size. Code/ROM contents are fixed independently of x and become nonuniform transition labels, not extra readable input information. Full raw input remains queryable in both models. All allocated array contents/16w registers and address/control bits are in b.

Therefore every Γ deterministic algorithm has a BP of depth at most F=O(n) and S_BP=O(sqrt(n)log n). But Theorem6.13 requires

`T >=Omega(n*sqrt(log(n/S_BP)/loglog(n/S_BP)))`

whose factor beyond n diverges, since log(n/S_BP)=Theta(log n). This contradicts O(n) depth for all sufficiently large n. Thus no deterministic Γ program decides COLL on the whole task family. The fixed ND program does, and deterministic programs are a syntactic subclass of ND programs, yielding a conditional **D_Γ proper subset N_Γ** on this declared task/model family.

Both PREPROCESSING and ordinary computation are included in the same F and b budget. A deterministic prefix that constructs an input-dependent summary is not prohibited; the BP lower bound already covers it. An uncharged external index or mutable raw input would instead violate the model and invalidate the transfer.

## 7. What is and is not certified numerically
Known exactly here: B4096, M(n), w(n), F(n), generated ND code size512, instruction count38, paid branch formula12w+21, initialization/acquisition reservations, and SUM7n+9.

Unknown here: an explicit numerical n0 at which the source's asymptotic lower bound beats32n+512 after all constants. Therefore this is NOT a finite hardware-budget certificate at n128 or1024 merely because tests ran there. Those dimensions test the upper implementation only. The source theorem supplies eventual exclusion, not a tested failure of every D program at one chosen finite n.

Also NOT certified: generic1/3-error randomized Γ lower bound, practical population coverage, accepted numerical portfolio preservation, standard P!=NP, or either standard side's ZFC unprovability. The source randomized ED statements have error conditions and cannot simply be substituted for the deterministic theorem. If goal v2 chooses randomized P-side solvers, a matching randomized theorem remains due.

## 8. Independent executable evidence
`python3 fullscan_nd_collision_standalone_v1.py` embeds the frozen abstract VM from my C58 extraction and the new program/tests, needs only the Python standard library, and is research-only, not an installed service. The factored development script is `fullscan_nd_collision.py`. Complete small arrays over3 values at n2..4 are sanity-checked with an explicit artificial width floor6 so38 instructions fit; they are NOT claimed to instantiate the asymptotic source domain. Every valid pair plus invalid/max addresses is tested. Larger n128/129/255/256/1024 include distinct, first/last duplicate and all-same arrays and address-boundary tests. Total132 arrays /4275 branch executions passed; every valid distinct-index branch used12w+21 steps, exactly2w choices, B4096, full init/acquisition reservations, and bit-charge cap. SUM exact semantics and7n+9 cost passed under the SAME profile.

Raw result: `fullscan-nd-collision-result.json`. Program canonical hash `b546506f5cb05e21d3dc059be755db4938a35a3de145ee37af61df302dd42cdb`. Tests confirm concrete upper semantics, not the asymptotic universal lower bound. Code and result are frozen below for consumption.

## 9. Remaining mathematical/coverage obligations
Independent review must check the original-source exact theorem/model, complete-state BP conversion, and the numerical profile's ND program. An effective finite n0 requires extracting constants through the source's earlier rectangle argument; no such bound is manufactured here. Memory scaling M=sqrt n may be too restrictive for the new practical goal; enlarging M so S_BP is linear in n removes this particular guaranteed superlinear factor. Broad capability inclusion and real coverage still need their own evidence.

This is nevertheless a genuine next candidate after the weak OR witness: true random access, full input scanning/acquisition, paid ordinary mutable memory and a native short ND witness fit the SAME declared resource vector, without a free read-only certificate. It is a localized conditional separation, not global goal acceptance.


## Frozen standalone reproduction source

```python
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

```

## Frozen test output

```json
{
  "status": "pass",
  "arrays": 132,
  "branch_runs": 4275,
  "nd_code_bytes": 512,
  "nd_instruction_count": 38,
  "nd_code_sha256": "b546506f5cb05e21d3dc059be755db4938a35a3de145ee37af61df302dd42cdb",
  "fullscan_SUM_same_profile": true,
  "initialization_reserved_in_total_fuel": true,
  "full_input_acquisition_pass_reserved": true,
  "small_test_width_floor_6_not_asymptotic_claim": true,
  "large_profiles": [
    {
      "n": 128,
      "w": 15,
      "memory_words": 11,
      "fuel": 4608,
      "valid_nd_steps": 201,
      "sum_steps": 905
    },
    {
      "n": 129,
      "w": 15,
      "memory_words": 11,
      "fuel": 4640,
      "valid_nd_steps": 201,
      "sum_steps": 912
    },
    {
      "n": 255,
      "w": 16,
      "memory_words": 15,
      "fuel": 8672,
      "valid_nd_steps": 213,
      "sum_steps": 1794
    },
    {
      "n": 256,
      "w": 17,
      "memory_words": 16,
      "fuel": 8704,
      "valid_nd_steps": 225,
      "sum_steps": 1801
    },
    {
      "n": 1024,
      "w": 21,
      "memory_words": 32,
      "fuel": 33280,
      "valid_nd_steps": 273,
      "sum_steps": 7177
    }
  ],
  "coverage_certified": false
}

```
