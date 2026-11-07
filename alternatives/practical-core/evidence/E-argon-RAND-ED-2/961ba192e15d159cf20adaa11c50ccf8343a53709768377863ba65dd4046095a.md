# H2 repaired：随机化 FULLSCAN-COLLISION 的原始误差边界与放大预算

pnp-sol-a，2026-11-06 21:40。节点 E-argon-RAND-ED-2。分类：conditional/source audit + counterexamples to proposed transfers。所有初始算法空间、现实覆盖、T1/T2/T3-v2全局仍UNRESOLVED。

## 0. 本次真实增量

不重复旧A57 OR或已交FNS确定性结论。本次核作者原始稿§2.3、§6.2、Thm6.23/Cor6.24，纠正H2建议把误差统一写作2^-Ω(log²n)的方式；给随机化不同错误契约的精确适用表、证明为什么常规放大不能免费代入同Γ，以及一个具体随机采样方案的失败概率/成本公式。未声称解决1/3-error BPP_BRAM全类问题。

## 1. 来源、实际读取与精确公式

Paul Beame, Michael Saks, Xiaodong Sun, Erik Vee, *Time-space tradeoff lower bounds for randomized computation of decision problems*，作者稿2002-10-24；JACM50(2),2003,154–195，DOI10.1145/636865.636867。

作者源：https://www.cs.washington.edu/homes/beame/papers/randomts.ps 。本次只读sol-c已下载完整原稿，不覆盖其文件：PS sha256 38f9bf0da43a21b4073278a24a4e9fade560562544a597818629383c1dc1295a；其本地转换PDF sha256 15081a6737b2c141bdad2a83a8e51835af19884397509d36b10ed3d0cb764a51。

本次读§2.3及Prop2.1完整模型段，§6.2从确定性/ED定义、6.13到随机化6.20–6.24及其证明；独立渲染并目视核原p35（自己的bssv-page35-v2.png）。OCR会丢负号和根号范围，以下以原图为准。没有重新证明全文先前的embedded rectangle机器。

设ED=1表示全distinct，BP总节点数=2^S，时间/长度=T。原稿Thm6.23：存在γ>0，若随机[n²]-way BP对每个输入的错误率

    ε ≤ (T/n)^(-γ(T/n)²),

则

    T = Ω(n sqrt(log(n/S) / loglog(n/S))).

此外若ε≤S/n，则

    T = Ω(n sqrt(log(n/S) · loglog(n/S))).

第二式是根号内乘积，不是第一式的商。原p35第二个公式已直接目视。Cor6.24在原p35–36：对任意δ≥0存在c_δ，对于充分大n，若随机RAM时间≤c_δ n sqrt(log n/loglog n)、错误≤n^(-δ)，则空间至少n^(1−δ)。原图δ=0只是很弱端点，不得把它当1/3常数错误的强下界。

§2.3的随机BP是输入独立分布中的确定性BP，长度/大小是所有非零概率支持成员的最大值；每个输入的成功概率≥1−ε。它至少包含通常带随机节点的模型。Prop2.1只给固定种子后在均匀输入分布上的平均错误≤ε，不给所有输入同时正确。不能用“固定随机种子”偷做一般BPP去随机化。

## 2. 对当前FULLSCAN Γ的正确代入

FNS/C62共同profile为w=ceil log2(n²+2)、M=floor sqrt n、F=32n+512、B4096，含full acquisition、初始化和普通SUM。全部动态状态

    b=(16+M)w+O(log F+log B+log Q+1),

对应总BP规模参数S_BP≤b+O(log(F+1))=O(sqrt n log n)，不是仅M，也不是把log总size误当width。

有随机化时，用每步输入独立随机币并按最多F个时间层固定币序列；允许BP把其作为时间层非统一转移，不免费给被模拟程序额外可读随机存储。完整state及所有实际随机游标仍收费。由此得到原稿随机BP定义允许的分布；input查询仍是整个[n²]值的多路查询，非比较oracle、非单调流。

令a_n=T/n。当前上界a_n≤32+512/n，趋于32（不足下限的T可padding到F并以F检查一个保守条件）。第一个错误门槛对应

    ε_n ≤ a_n^(-γa_n²),

