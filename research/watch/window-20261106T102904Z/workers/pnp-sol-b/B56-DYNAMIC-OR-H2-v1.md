# B56 / H2：动态聚合索引的未来能力、完整状态与计费实现 v1

pnp-sol-b，2026-11-06；分类：局部候选定理 + 可执行能力底线 + 反例，待独立复核。不是实测human、不是现实大部分覆盖、不是标准P/NP或新v2总目标完成。

## 0. 新信息及任务接口

已读chief的ARGON-H1-DISPOSITION及C的IDX/GVC/FNS证据。IDX已经证明静态坐标查询需要保留数据，而静态OR可以只存1 bit。本文**不重复静态INDEX或OR query下界**；研究同样只输出1-bit OR，却允许未来数据更新时摘要是否仍能保全能力。

结果：若不再保留raw data，未来允许最多U次任意SET(i,b)更新，则最少初始可区分状态数（0≤U<N）恰为

`M(N,U) = 1 + Σ_{k=0}^U binom(N,k)`。

即至少`ceil(log2 M(N,U))`个完整初始状态bit。U=0只需1bit；U=N−1需要Nbit。静态一bit压缩不能免费继承长期编辑能力，即使每个query的输出始终只有1bit。

如果raw data仍保留，普通确定算法可用全数据N bit加一个`ceil(log2(N+1))`-bit计数器，支持确切更新/查询。本文给出该实现及生命周期账本；这不与上述下界冲突，因raw data本来就已经贡献N bit状态。

## 1. 精确模型：可访问状态而非某个工作数组

Build读取任意x∈{0,1}^N，输出初始系统状态s(x)。之后：
- 原x不再可读，且没有其他未计费的input-dependent索引、日志、时钟信息或外存；
- Update接收位置i及新bit b，语义为x_i←b，不额外提供可信旧bit；
- Query必须在每个允许历史上正确返回当前OR；
- 至多U次Update，Query可以在它们之前、之间和之后发生；
- N、U、程序和初始public常量相同，不依赖x；系统确定且精确。

若允许原始数据随机访问，使用下文另一合法模型；不得把该访问留着却仍把辅助索引bit数当全部状态下界。

状态包括未来可读取的全部输入相关内容：index、working memory、register/PC、保留输出、外部文件、计时/游标状态等。Build的不同结束时刻若以后可读，也是信道，不能放在s之外。N/U等公开常量不携带关于x的信息，不是免费当前输入advice。

这是确定精确动态数据结构的状态容量定理。不未经证明提升成随机允许错误或量子模型下界，也不约束有权限读取外部真值服务的不同任务协议。

## 2. 下界的自含证明

将x视为1所在的集合S⊆[N]。

1. 任意两个不同的集合S,T，若各自大小≤U，就可区分。若T\S非空，执行把S中每个位置SET为0的共同后继序列，长度|S|≤U。S世界最后OR=0，T世界仍有T\S所以OR=1。若T⊂S则交换二者。
2. 任意|S|≤U的集合与任何|T|>U的集合也可区分：同样清空S，后者至少还有一个1。
3. 因为同一初始状态遇到同一更新序列会产生同一轨迹/输出，以上各个小集合必须各有不同初始状态，且与至少一个“大集合”状态分开。

因此需要至少`Σ_{k=0}^U binom(N,k)+1`种状态。若完整可访问状态只含b个二进制位，最多2^b种，得到b≥ceil(log2 M)。若使用变长编码，长度/边界也须计入状态；不能把“b bit内容+免费可变长度”当2^b状态。

此证明允许任意计算、随机访问已保存状态、任意多次重读、任意Build时间；它不依赖streaming/pass假设。它同样不禁止合法预处理：预处理可任意强，但如果丢掉区分状态，就不能支持全部未来更新。

## 3. 初始状态类数上界：为何这个数量恰好

若|S|>U，未来至多U次SET最多清掉U个1，因此所有未来Query始终1。所有这种初始S可合并为同一个ALWAYS_ONE状态。

若|S|≤U，保留S的精确表示和剩余更新预算r。每次更新后得S'，r←r−1；若|S'|>r，可转入ALWAYS_ONE，因为剩余更新再不能清空它；否则继续保留S'。因此初始时恰有每个小集合加一个大集合类，没有更多必要等价类。

这证明**初始信息容量**紧，不证明每一步都可用log2 M个bit、零额外scratch或高效直接转移。固定N/U时可将初始类编码成整数，但解码/更新需要时间、描述和工作空间。下面的frozenset实验只是语义见证，不声称已经实现最优bit-packed动态表示。

案例N=8：

| U | 初始状态类数 | 至少bit |
|---:|---:|---:|
| 0 | 2 | 1 |
| 1 | 10 | 4 |
| 2 | 38 | 6 |
| 4 | 164 | 8 |
| 7 | 256 | 8 |

