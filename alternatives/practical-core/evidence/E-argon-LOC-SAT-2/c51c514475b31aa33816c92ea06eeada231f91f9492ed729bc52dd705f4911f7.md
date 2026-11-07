# H2 repaired：小见证局部约束并不自动继承SAT下界

pnp-sol-a，2026-11-06 21:44；节点E-argon-LOC-SAT-2。分类conditional + 归约资源反例。不是新增SAT或CLIQUE下界，不是现实覆盖认证。

## 0. 新增信息

针对H2“小见证k-clique/2-CSP修复FLMV空间失配”建议，本次给完整收费ND上界及证书枚举引理；构造并执行标准3CNF-occurrence-graph归约，精确展示k不是固定常数、输入变成平方大，以及为什么平方输入让证书装入sqrt(N)工作word的同时使原SAT细粒度下界不再匹配。未重复已解决的OR/COLLISION本体证明。

## 1. 局部k-clique的真正收费上界

设v顶点无向图，用只读显式v×v邻接位矩阵（每格一个word存0/1）表示，头含v,k；输入规模N=Θ(v²)个word。选择w足以存所有合法矩阵地址和中间乘积，所有资源函数在观察答案前冻结。

ND程序逐bit猜k个顶点编号，每个word按已有BRAM paid power-loop生成：6w+2步/编号；检查编号<v并STORE到普通工作数组。拒绝所有越界编号。随后对每一对编号LOAD、比较互异、读取对应矩阵格，要求为1。全部地址有界后才计算/访问。所有选择、保留编号、验证控制、输出均在本体计费；不依赖长只读proof tape或重复独立重猜。

总时间 O(kw+k²) 个普通word步骤（另有完整输入获取、零初始化、乘法位收费），保留空间k·w+O(w+log k) bit，工作数组k words。这里的O常数来自将这些有限循环编成ISA，**尚未给具体完整字节码，不能自称恰落在32N+512的数值Γ内**。

若k固定，则见证Θ(log v) bit；若k=Θ(log v)，见证Θ(log²v) bit，不能笼统称“都装进16w寄存器”。16w=Θ(log v)，还要留控制/地址寄存器。当前profile另外允许M=Θ(sqrt N)=Θ(v)工作word，因此k=O(log v)乃至k≤v可使用普通数组保留，不必免费移出空间账本。适用上界不等于存在全类D下界。

## 2. 小证书枚举引理（不能只缩见证就保留NP难度）

固定确定性验证器V，证明长≤b(n) bit，验证时间t(n)、私有空间s(n)，在共同模型上可读到被实际存储的证明位。用一个b位计数器依次枚举所有证明，重用验证scratch，得到确定性算法：

    时间 O(2^b · (t+b+reset费用)),
    空间 O(s+b+控制位).

推导：每个候选必须是同一固定bit串；计数器/存储真实占b位，每个候选验证前的初始化/状态恢复实际计费；若证书地址访问模型与存储机器不同，还要乘显式模拟访问成本。没有把任意证书查询当免费oracle。

在本文w=O(log n)的普通有效BRAM/标准位机器上，重置可按被访问单元显式模拟并保持多项式开销；特别在b=O(log n)、t多项式时得到P算法。故若一般SAT真有O(log n)见证、多项式时间验证器，会推出P=NP；不是用“SAT小见证已显然存在”修复空间缺口。该条件结论不证明这种验证器绝不存在，也不把P≠NP当既知前提。

同理固定k-CLIQUE可确定性枚举v^k个元组并核k²边；k是固定常数时属于P。若有一般SAT到固定k-CLIQUE的多项式大小、可计算many-one归约，将同样推出P=NP。k=O(log n)则枚举通常只给准多项式上界，不能误说仍是多项式。

注意枚举算法也可能超当前线性fuel Γ；此引理没有否定同资源D/ND分离的可能。已有FNS的COLLISION正是短见证与线性时间/小空间D下界可以并存的例子，但不能把该特定下界的函数名换为任意小见证问题。

## 3. 标准3SAT到CLIQUE：哪里付掉了原预算

给m个3文字clause，各文字变量编号≤O(m)，原编码长度ℓ=O(m log m)；可选择变量数Θ(m)的普通实例族。

图的顶点为所有文字出现位置(ci,literal)，所以v=3m。不同clause的两个顶点之间有边，当且仅当二者文字不是互为否定；同clause不连边。目标clique大小为**k=m**，不是固定k，也不是O(log m)。

正确性：满足赋值可从每clause选一个真文字，任何两者不矛盾，构成m-clique。反向，m-clique因同clause无边而每clause恰选一个文字，且文字不互反，可延拓为一个满足赋值。所有边均由公式实际内容计算，没有把SAT答案放进免费标签。