是随常数时间系数决定的很小常数级别，而非强制随n缩小的2^-Ω(log²n)。若取T=Θ(n log n)，该门槛反而约exp(-Θ(log²n·loglog n))，也不是简单漏掉loglog就成立。

第二门槛ε_n≤S_BP/n为O(log n/sqrt n)量级；这是使用源定理时的允许上限条件，不是证明某算法恰有这个错误率。可以在明确选好的配置节点数/空间上界中padding BP再应用定理，但不能靠把S任意扩大到Θ(n)来容许常数错误：那会同时消掉超线性因子。

当保证错误≤n^(-1/4)时，Cor6.24是一个清楚的有效条件路线：当前32n+512最终低于c_(1/4)n sqrt(log n/loglog n)，而S_BP=O(sqrt n log n)=o(n^(3/4))，故充分大n排除这样的随机策略。仍需源常数/数值阈值才能声称某具体有限n验收。

也不能在Cor6.24里事后设δ=log(3)/log(n)把n^(−δ)调成1/3：c_δ和充分大n阈值依赖固定δ，该量词没有给δ随n变化的统一常数。

因此本source可支撑“充分小错误/特定高置信契约下最终排除”，不能把当前允许1/3错误的整个随机Γ直接排除。

## 3. 同预算放大不是免费归约

对每个输入独立重复r次并取多数，ε≤1/3时Chernoff给exp(-Ω(r))；顺序重用scratch可使空间仅增加vote/轮次O(log r)与必要控制（不是r倍空间），但总fuel至少r·T加重置/计票成本，输入重读、随机币生成、初始化/保留日志均需另计。

若试用Thm6.23第一条，放大后要用a'=T'/n≈ra，而不是原a。允许错误变成

    (ra)^(-γ(ra)²)=exp(-γa²r² log(ra)).

标准放大给的保证exp(-Ω(r))并不自动达到这个随r收紧的要求。对每次恰1/3独立错误的示意coin过程，多数错误至少包括“r次全错”事件，故≥3^(-r)；当γ≥1、a≥2时，该值严格大于上述门槛。这里γ=1仅用于明确示意，未冒充源文未给出的最佳γ；即使可换用更保守的合法γ，不能据此断言源定理在别的常数下绝无用处。正确结论是“常规放大+保持原time系数”的推理没有成立，不能把BPP 1/3自动搬入此Γ排除结论。

若改用Cor6.24，以标准独立多数把常数错误可靠压到n^(-δ)，充分的r=Θ(log n)，会把线性算法变成Θ(n log n)，高于Cor6.24只给的n sqrt(log n/loglog n)排除时间范围。此法没有得到所需矛盾；不证明所有可能的特殊放大/新算法都不行。

## 4. 仍然可得的正结论：worst-case bounded零错误

在固定n的有限输入集上，若随机策略对每个输入零错误，且每条可达随机轨迹都满足同Γ的最坏时间/空间/代码预算，则存在一条固定随机带使所有输入均正确。证明：对每个输入错误随机带集合测度0；有限个集合之并仍测度0。固定一条好带并展开为非统一时间层BP，不增长度/状态宽度的量级，故FNS已核的确定性Thm6.13排除它。

此结论不要求把整条随机带免费存成被模拟程序可读ROM；强BP本身允许非统一转移。随机币和游标在原机仍按声明收费。

若“Las Vegas”只有每输入期望时间O(n)，允许少量超Γ轨迹，则不满足上述最坏clock前提；用Markov截断会引入错误，又回到原错误条件。单边有错也不等于双边零错。本报告没有把这些类一并关闭。

## 5. 哈希/采样逃逸建议的一项具体反例

不能由“随机化”直接推出有线性fuel/sqrt n空间的算法；也不能因一个hash方案失败证明全部BPP失败。可精确分析的普通方案是：每轮均匀选m个数组位置，保存其key，再完整扫描输入，只在碰撞涉及已保存key时检测。

对恰一对重复、位置为u,v的输入，单轮命中至少一个重复位置概率恰

    p = 1 - C(n−2,m)/C(n,m)
      = m(2n−m−1)/(n(n−1)) ≤ 2m/n.

