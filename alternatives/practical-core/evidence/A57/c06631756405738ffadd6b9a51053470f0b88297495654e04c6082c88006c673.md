# A57：收费见证的可执行BRAM严格分离，以及它为何不是当前现实覆盖证书

pnp-sol-a；2026-11-06。局部proved-candidate，待独立核验。自然机器模型中的精确D/ND分离；不声称标准P≠NP，不把小OR任务当现实总体覆盖。

## 1. 相对前序的真实增量

在E-chief-dom-1实际执行的BRAM上新增逐bit非确定性指令GUESSBIT（一次只返回0/1，计1步和正常字操作bit_charge），实现完整见证生成、存储、校验；不借用免费只读证书。证明该模型某个完全相同数值资源profile的D/ND严格分离，并给随机化查询下界。随后证明该profile不能包含已给出的全输入SUM reference，故拒绝把此toy分离作为用户新目标的正验收。

## 2. 模型、任务与相同预算

继承E-chief-dom-1 BRAM：代码/data描述≤B字节，16个w-bit寄存器、M个工作word，重读随机访问输入，每指令1fuel，乘法模2^w且有w²位收费，无外部工具oracle。新ND模型只多GUESSBIT，选择位按一步生成，一路按存在性接受；D是没有非确定性选择的子类，R把选择解释为随机币。

任务OR_n，输入同一编码[n,x_0,...,x_(n−1)]，各x_i∈{0,1}。n≥128；w=ceil(log2(n+2))（实现为(n+1).bit_length()，且测试额外下限5便于短代码地址），F=6w+12，B=512，M=0，O=1。16w寄存器、控制计数位、初始化16w零写全部收费，两侧相同。输入长度n+1≤2^w−1。

若加位收费上限，可取F(4096+8w+w²)以及初始化16w；因为每条指令编码≤整份512字节代码，逐指令fetch≤512，所有已有计费均在此显式上界内。它很松但不是无界免费算术；D下界甚至允许更强的任意内计算和任意输入独立初始化，故仍成立。

接受当且仅当halt且输出[1]；输出[0]为拒绝。ND对否实例全部分支拒绝，对是实例至少一分支接受；不是把一次随机碰巧成功当成功概率1。

## 3. 完整收费ND程序：恰6w+12步上界

具体ND_OR代码在paid_certificate_or_v1.py：

- 初始化寄存器9=0（见证地址）、10=1（位宽探测power）、11=2，用3步。
- 每轮GUESSBIT12；寄存器9←2·9+12；寄存器10←2·10 mod2^w；若power非0继续。
- power在恰w次倍增后首次为0；中间w−1轮每轮6步，末轮5步。因此生成/packing/控制共3+6(w−1)+5=6w+2步，不是免费一次猜完整地址。
- 见证j存寄存器9，最多w bit，和当步选择位/循环控制都在已计16w寄存器文件内。没有w-bit只读证明带藏在空间外，也没有随机访问过去选择位。
- 余下固定10步以内：读n，复制j，检验j<n；无效见证输出0。合法见证读取x_j（输入下标j+1），输出该bit并halt。

完整代码275字节（含GUESSBIT字符串），低于两侧同B512；没有额外data。合法见证路径恰6w+12步，非法路径更短。

正确性：全零输入对任何j均拒绝；存在x_j=1时，选择位序列逐bit生成这个合法j，接受。j<n先验证再加1，故最大word地址回绕不会让n头字段冒充x_j。所有符号、PC和数据范围在给定w内。

源码实现bounded_vm_nd_v1.py仅增加GUESSBIT与choice_bits计数；确定性原始VM不改，已发布hash不变。测试传入的choices是逐位分支选择流而非额外任意字符串读取oracle；解释器只消耗一次，记录w次GUESSBIT。

## 4. D的同资源下界：n次输入bit读取必要

取任意确定性策略，任意input-independent代码/data（甚至允许对每个n任意大的非统一advice，只要不依赖x）。在全零x上运行；若读取不足n个不同数据位置，选一个从未读取的位置j，把它改为1。

按执行步归纳，两输入至算法停止前的读取结果完全一致，因此PC、内存、输出与停止状态一致。全零和单1的OR值不同，故它至少错一边。允许重读、随机访问、任意内计算和自适应地址不会破坏此不可区分性。

D正确计算OR必须至少n次数据读取；每步至多读一个输入word，所以fuel至少n。n≥128时n>6ceil(log2(n+2))+12=F，故D-BRAM(Γ)无法计算整个OR_n，而ND_OR在同Γ内做到。这是该资源profile的严格D/ND分离，不是仅某个D实现失败。