这量化“未来能力要付多少钱”，不是把更新能力直接当现实覆盖。

## 4. 两个真正可失败的接口反例

### 4.1 一bit OR缓存不能支持任意删除

x=(1,0)、y=(1,1)的静态OR都为1。若只存这一bit，后继相同操作SET(0,0)后，x的OR变0、y仍为1，系统不可能对两者都正确。

这不是说普通cache无用，而是说static aggregate的语义范围不含任意更新。可以禁用/拒绝更新，也可以付费重建；不能在同一能力保全证书里悄悄声称全支持。

### 4.2 “只存计数就够”还须旧bit来源

如果保留count但不保留raw数据，而且Update只给(i,new)，就不知道原x_i。例x=(1,0)、y=(0,1)计数都为1，对SET(0,0)一个应减1、一个应不变。只存count仍不够。

如果协议额外给可信oldbit，则可以更新count，但oldbit是新信息/信任前提。若由不可信调用者声称，需要回读raw验证或其他认证，不能把认证本身免费化。此处选择保留raw以获得可实现的普通算法。

## 5. 保留raw data的确定实现：能力底线而非封禁工具

`DynamicOR`冻结如下语义：
- Build把N个输入bit读入自己的packed mutable raw buffer；同时用binary ripple counter累计1的个数。
- count位宽B=`ceil(log2(N+1))`，不是一律ceil(log2 N)。N为2的幂且全1时，少一位会overflow。代码`N.bit_length()`给正确B。
- SET先验证位置、新bit和expected_version，读旧raw bit；值改变时增/减counter，再写raw，递增version。没有免费oldbit服务。
- Query读取counter判断非零；不每次重扫N个raw bit。
- 同步单调用顺序执行，没有并发读写。expected_version仅拒绝过期调用，不是磁盘崩溃恢复、持久原子事务或线性化并发实现。若中途故障/被并发观察，需另做事务设计；本节点不免费承诺。

可访问输入相关数据至少包含raw N bit+counter B bit，外加version、shape、ledger等metadata。packed payload字节数可测，**不是Python RSS或整个存储峰值**。版本和日志不能在无限生命周期中当O(1)；最多H次更新时版本需ceil(log2(H+1)) bit，计数器等也需按各自最大值收费。

## 6. 明确计费，不用query warm成本冲掉cold Build

实验逐项记录input reads、raw reads/writes、counter reads/writes、query/update/reject次数。fresh buffer零初始化也按逻辑bit writes收费。

- cold Build：N次输入bit观察、N次raw copy writes、N次raw零初始化writes、B次counter初始化，再加实际count更新操作。
- 单次SET：至少1次raw读取、1次raw写入（即使幂等也保留写账）；若值改变，最多B次counter read及B次write。另付参数传输、地址准备、version比较/更新和控制。
- Query：本实现读B个counter bit，输出1 bit；调用/返回和版本策略成本另外说明。
- 完整生命周期：Build + 实际updates + 实际queries + 失败/拒绝请求成本；不能只报warm query和假设无限查询摊销。

这些cell counters不是完整bit/word机器指令或墙钟。要转成位模型，可固定indexed bit-cell ISA，将每次cell寻址的O(log(N+H+1))位地址构造、版本/控制操作显式加上。一个保守统一上界为Build `O(N log²(N+H+1))`、每次更新/查询 `O(log²(N+H+1))`，存储`N+O(log(N+H+1))`位加固定程序/metadata；该上界有意宽松，不声称Python每步实现常数1。具体硬件word packing、host对象和物理峰值仍须另核。

N=64、输入交替1/0，删除32个初始1后Query=false；本次账本：input_reads=64，raw_reads=32，raw_writes=160，counter_reads=133，counter_writes=133，updates=32，queries=1。packed raw+counter payload=9 bytes；version和ledger/Python host开销未包含且不是0。源输入在测试harness中的驻留/副本同样不能拿9 bytes冒称全物理峰值。

## 7. 验证范围及真实未付款

7项标准库测试通过：
1. N=1..7、所有U<N，枚举所有初始数组及大小≤U的reset子集，核恰有M(N,U)种观察signature；
2. N=4所有初始数组，对每个U=0..3穷举全部允许的SET地址/值历史，核有界summary语义；
3. N=1..7全部数组与单步SET，核raw+counter和直接OR/count一致；
4. N=16全1的counter宽度、全部删除后OR=0；
5. 一bit summary删除反例；
6. stale expected_version在任何修改前拒绝；
7. cold账本含输入读取/初始化，payload不冒host内存。

实验是公式/语义核验，不代表全算法证明。第2节自含论证才覆盖完整状态量词。既没有使用PPST摘要，也没有再拿缺μ当研究成果。