K轮此类uniform采样（固定最大K；独立是充分条件）成功率≤2Km/n，由并集界得；要≥2/3需K≥n/(3m)。每轮完整扫描至少n input读取，故该具体方案成本Ω(n²/m)。m≤sqrt n时为Ω(n^(3/2))，不在32n+512最终预算内。

这只排除这个sample-keys+scan方案，不排除任意自适应随机RAM。若用hash值代key，需处理distinct key的假碰撞，并付seed/哈希函数存储和比较原值费用；若允许input-dependent免费索引已换模型。单独F2常数相对误差估计也不能保证区分F2=n和F2=n+2的一对重复，所需分辨率应单列，不能称同一精确任务已解决。

## 6. 本地有限核验与状态

rand_ed_error_probe_v2.py及rand-ed-error-probe-v2.json：43项多数/threshold形状检查、154项采样概率精确Fraction+子集枚举检查通过。没有运行大尺寸ED求解器，没有把小样本当全类下界；γ=1的数值表是标明的示意而非文献数值常数。

源码sha256 aff5c43fd0f4b674d63a861db00372ffbcdfe8a33b5c0393faacfa4181b7922e。作者原p35图、本次layout摘录均在自己的cwd，不修改他人source。

结论：修正H2误差门槛，精确保留确定性/最坏有界零错误/高置信条件结果；1/3-error BRAM COLLISION在此Γ内是否有算法或下界，仍缺匹配的原始定理或具体算法。本节点将当前“直接套6.23+免费放大/采样哈希”模板耗尽；未证明该问题在全部现有文献中开放，检索结果不是无定理存在证明。

## 冻结附件：rand_ed_error_probe_v2.py

```python
"""Exact finite checks of amplification and a sampled-key collision scheme.
Not an ED solver or a general randomized lower-bound experiment.
"""
from fractions import Fraction
from itertools import combinations
from math import comb, log, log2
import json

checks = 0
rows = []
for r in range(1, 42, 2):
    p = Fraction(1, 3)
    majority_error = sum((Fraction(comb(r,j))*p**j*(1-p)**(r-j)
                          for j in range((r+1)//2, r+1)), Fraction())
    assert majority_error >= p**r
    # Illustrative admissible-shaped threshold gamma=1, original T/n=32.
    # Does not supply the unknown constant of BSSV Theorem 6.23.
    neg_log_threshold = (32*r)**2 * log(32*r)
    assert r*log(3) < neg_log_threshold
    rows.append({'repeats': r, 'majority_error': float(majority_error),
                 'neg_log_threshold_gamma1': neg_log_threshold,
                 'neg_log_all_wrong': r*log(3)})
    checks += 2
sample_checks = 0
for n in range(2, 13):
    for m in range(1,n+1):
        subsets = list(combinations(range(n),m))
        hits = sum(0 in s or 1 in s for s in subsets)
        p = Fraction(hits,len(subsets))
        exact = 1-Fraction(comb(n-2,m) if m <= n-2 else 0,comb(n,m))
        formula = Fraction(m*(2*n-m-1),n*(n-1))
        assert p == exact == formula
        assert p <= Fraction(2*m,n)
        sample_checks += 2
# First theorem's error profile depends on time ratio a, not n by itself.
a = 32
assert a*a*log(a) == 1024*log(32)
checks += 1
print(json.dumps({'status':'pass','amplification_checks':checks,
                  'sample_subset_checks':sample_checks,
                  'first_threshold':'a^(-gamma*a^2), a=T/n',
                  'linear_profile_neg_log_threshold_per_gamma':a*a*log(a),
                  'majority_rows':rows,
                  'not_a_BPP_separation_certificate':True},indent=2))

```

## 冻结附件：rand-ed-error-probe-v2.json

