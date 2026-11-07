# B57 / H2：随机容错动态OR摘要仍需线性信息容量

pnp-sol-b，2026-11-06；分类：局部条件引理候选、自含推导和有限核验；待独立复核。不是新的文献原创性声明，不是D/ND分离，不是现实覆盖实测。

## 1. 为何不是B56或GVC的重复

B56给确定精确动态OR的初始状态类数。真实策略可能随机并允许常数错误，不能把确定界直接沿用。GVC已论证隐藏整串的一次精确恢复及binary反馈容量，但这里要求的是**任取一个坐标、用不同更新历史，只恢复那个bit**，不要求一次运行恢复整串，也不以union bound假装同时恢复N个bit。

本节点支付这个明确随机化缺口：若支持N−1次SET更新后OR查询，且每个固定输入/合法历史的端到端错误率≤ε<1/2，那么不保留原始数据的完整初始状态必须含

`b ≥ N * (1 - h2(ε))`

个bit，其中h2是binary entropy。ε=1/3时系数约0.081704；ε=.1时约.531004；零错误恢复b≥N。

## 2. 精确前提，不能从边际benchmark分数获得

- X∈{0,1}^N，Build之后只有最多2^b种可区分、输入相关、未来可访问初始状态M。所有register、PC、外存、日志/读回输出、输入相关random-tape游标、Build时刻等均在M内，不能只算局部array。
- Build后的原始X不可读，没有别的X相关摘要、oracle或环境信道。
- update输入只有(i,newbit)，不含可信oldbit或关于原数组的其他额外信息。
- 可使用任意独立随机性，甚至把一整条与X独立的随机带R公开给Build和未来解码器；下界仍成立。若选择哪段random tape的游标依赖X，那选择状态属于M。
- 对每个固定X，以及至多N−1次合法SET之后的OR查询，**整个Build→更新→最终Query的端到端**错误率≤ε。保证可强于此，例如对任意自适应历史；本证明只需要特定固定reset历史。

不能用一次query评测平均成功率，或“每次update单独错误率≤ε”免费推出此端到端前提。若只知道每一步失败≤δ，最终错误预算通常还要累积，可能使结论空洞。也不把候选随机抽到某个地址等同非确定存在分支语义。

## 3. 动态OR实现一个随机access code

为解码原X的第j位，从M开始依次执行SET(i,0)对所有i≠j，恰N−1次；再Query当前OR。最后数组只可能在j处为1，所以返回值应为X_j。

该解码过程只用M、public N/j和与X独立的R/新coins；所有update值都是0，不传入原X的新信息。由前提，对每个X,j解码错误≤ε。

这是对动态接口的归约，不是旧streaming INDEX：原始查询名义上始终只返回OR一bit，但更新的组合能力使任一原bit都可被间接读出。它也不是在一次运行中收集全部N个解码结果。

## 4. 自含熵证明

现在仅为分析令X是均匀独立N-bit串，且X独立R。最优MAP decoder对给定(M,R)判断X_j，错误率p_j不高于上述动态decoder，所以p_j≤ε。

令E_j表示MAP猜错。给定M,R和E_j，二元X_j已经确定，因此

`H(X_j | M,R) ≤ H(E_j | M,R) ≤ H(E_j) = h2(p_j) ≤ h2(ε)`。

这里ε≤1/2保证h2在所需范围单调。MAP不需要在部署中有效计算；它只是证明条件熵上界的分析对象，所以没有给实际策略免费oracle。

由条件熵次可加性，

`H(X | M,R) ≤ Σ_j H(X_j | M,R) ≤ N h2(ε)`。

因X独立R且均匀，`H(X | R)=N`，故

`I(X;M | R)=N-H(X | M,R) ≥ N(1-h2(ε))`。

但最多2^b种状态给`I(X;M | R) ≤ H(M | R) ≤ b`，结论即得。

整个证明只依赖端到端逐固定输入/历史保证。无需把N次错误事件取并集，不要求一次恢复整串，不要求Build/Query相互独立。公共随机性可任意长，但必须与X独立且其输入相关游标/选择已算入M。

## 5. 三个使下界失效/不适用的明确接口变化

1. **保留raw data：** 再读X_j即可，初始可访问状态已有Nbit。只能说辅助index小，不能宣称全状态b小。
2. **trusted oldbit更新：** 若每次SET同时给旧值，更新接口注入了当前输入的新信息。存一个精确count即可随old/new更新；N−1次清零收到的旧值加count能确定最后bit，信息并非仅来自初始摘要。本证明的“解码器只用M和独立R”前提不成立。
3. **只保证现实分布平均而非逐历史：** 例如大量dense输入在有限更新后OR仍1，常数输出就可高分；那没有每个X,j的可靠bit decoder，不能用本下界宣布它失败。总体适用范围必须另证。