新的待付义务：
- 若把动态更新加入能力保全目标，应先冻结允许的更新集合/次数H、raw是否保留、oldbit谁提供、故障/并发语义；否则static-index证书不能转移。
- 真实reference若要求长生命周期、持久共享索引，必须计全部可访问状态，而非只有每次Query局部workspace。
- 完整物理实现还要核runtime、peak live、日志、version增长、地址/序列化、持久化/崩溃恢复；此研究未部署服务。
- 若要新的D/ND分离，双方须同样得到raw/索引/update权限。本结果是容量和功能保全边界，不是新D/ND分离证书。
- 现实任务分布/强参考广度仍须独立认证；本节点不说现实大部分任务已测。

## 8. 消费/回退与只读旧证据

共享板B56的不可变hash证据是消费者入口；以下冻结附录允许独立复制复现，只依赖Python标准库。源和结果在pnp-sol-b独占cwd；未安装CLI/服务或修改PATH/凭据。可回退到只读旧IDX/static aggregate语义，但那会丢失这里新增的更新能力，不能标作同能力无损回退。

旧v1、E48/B54、PPST/B55及原104文件均未修改。当前标准T1/T2及T3-v2保持UNRESOLVED。

## 附录：冻结研究源

```python
"""B56 research-only dynamic OR: explicit bit cells and lifecycle counters.
No physical RAM/time claim; Python execution is a semantic reference.
"""
from dataclasses import dataclass, field
from itertools import combinations, product
from math import comb
import json
import unittest

@dataclass
class Ledger:
    input_reads:int=0
    raw_reads:int=0
    raw_writes:int=0
    counter_reads:int=0
    counter_writes:int=0
    queries:int=0
    updates:int=0
    rejected_updates:int=0

class PackedBits:
    def __init__(self,n): self.n=n; self.data=bytearray((n+7)//8)
    def read(self,i): return (self.data[i//8]>>(i%8))&1
    def write(self,i,b):
        mask=1<<(i%8)
        if b: self.data[i//8]|=mask
        else: self.data[i//8]&=~mask

class DynamicOR:
    def __init__(self,bits):
        self.n=len(bits)
        if self.n<1: raise ValueError('invalid dataset')
        self.ledger=Ledger()
        self.raw=PackedBits(self.n)
        self.width=self.n.bit_length() # ceil(log2(N+1)), includes the all-ones count N
        self.count=PackedBits(self.width)
        self.version=0
        self.ledger.counter_writes+=self.width # initialization is not free
        self.ledger.raw_writes+=self.n # charge logical zero-initialization too
        for i,b in enumerate(bits):
            self.ledger.input_reads+=1
            if b not in (0,1): raise ValueError('invalid dataset bit')
            self.raw.write(i,b); self.ledger.raw_writes+=1
            if b: self._change_count(1)
    def _change_count(self,delta):
        for j in range(self.width):
            old=self.count.read(j); self.ledger.counter_reads+=1
            self.count.write(j,1-old); self.ledger.counter_writes+=1
            if (delta==1 and old==0) or (delta==-1 and old==1): return
        raise AssertionError('counter overflow/underflow')
    def query(self):
        self.ledger.queries+=1
        answer=0
        for j in range(self.width):
            answer|=self.count.read(j); self.ledger.counter_reads+=1
        return bool(answer)
    def update(self,i,new,expected_version):
        if not 0<=i<self.n or new not in (0,1) or expected_version!=self.version:
            self.ledger.rejected_updates+=1
            raise ValueError('invalid update or stale version')
        old=self.raw.read(i); self.ledger.raw_reads+=1
        if new!=old: self._change_count(1 if new else -1)
        self.raw.write(i,new); self.ledger.raw_writes+=1
        self.version+=1; self.ledger.updates+=1
    def decoded_count(self):
        # Diagnostic, NOT a charged Query operation or a production escape hatch.
        return sum(self.count.read(i)<<i for i in range(self.width))
    def packed_payload_bytes(self): return len(self.raw.data)+len(self.count.data)

@dataclass(frozen=True)
class BoundedSummary:
    n:int
    remaining:int
    support:frozenset=field(default_factory=frozenset)
    always_one:bool=False
    @staticmethod
    def build(bits,U):
        if not 0<=U<len(bits): raise ValueError('U must be below N')
        S=frozenset(i for i,b in enumerate(bits) if b)
        return BoundedSummary(len(bits),U,frozenset() if len(S)>U else S,len(S)>U)
    def query(self): return self.always_one or bool(self.support)
    def update(self,i,b):
        if self.remaining==0 or not 0<=i<self.n or b not in (0,1): raise ValueError('outside contract')
        if self.always_one: return BoundedSummary(self.n,self.remaining-1,frozenset(),True)
        S=(self.support|{i}) if b else (self.support-{i})
        r=self.remaining-1
        return BoundedSummary(self.n,r,frozenset() if len(S)>r else frozenset(S),len(S)>r)

def class_count(N,U): return sum(comb(N,k) for k in range(U+1))+1

def reset_signature(mask,N,U):
    vals=[]
    for k in range(U+1):
        for R in combinations(range(N),k):
            clear=sum(1<<j for j in R)
            vals.append(bool(mask&~clear))
    return tuple(vals)

class DynamicTests(unittest.TestCase):
    def test_exact_initial_equivalence_classes(self):
        for N in range(1,8):
            for U in range(N):
                signatures={reset_signature(x,N,U) for x in range(1<<N)}
                self.assertEqual(len(signatures),class_count(N,U))
    def test_bounded_summary_all_short_histories(self):
        N=4
        for U in range(N):
            for x in range(1<<N):
                bits=[(x>>i)&1 for i in range(N)]
                def walk(s,raw,r):
                    self.assertEqual(s.query(),any(raw))
                    if not r: return
                    for i,b in product(range(N),(0,1)):
                        new=raw.copy(); new[i]=b
                        walk(s.update(i,b),new,r-1)
                walk(BoundedSummary.build(bits,U),bits,U)
    def test_raw_plus_counter_all_transitions(self):
        for N in range(1,8):
            for x in range(1<<N):
                initial=[(x>>i)&1 for i in range(N)]
                for i,b in product(range(N),(0,1)):
                    a=DynamicOR(initial); raw=initial.copy(); raw[i]=b
                    a.update(i,b,0)
                    self.assertEqual(a.query(),any(raw))
                    self.assertEqual(a.decoded_count(),sum(raw))
    def test_full_ones_counter_width(self):
        a=DynamicOR([1]*16)
        self.assertEqual(a.width,5) # log2 N bits alone would overflow at count N
        self.assertEqual(a.decoded_count(),16)
        for j in range(16): a.update(j,0,j)
        self.assertFalse(a.query())
    def test_boolean_summary_failure(self):
        x=[1,0]; y=[1,1]
        self.assertEqual(any(x),any(y))
        x[0]=0; y[0]=0
        self.assertNotEqual(any(x),any(y))
    def test_stale_rejected_before_mutation(self):
        a=DynamicOR([1,0]); a.update(1,1,0)
        before=(bytes(a.raw.data),bytes(a.count.data),a.version)
        with self.assertRaises(ValueError): a.update(0,0,0)
        self.assertEqual(before,(bytes(a.raw.data),bytes(a.count.data),a.version))
    def test_cold_cost_and_retained_data(self):
        a=DynamicOR([1,0]*32)
        self.assertEqual(a.ledger.input_reads,64)
        self.assertEqual(a.ledger.raw_writes,128)
        self.assertEqual(a.packed_payload_bytes(),9)
        self.assertGreaterEqual(a.ledger.counter_writes,a.width)

if __name__=='__main__': unittest.main(verbosity=2)
```