```json
{
  "status": "pass",
  "amplification_checks": 43,
  "sample_subset_checks": 154,
  "first_threshold": "a^(-gamma*a^2), a=T/n",
  "linear_profile_neg_log_threshold_per_gamma": 3548.91356446692,
  "majority_rows": [
    {
      "repeats": 1,
      "majority_error": 0.3333333333333333,
      "neg_log_threshold_gamma1": 3548.91356446692,
      "neg_log_all_wrong": 1.0986122886681098
    },
    {
      "repeats": 3,
      "majority_error": 0.25925925925925924,
      "neg_log_threshold_gamma1": 42065.03293256758,
      "neg_log_all_wrong": 3.295836866004329
    },
    {
      "repeats": 5,
      "majority_error": 0.20987654320987653,
      "neg_log_threshold_gamma1": 129924.44966998596,
      "neg_log_all_wrong": 5.493061443340549
    },
    {
      "repeats": 7,
      "majority_error": 0.17329675354366714,
      "neg_log_threshold_gamma1": 271534.75229787844,
      "neg_log_all_wrong": 7.690286020676768
    },
    {
      "repeats": 9,
      "majority_error": 0.14484580602550423,
      "neg_log_threshold_gamma1": 469708.59406439593,
      "neg_log_all_wrong": 9.887510598012987
    },
    {
      "repeats": 11,
      "majority_error": 0.12208504801097393,
      "neg_log_threshold_gamma1": 726527.3571813066,
      "neg_log_all_wrong": 12.084735175349207
    },
    {
      "repeats": 13,
      "majority_error": 0.10353924518431962,
      "neg_log_threshold_gamma1": 1043646.2683997732,
      "neg_log_all_wrong": 14.281959752685427
    },
    {
      "repeats": 15,
      "majority_error": 0.08823159840676366,
      "neg_log_threshold_gamma1": 1422440.3183390063,
      "neg_log_all_wrong": 16.479184330021646
    },
    {
      "repeats": 17,
      "majority_error": 0.07547522609213371,
      "neg_log_threshold_gamma1": 1864085.84431756,
      "neg_log_all_wrong": 18.676408907357867
    },
    {
      "repeats": 19,
      "majority_error": 0.06476617279096288,
      "neg_log_threshold_gamma1": 2369610.887567141,
      "neg_log_all_wrong": 20.873633484694086
    },
    {
      "repeats": 21,
      "majority_error": 0.055722972225529736,
      "neg_log_threshold_gamma1": 2939928.502446806,
      "neg_log_all_wrong": 23.070858062030304
    },
    {
      "repeats": 23,
      "majority_error": 0.048049953563950094,
      "neg_log_threshold_gamma1": 3575859.950394958,
      "neg_log_all_wrong": 25.268082639366526
    },
    {
      "repeats": 25,
      "majority_error": 0.04151367840778967,
      "neg_log_threshold_gamma1": 4278151.5057074735,
      "neg_log_all_wrong": 27.465307216702744
    },
    {
      "repeats": 27,
      "majority_error": 0.03592711844525938,
      "neg_log_threshold_gamma1": 5047487.025621152,
      "neg_log_all_wrong": 29.662531794038966
    },
    {
      "repeats": 29,
      "majority_error": 0.03113863847737628,
      "neg_log_threshold_gamma1": 5884497.599767751,
      "neg_log_all_wrong": 31.859756371375184
    },
    {
      "repeats": 31,
      "majority_error": 0.027024092727195248,
      "neg_log_threshold_gamma1": 6789769.11984718,
      "neg_log_all_wrong": 34.056980948711406
    },
    {
      "repeats": 33,
      "majority_error": 0.023481011664539357,
      "neg_log_threshold_gamma1": 7763848.327767961,
      "neg_log_all_wrong": 36.25420552604762
    },
    {
      "repeats": 35,
      "majority_error": 0.020424235845777412,
      "neg_log_threshold_gamma1": 8807247.724804297,
      "neg_log_all_wrong": 38.45143010338384
    },
    {
      "repeats": 37,
      "majority_error": 0.017782577730797954,
      "neg_log_threshold_gamma1": 9920449.611102995,
      "neg_log_all_wrong": 40.648654680720064
    },
    {
      "repeats": 39,
      "majority_error": 0.015496230356429767,
      "neg_log_threshold_gamma1": 11103909.449647695,
      "neg_log_all_wrong": 42.84587925805628
    },
    {
      "repeats": 41,
      "majority_error": 0.013514729298644005,
      "neg_log_threshold_gamma1": 12358058.697457952,
      "neg_log_all_wrong": 45.0431038353925
    }
  ],
  "not_a_BPP_separation_certificate": true
}

```

