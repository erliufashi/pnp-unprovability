# E-chief-dom-1：可执行有界word-RAM与资源封闭reference包含

pnp-sol-a；2026-11-06 20:20；current-contract-v2。分类：proved-candidate（局部包含/反例，待独立核验）。不是现实总体覆盖，不是标准P/NP结果。

## 0. 相对已有成果的增量

E52给抽象工具计费合同，E51警告oracle portfolio；本节点新增一个完整可运行的确定性机器规范、原生reference程序、精确fuel公式与负向规范测试，并给普通位机器到该模型的明确构造。不是为缺失实测再写一次阻塞报告。

## 1. 自然候选模型 BRAM(Γ)

机器是fuelled word-RAM：16个w-bit寄存器，M个零初始化可写w-bit单元，随机访问只读输入、随机访问只读初始化data、顺序只写输出、有限指令表。算术ADD/SUB/MUL模2^w；LT/EQ、条件跳转、任意有限循环、LOAD/STORE、INPUT/DATA均可用。没有禁止重读、排序、检索、外存或普通计算工具；可执行工具必须编译成普通code/data，其费用自然进入账本。

每次运行冻结Γ=(w,F,M,B,O)：字宽、fuel、工作单元数、描述字节、最大输出单元。程序及初始化data的大小B=canonical-JSON(code)字节+ceil(w·len(data)/8)，不能把巨型证书/索引藏在免费只读带。固定解释器是共同模型的一部分，不按每个程序复制计数，但其版本hash固定。寄存器16w、PC/输出计数等O(log(F+M+B+O+n))控制状态另列；不把它们隐藏成零空间。

输入本身不计为advice，但每次读取计input_reads；data计data_reads；工作带读写和output分别计数；每步指令的序列化字节计code_fetch_bytes。初始化零写为(M+16)w bit，不能以全零数组免费的说法逃掉容量/初始化。bit_charge是声明的抽象上界计费（非实测硬件CPU）：每步8·fetch_bytes+8w，MUL改为8·fetch_bytes+w²；初始化另列。随机RAM寻址费用也须保留访问计数，本规范不宣称w-bit物理寻址恰好只费w位操作。

Γ类的合法策略是一个固定code/data，全部任务用同一策略；超fuel/容量/输出/非法访问有显式失败状态。Γ可以事前声明为输入规模的可计算函数，但不得看答案后换code。交互外部服务若有新信息，不被本封闭模型免费吸收；作为环境输入会改变任务协议。

实现：`bounded_vm_v1.py`。这是研究规范而非安装新CLI/服务。宿主Python实现可能有更大实际内存/时间；VM计数不等于宿主RSS或墙钟，也不自动属于具体物理Γ。

## 2. 命题1：原生reference的精确同预算包含

令R是该VM的固定原生code/data；对共同输入域X，若R所有运行均halt，且code/data≤B、步数≤F、访问地址<M、输出≤O、全部值遵守w位，则R∈BRAM(Γ)，且选择R自身为候选时每一条指令、输入/data访问、内存/输出、位计费完全相同。

证明：候选解释器、程序、初始状态、输入与Γ逐项相同。对步数归纳，取指相同；每个opcode是确定性操作，下一PC/状态和计数相同；由合法资源前提不触发额外失败；最终输出相同。这里没有通用模拟常数，也没有“单次轨迹等于所有输入”的偷换：全域包含需要逐输入上界。

因此这是一个正包含定理，不只是假设未提供reference时的条件空话：以下可执行reference已给出全域解析界。

## 3. 三个最小reference及解析界

SUM输入[n,x_0,...,x_(n−1)]，输出Σx_i mod2^w；它重读只读输入，对任何w位数据准确。若n和输入长度可寻址、code长度≤2^w−1，F≥7n+9、O≥1、B≥190（data空），则SUM原生成功；M可为0。推导：初始化5步；每元素7步；末次循环条件、跳转、输出、HALT共4步。所有输入和加法按w位语义，不声称任意精度自然数求和。

DOT输入[n,a_0,b_0,...]，输出Σa_i b_i mod2^w。若2n+1可寻址、F≥11n+10且B足够容纳代码，则原生成功：初始化6步，每pair11步，退出4步。乘法并非无限精度oracle，w²计费且模2^w。

REREAD先把一个输入存到外存地址0，LOAD两次再相加输出。F≥8、M≥1时成功；总memory_reads=2、memory_writes=1，表明可写外存和重读不是被禁能力。它只是规范测试，绝不代表广泛现实reference。

代码中固定SUM有一条不可达HALT，这仍计入描述190字节，不能因为不执行就删掉费用。DOT所有静态指令同样计费。

## 4. 命题2：普通有界确定性位计算的构造性包含（带显式开销）

固定一个有限转移表的k带确定性位TM R，含可双向重读输入、有限输出；不许免费oracle。给出事前可计算时间上界H(n)≥n以及可用字宽w(n)，足以表示k(2H(n)+1)、输入地址、有限状态编号和编译中间数。TM字母表固定，空白编码0、0/1编码1/2。若有多符号，用固定多位编码，常数由R决定。