这里程序描述是否按字节最小、指令是否能优化，都不会改变下界；即使扩大代码/data容量也无法让未读的独立输入bit变成已知。

## 5. 随机化不能免费填平查询差

允许至多q次数据查询、每实例错误率≤ε的随机策略。把全零输入与均匀随机位置J的单1输入耦合同一随机带。沿全零轨迹，命中J的概率至多q/n；未命中时执行/输出完全一致。若全零接受概率≤ε，而所有单1接受概率≥1−ε，则1−ε≤ε+q/n，即q≥n(1−2ε)。无需独立查询，重复只降低不同位置覆盖。

所以固定最坏fuel F限制下，ε≥(1−F/n)/2；对很大n趋近1/2。ND存在性接受不能当作现实随机运行的高成功率：单1时均匀猜j一轮只以约1/2^w命中，确定性找证据最坏仍需n次读取。收费证书证明和可执行有保证的寻找器必须分开。

## 6. 为什么这个候选不能验收新现实目标

同域全输入SUM reference需要在最坏情形读取n个数据位置：若漏一个bit，将其0改1，模2^w和也改变（n<2^w，不存在该单bit差为0）。相同不可区分性立即给n查询下界。因此F=O(log n)不可能包含E-chief-dom-1给出的SUM全域能力，更不包含一般读取整个输入的数据库/文档任务。

反之若放宽F以覆盖原生SUM的7n+9步，同时B≥204，则固定确定性OR_SCAN（204字节）最坏7n+8步可用：全零时每元素7步，初始化/退出合计8步，遇1提前输出。这个特定OR分离被该增强预算消去。

结论不是所有强模型都不可分离，而是此“易证明的sublinear-input”候选无法同时满足全输入reference包含。用户要求强现实能力时不能拿此已知弱预算充数，也不能把同模型“纯数学分离已证候选”混称现实覆盖与严格分离联合通过。另一方面，BRAM模型本身支持任意普通计算；失败在选的Γ，不是禁重读或禁外存。

## 7. 实际测试、原始证据与未解

paid_certificate_or_v1.py通过511个不同输入实例（n=0..8的全部二进制数组）及16352个w-bit见证路径；每条同时核直接付费data验证器和完整逐bit ND生成程序，包含非法/最大地址、全零soundness、存在性completeness、合法路径6w+12步。OR_SCAN同步核对；n=64全零实测456=7n+8步、65 input_reads。测试小尺寸只检查语义，n≥128下界由上述一般证明给出。

原始输出paid-certificate-or-test-v1.json。ND VM sha256 c8ded75264b622c6e67dc921bd6cea3fe7ec6dba73886762e8232e43a6f4c23c；测试脚本sha256 1782425ca5571791295a0944b5001b727af41afaf8048faf3b15801ccd730bfa。附录冻结完整源码和测试输出。

未解：在包含强现实reference的Γ里找到不靠sublinear-input弱化的同模型分离；现实分布mass仍缺。没有引用未经核对的层级定理，没有从该局部资源分离跨到标准P/NP或ZFC不可证性。

## 冻结附件：bounded_vm_nd_v1.py

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test; this is a research specification, not an installed service")
    print(json.dumps(self_test(), indent=2))

```

## 冻结附件：paid_certificate_or_v1.py

```python
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

```

## 冻结附件：paid-certificate-or-test-v1.json

```json
{
  "status": "pass",
  "input_cases": 511,
  "witness_paths_checked": 16352,
  "generation_steps_per_path": "6w+2, including w GUESSBIT instructions and packing/loop",
  "certificate_storage_bits": "w in register 9, within charged 16w-bit register file; direct verifier variant additionally charges data bytes",
  "max_verifier_steps": 10,
  "nd_code_bytes": 275,
  "nd_total_steps_per_valid_path": "6w+12",
  "existential_not_physical_solver": true,
  "reality_coverage": false,
  "source_vm_sha256": "a6361e8f0f9299d80b8861b91b70fe236181d852541ab7ed6027a82b81282a41",
  "certificate_code_bytes": 147,
  "scan_code_bytes": 204,
  "sum_code_bytes": 190,
  "zero_scan_trace": {
    "status": "halt",
    "output": [
      0
    ],
    "stats": {
      "steps": 456,
      "description_bytes": 204,
      "memory_words": 0,
      "register_words": 16,
      "init_write_bits": 112,
      "input_reads": 65,
      "data_reads": 0,
      "memory_reads": 0,
      "memory_writes": 0,
      "output_words": 1,
      "code_fetch_bytes": 5340,
      "bit_charge": 68256
    },
    "code_sha256": "8347921f2fdfdc2ce0dc2d65a4d90167175fed9452700c58b7cb7736588a56e2"
  }
}

```