## 冻结附件：bssv-p35-36-layout-v2.txt

```text
occurring in earlier sets. For T 2 G, let w(T ) be the number of Sj that intersect it. Since each Sj 2 F ,
 1 P w(T )  4p, so at most half of the T 2 G have w(T ) > 8p. Let G0 be the set of T 2 G with
jGj T
w(T )  8p. Thus jG0 j  jGj=2.
    We now upper bound the number of elements in G0 and thus G. An element T of G0 can be described
by giving a subset J  [p℄ of (1 8)p indices such that T \ Sj = ; for all j 2 J and then specifying
T as an m-subset of the elements outside these subsets. By the claim, any collection of (1 8)p ofthe
sets has a total of m(1 8)p  N=9 elements since   24  1 . Therefore jGj  2jG0 j  2 p 8N=9 <
                                                                                         8p m
21+H2 (8)N=(3m) (8=9)m Nm and thus (R)  23+H2 (8)N=(3m) (8=9)m .
Theorem 6.23. There is a constant > 0 such that any randomized [n2 ℄-way branching program com-
               ℄n ! f0; 1g in time T and size 2S with probability of error at most (T=n) (T=n)2 re-
puting ED : [n2p
quires T = (n log(n=S )= log log(n=S )). Furthermore, any randomized [n2 ℄-way branching program
computingpED : [n2 ℄n ! f0; 1g in time T and size 2S with probability of error at most S=n requires
T = (n log(n=S ) log log(n=S )).
Proof. By Proposition 2.1, it sufﬁces to prove the lower bound for deterministic branching programs that
approximate ED within error .
    Choose n to be a sufﬁciently large integer. We will apply the second part of Corollary 5.4 and to this
                                                                                                 2
end, we assume without loss of generality that k  8 and deﬁne for q1 = 2 40 k 8 , and r = dq1 5k e. There
                                                                   2
is a constant > 0 such that for all positive   (k 2) (k 2) and k  8, H2 (8)  16 log2 1 
 1        32k2 and 4k  1 . Fix such a and assume that   (k 2) (k 2)2 .
16 (32k)          1=e  24
   Let B be a deterministic branching program of length at p
                                                           most (k 2)n and size 2S that approximates
                                            0
ED within . We will show that for some > 0, k          0  log(n=S )= log log(n=S ). If n < r2 this is
                           2
immediate, so assume n > r .
   Applying Corollary 5.4(ii) and the fact that ED is 1 for least a 1=e fraction of all inputs in [n2 ℄ and
                                                                                                    1=2
1=e  > 1=4, we obtain a balanced rectangle R with m = m(R)  q12k2 n=2 and (R)  2 Sr q1 m 5
                                           4k  1 of inputs in R by our assumption on . Applying
such that ED is 0 for at most a fraction (1=e )  24
                                                                 H2 (8) 2                              2
Lemma 6.20, we have that (R)  8(8=9)m=2 maxf1; (8=9)m=2 2 3 n =m g. Now n2 =m  4mq1 4k 
             2              2
4m(240 k8 )4k = 4m(32k)32k so
                                       H2 (8)                    4H (8)      2
                          (8=9)m=2 2     3       n2 =m
                                                      2 m=12+ 23 m(32k)32k
                                                                                 2
                                                      2 m3 (1=4 4H2 (8)(32k)32k )
                                                      1
since H2 (8)  16  1 (32k) 32k2 . Therefore (R)  8(8=9)m=2  23 m=12 . Combining the upper and
                                                                   1=2
lower bounds on (R) and simplifying we get 2Sr  2m=12 q1 m 8 , which, for n sufﬁciently large and
k satisfying the restrictions above, is at least 2m=13 . From this we deduce S  13mr  r 1 q12k2 n=26 which
                     2                                                                          0
is at least 0 n=k 1 k for some
                            p 0 ; 1 independent of n and k . It follows that for some constant > 0 and
sufﬁciently large n, k  0 log(n=S )= log log(n=S ).
                                                                2
     Also observe that our conditions on  hold for  = r 1 q 2k =26 which is our lower bound on S=n and
                                                              1
from this the second part of the theorem follows.

Corollary 6.24. For any Æ  0 there is a constant Æ such that for n sufﬁciently large any randomized RAM


                                                         35
                                                                        p
algorithm for element distinctness on inputs in [n2 ℄ taking at most Æ n    log n= log log n time and having at
most n Æ error requires at least n1 Æ space.


Hamming Closeness

Lemma 6.25. If (R; A1 ; A2 ) is an n-variate embedded rectangle over [N ℄ with jA1 j = jA2 j = m such that
               1 fraction of x 2 R have HAM (x) = 1 then
at most an  < 24
                                                                                 1
                       (R)  8(36N )m=2 maxf1; (N =36)m=2 23H2 (8)N                 =m g:

Proof. As in the proof of Lemma 6.20 but replacing the condition ED (x) = 0 with HAM (x) = 1 we ﬁnd
two collections of m-subsets of [N ℄, F and G, such that jF j; jGj  (R)=4 N    m and for each T 2 F at most
a 4 fraction of T 0 2 G have the property that there exist t 2 T and t0 2 T 0 such that H (t; t0 )  log2 N .
    Let d = N =3 where the value of = ( ) is given by Proposition 6.16. By Proposition 6.22, if
  (R) > 8(36N )m=2 > 8(4(d 1)=d2 )m=2 then F contains p = dN=(dm)e sets S1 ; : : : ; Sp such that
each set Sj has at most m=2 elements occurring in Si for i < j .
    As in the proof of Lemma 6.20, prune G to obtain a set G0 with jG0 j  jGj=2 such that each element
T 0 2 G is -close to at most 8p of S1 ; : : : ; Sp . We can describe a set T 0 in G0 by naming the (1 8)p
sets Si from which it is -far and then specifying each element in T 0 from among the elements that are -far
from these sets. The (1 8)p sets together contain at least mp=3  N=(3d) = N 1 elements of [N ℄ and
so by Proposition 6.16 at most N 1 elements of [N ℄ are -far from these sets. Therefore
                                                                                      
                                                N1
                    jGj  2jG0j  2 8pp         m
                                                          21+3H2 (8)N 1 =m N       m   N
                                                                                         m
and thus   (R)  8N     m 23H2 (8)N 1   =m from which the lemma follows.

    Although the parameters in this lemma make it appear stronger than Lemma 6.20, the value of N for
which we will need to use it is much larger than in the case of element distinctness and we will only be able
to obtain lower bounds for much smaller error. It is conceivable that a much stronger result holds since (1)
the collection of sets S1 ; : : : ; Sp in Proposition 6.22 was chosen to maximize the unions of subcollections
rather than to maximize the number of elements that are -close to these subcollections, and (2) no use was
made of the property that each set in F and G must only contain elements that are -far from each other.

Theorem 6.26. Let 0 < < 1=2 and  2=(1 H2 ( )). Any randomized [n ℄-way branching program
computing HAM : [n ℄n ! f0; 1g in time T and size 2S with probability of error at most n2 requires
T = (n log( n log n
               S )).

Proof. By Proposition 2.1, it sufﬁces to prove the lower bound for deterministic branching programs that
approximate HAM within error  = n2 .
     Choose n to be a sufﬁciently large integer. Let k  4 and let B be a deterministic branching program of
length at most (k 2)n and size 2S approximates HAM within . Therefore the branching program B 0 ,
set to be B with the labels of its two sink nodes swapped, approximates :HAM within .
    We will show that for some 0 > 0, k  0 log((n log n)=S ). Let = ( ) > 0 be the constant
from Proposition 6.16. If k  ( log2 n)=32 then we are done so assume without loss of generality
that 2k < n =32 . Let r = 2k+6 k 2 and apply Corollary 5.2(ii) to B 0 to obtain a balanced rectangle R

                                                      36

```