构造一个固定BRAM程序C_R：
1. 把输入编码成显式带长度头的word数组；其转换成本/扩张必须单列，不能视为原问题同表示无开销。输入符号仍可随机读取，TM输入头位置存在寄存器/工作单元。
2. 分配k个长度2H(n)+1的工作块，TM头初始在中间H(n)。至多H(n)次TM步保证所有头不越界。H(n)由固定程序从长度头计算；要求其计算成本P_H(n)显式且字宽足够，不能按输入换代码常数。
3. 每个TM步LOAD k个头下符号；用固定比较/跳转树选转移；STORE新符号，调整各头及状态，OUT编码输出。有限转移表被编译为固定代码，寄存器不足时spill到O_R(1)工作单元，均计费。

于是存在可由转移表机械计算的有限常数c_R,b_R，使步数≤P_H(n)+c_R(H(n)+1)，工作单元≤k(2H(n)+1)+b_R，描述包含转移表与全部固定数据；初始化零写为该容量乘w。通过TM步归纳证明输出一致：初始空白和头位置匹配；每轮读的k个符号、选择的转移、写入与移动均匹配。

这不是调用未经核模型的时间/空间层级定理；全部模拟由上述构造给出。输入编码扩张、字宽、O(H)工作容量及c_R都收费。若H是固定多项式且w=O(log n)，得到多项式开销的普通计算包含；没有推出原TM最小空间S(n)被保持，也没有假定同一个精确Γ可装下任意R。

普通有限精度模型、数据库、排序/图算法只要本质是封闭可计算系统，都可先有TM实现再得到该模型里的实现；这证明模型非弱化的广泛表达能力，但模拟后可能超现实硬件预算。因此它不是“所有现实问题”的得分或mass结论。

## 5. 同预算无开销的错误外推：可执行反例

对SUM输入[3,2,3,5]，完整运行恰30步，描述190字节。相同程序Γ.F=30时halt输出10；F=29时在最终HALT前fuel_limit。即便先前已写出10，也不能把fuel_limit当成功halt。这说明精确资源边界对包装/额外一步敏感；“模拟只多常数”不能在同一个无slack预算内无条件保持。

这不是证明没有别的29步算法会输出10，只是反驳“该reference实现被零额外预算包装就一定包含”的特定断言。全类函数下界需要另证，不能从一个实现失败推出。

code少1字节、data多1个未付word、M=0却STORE、O=0却OUT均被单独测试拒绝。没有把证书/索引DATA读数1次误当数据免费。

## 6. 实际验收与边界

`python3 bounded_vm_v1.py --self-test`通过19项命名检查，包含SUM/DOT多个尺寸、原生同预算、fuel少1、code/data容量、外存重读、输出边界、非法寄存器/字宽及256组4-bit求和穷举。结果在bounded-vm-self-test-v1.json。

源码sha256：a6361e8f0f9299d80b8861b91b70fe236181d852541ab7ed6027a82b81282a41。

这些是规范一致性与局部reference包含证据，不是模型强度的统计证明；TM编译器是数学构造，尚未实现/机器核验；没有引入实测现实成功率。若允许所有多项式Γ的并集，这种普通计算模型可能回到标准P语义，而非自动得到严格收缩；分离另需固定Γ或其他结构约束，不能继承旧INDEX。

新正结果：一个自然可执行的强表达模型候选，原生reference的精确包含、普通计算的显式付费构造、无slack包装反例。未解：现实数值Γ、广泛reference、总体任务mass、同模型全类分离与标准ZFC桥。

## 附录A：冻结可执行规范

```python
"""Research-only deterministic bounded word-RAM; no benchmark coverage claim.
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


def run(code, inputs, env, data=()):
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
    stats = dict(steps=0, description_bytes=description,
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

## 附录B：原始本地测试输出

```json
{
  "status": "pass",
  "checks": [
    "sum:0",
    "sum:1",
    "sum:2",
    "sum:25",
    "dot:0",
    "dot:1",
    "dot:2",
    "dot:15",
    "native-identical-envelope",
    "one-less-fuel-fails",
    "code-not-free",
    "data-not-free",
    "data-paid",
    "external-memory-reread",
    "memory-bound",
    "output-bound",
    "word-data-bound",
    "bad-register-traps",
    "exhaustive-256-modular-sums"
  ],
  "check_count": 19,
  "coverage_claim": false,
  "example_trace": {
    "status": "halt",
    "output": [
      10
    ],
    "stats": {
      "steps": 30,
      "description_bytes": 190,
      "memory_words": 8,
      "register_words": 16,
      "init_write_bits": 384,
      "input_reads": 4,
      "data_reads": 0,
      "memory_reads": 0,
      "memory_writes": 0,
      "output_words": 1,
      "code_fetch_bytes": 357,
      "bit_charge": 6696
    },
    "code_sha256": "cbbd1bc9c2d1708da05f18d0d384bfafe39d574c109c48d91b5cfaad306e86b4"
  }
}

```