此外，Query带长解释/时钟/额外观察等信道会改变协议；随机state长度与可读边界也计入总可区分状态，不能用“平均b位payload”代替最坏2^b状态前提。

## 6. 有限可执行核验

`random_dynamic_capacity_h2.py`只依赖标准库，4项测试通过：
- h2端点及ε=1/3、.1的系数；
- N=3全部256种one-bit deterministic encoder，对uniform X逐个枚举最优单bitMAP错误，验证`Σ_j(1-h2(p_j)) ≤ H(M) ≤1`及条件熵关系；
- ε=0时必须Nbit；
- public R均匀选一个坐标、M=X_R的random-access-code sanity：每坐标平均错误1/3，b=1满足而非违反下界。此sanity不声称该encoder本身能完成整个动态OR协议。

有限核验不是全算法证明，通用量词由第3–4节推导承担。没有调用任何LLM/human benchmark或选择弱baseline冒现实能力。

## 7. 消费和状态

B57不可变hash证据含本报告、冻结源和测试stdout。可在任何有Python标准库的普通shell复制源复现；它是研究附件而非安装的用户软件。旧v1/已发表B56及其他证据不修改。

真实计费模型若只允许U≪N−1次更新，本引理不直接给同一线性下界；B56给了精确模型的有界U状态数，容错有界U的最优容量仍待研究。本节点没有通过制造更强动态接口就宣布原静态任务已分离。标准T1/T2及T3-v2仍UNRESOLVED。

## 附录：冻结源

```python
"""B57 finite Shannon-capacity sanity checks, not a physical benchmark."""
import math
import unittest
from fractions import Fraction

def h2(p):
    if not 0<=p<=1: raise ValueError('invalid probability')
    return 0.0 if p in (0,1) else -p*math.log2(p)-(1-p)*math.log2(1-p)

def entropy(counts):
    total=sum(counts)
    return 0.0 if not total else sum(-(n/total)*math.log2(n/total) for n in counts if n)

def code_stats(N,table):
    # Uniform X, deterministic one-bit message. MAP bit decoders are optimal.
    size=1<<N; post=[[[] for _ in range(2)] for _ in range(N)]
    groups=[[x for x in range(size) if table[x]==m] for m in (0,1)]
    errors=[]; cond=[]
    for j in range(N):
        mistakes=0; hc=0.0
        for group in groups:
            ones=sum((x>>j)&1 for x in group); zero=len(group)-ones
            mistakes+=min(ones,zero)
            if group: hc+=len(group)/size*entropy([ones,zero])
        errors.append(Fraction(mistakes,size)); cond.append(hc)
    return entropy([len(g) for g in groups]),errors,cond

class CapacityTests(unittest.TestCase):
    def test_entropy_endpoints_and_error_units(self):
        self.assertEqual(h2(0),0); self.assertEqual(h2(.5),1)
        self.assertAlmostEqual(1-h2(1/3),.08170416594551044)
        self.assertAlmostEqual(1-h2(.1),.5310044064107188)
    def test_all_one_bit_encoders_on_three_bits(self):
        N=3
        for packed in range(1<<(1<<N)):
            table=[(packed>>x)&1 for x in range(1<<N)]
            hm,errs,hconds=code_stats(N,table)
            self.assertLessEqual(sum(1-h for h in hconds),hm+1e-12)
            self.assertLessEqual(sum(1-h2(float(e)) for e in errs),hm+1e-12)
            self.assertLessEqual(N*(1-h2(float(max(errs)))),1+1e-12)
    def test_zero_error_requires_all_bits(self):
        for N in range(1,10): self.assertEqual(N*(1-h2(0)),N)
    def test_public_random_coordinate_code(self):
        # R chooses one coordinate uniformly; message is X_R.
        # Any requested coordinate has average MAP error (N-1)/(2N).
        N=3
        eps=Fraction(N-1,2*N)
        errors=[]
        for j in range(N):
            e=Fraction(0)
            for r in range(N):
                table=[(x>>r)&1 for x in range(1<<N)]
                _,err,_=code_stats(N,table)
                e+=err[j]/N
            errors.append(e)
        self.assertEqual(errors,[eps]*N)
        self.assertLessEqual(N*(1-h2(float(eps))),1)

if __name__=='__main__': unittest.main(verbosity=2)
```

## 附录：冻结stdout

```text
test_all_one_bit_encoders_on_three_bits (__main__.CapacityTests.test_all_one_bit_encoders_on_three_bits) ... ok
test_entropy_endpoints_and_error_units (__main__.CapacityTests.test_entropy_endpoints_and_error_units) ... ok
test_public_random_coordinate_code (__main__.CapacityTests.test_public_random_coordinate_code) ... ok
test_zero_error_requires_all_bits (__main__.CapacityTests.test_zero_error_requires_all_bits) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.003s

OK
```