## 附录：冻结测试输出

```text
test_boolean_summary_failure (__main__.DynamicTests.test_boolean_summary_failure) ... ok
test_bounded_summary_all_short_histories (__main__.DynamicTests.test_bounded_summary_all_short_histories) ... ok
test_cold_cost_and_retained_data (__main__.DynamicTests.test_cold_cost_and_retained_data) ... ok
test_exact_initial_equivalence_classes (__main__.DynamicTests.test_exact_initial_equivalence_classes) ... ok
test_full_ones_counter_width (__main__.DynamicTests.test_full_ones_counter_width) ... ok
test_raw_plus_counter_all_transitions (__main__.DynamicTests.test_raw_plus_counter_all_transitions) ... ok
test_stale_rejected_before_mutation (__main__.DynamicTests.test_stale_rejected_before_mutation) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.055s

OK
```

## 附录：冻结账本和有限状态结果

```json
{
  "status": "research semantic/cell-accounting only",
  "initial_state_bounds": [
    {
      "N": 8,
      "U": 0,
      "classes": 2,
      "ceil_log2_classes": 1
    },
    {
      "N": 8,
      "U": 1,
      "classes": 10,
      "ceil_log2_classes": 4
    },
    {
      "N": 8,
      "U": 2,
      "classes": 38,
      "ceil_log2_classes": 6
    },
    {
      "N": 8,
      "U": 4,
      "classes": 164,
      "ceil_log2_classes": 8
    },
    {
      "N": 8,
      "U": 7,
      "classes": 256,
      "ceil_log2_classes": 8
    }
  ],
  "final_or": false,
  "ledger": {
    "input_reads": 64,
    "raw_reads": 32,
    "raw_writes": 160,
    "counter_reads": 133,
    "counter_writes": 133,
    "queries": 1,
    "updates": 32,
    "rejected_updates": 0
  },
  "persistent_payload_bytes": 9,
  "version": 32,
  "metadata_host_overhead": "not measured; not zero"
}
```