显式矩阵有9m²个格；构建/输出已需Ω(m²)次格写入，一旦采用该实际矩阵表示不能说归约只做O(ℓ)步。一般索引列表见证长m·ceil log2(3m) bit；利用clause结构压缩为“每clause选0/1/2”可用2m bit（合法性另验），仍不是O(log ℓ)。这只是具体见证编码上界，不宣称任何可能的SAT证书都至少线性长。

令新图输入规模N=9m²。若图机允许M=floor sqrt N=3m工作word，那么k=m个顶点编号确实可装入已收费数组。**这不是魔术小证书：图输入平方扩张本身把sqrt(N)内存提高到了线性m word。**

若图算法耗O(N)时间、O(sqrt N)word空间，其投影回SAT的显式归约+运行约O(m² polylog m)时间、O(m log m)bit工作空间（加归约是否流式/显式保留的额外账本）。这远非原ℓ^(7/5)时间、ℓ^(1/100)空间profile，故现有PPST/FLMV审计中该SAT实例不能直接排除这个图算法。

若不构造矩阵而按需回答邻接，则必须公开这是虚拟输入归约，逐个graph查询需读取/定位原文字；图输入长度、空间、每次查询成本和caller计费全部重新换算。允许局部可计算边并不自动保线性时间/同精确Γ，不能将显式矩阵和虚拟接口的好处混在一张账本里。

本节点只用上述归约的直接证明。关于FLMV已核模型/具体指数，读取共享E-chief-PPST-1证据作已标注来源输入；不声称重新独立核原论文或新增文献下界。主结论不依赖FLMV定理真值：仅由时间/空间数值变大已足以否定所声称的直接同预算蕴含。

## 4. 实验和保留的反例状态

loc_sat_clique_probe_v2.py显式构造全部邻接格，不使用SAT答案建图；对2变量、1..3个3文字clause的8420个公式，及3变量、1..2 clause的3192个公式，逐一核SAT赋值存在与每clause选一文字的clique存在等价，共11612个公式。每图都核v=3m、格数9m²。

结果loc-sat-clique-probe-v2.json全部通过；源码sha256 2a484a5378fd3e64f69182b4722329e23a2d7abffbba8bb6f68e1ac5fe735ced。小实例只核归约语义/计数，没有观察或认证渐近下界。

当前结果：小见证局部问题的ND membership可以完整付费构造，但**SAT下界传递缺口没有被“换成k-clique”自动补上**。一个真实可行下一数学输入是同一新函数/访问模型的D全类下界，或能保持所需指数/空间的明确归约；这些均未由本节点给出。当前模板余值归零，不以不断改k或重复SAT包装算新鲜度。

## 冻结附件：loc_sat_clique_probe_v2.py

```python
"""Explicit 3CNF occurrence-graph reduction; no complexity lower-bound claim."""
from itertools import combinations, combinations_with_replacement, product
import json


def sat(formula, nv):
    return any(all(any(a[abs(l)-1] == (l > 0) for l in c) for c in formula)
               for a in product((False,True), repeat=nv))


def occurrence_graph(formula):
    occurrences = [(ci,l) for ci,c in enumerate(formula) for l in c]
    graph = [[int(ci != cj and li != -lj)
              for cj,lj in occurrences] for ci,li in occurrences]
    return graph


def local_witness(formula, graph):
    # One literal occurrence chosen from each clause, rather than free assignment tape.
    for chosen in product(range(3),repeat=len(formula)):
        ids = [3*i+j for i,j in enumerate(chosen)]
        if all(graph[u][v] for u,v in combinations(ids,2)):
            return True
    return False


counts = {}
for nv,maxclauses in [(2,3),(3,2)]:
    literals = tuple(range(1,nv+1))+tuple(range(-nv,0))
    clauses = tuple(combinations_with_replacement(literals,3))
    count = 0
    for m in range(1,maxclauses+1):
        for formula in product(clauses,repeat=m):
            graph = occurrence_graph(formula)
            assert len(graph) == 3*m
            assert sum(map(len,graph)) == 9*m*m
            assert local_witness(formula,graph) == sat(formula,nv), formula
            count += 1
    counts[f'{nv}-variables'] = count
print(json.dumps({'status':'pass','formula_counts':counts,
                  'total_formulas':sum(counts.values()),
                  'graph_vertices':'3m', 'explicit_adjacency_cells':'9m^2',
                  'required_clique_size':'m, not a fixed constant',
                  'claimed_SAT_or_clique_lower_bound':False,
                  'claimed_reality_coverage':False},indent=2))

```

## 冻结附件：loc-sat-clique-probe-v2.json

```json
{
  "status": "pass",
  "formula_counts": {
    "2-variables": 8420,
    "3-variables": 3192
  },
  "total_formulas": 11612,
  "graph_vertices": "3m",
  "explicit_adjacency_cells": "9m^2",
  "required_clique_size": "m, not a fixed constant",
  "claimed_SAT_or_clique_lower_bound": false,
  "claimed_reality_coverage": false
}

```
