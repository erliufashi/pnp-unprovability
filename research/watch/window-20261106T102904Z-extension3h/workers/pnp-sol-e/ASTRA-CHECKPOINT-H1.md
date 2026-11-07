# Astra E checkpoint H1 — E-CLOSURE-ADVICE-1

时间：2026-11-06 23:46 Asia/Shanghai。身份 `pnp-sol-e`，独占 cwd；mail 已手动配置 `paused/followUp/60`。上层 ACTIVE 的更早硬截止为 2026-11-07 01:29:04+08:00，我不把用户消息中的 04:00 当作延期授权。

## 选择与板操作

- 已读 `TEAM-CONTRACT-v1.md`、`current-contract-v2.json`、`ACTIVE.json`、window state 和共享三层板。
- `next` 无可用未占用叶；已新增并 claim `E-CLOSURE-ADVICE-1`（layer 3），父层为 M21/M22/M23，操作分别为 `astra-e-add-closure-v1`、`astra-e-claim-closure-v1`。
- 该节点不重复已完成的 `E-argon-IDX-audit1`：后者规定单一 Build 的允许观察视图/标签非干涉；本节点审计**组合闭包**：即便每个组件输出单独在分布上不泄漏，联合辅助状态仍可泄漏，且固定描述预算下闭包不能免费增长。

## 研究结论（条件性局部结果）

1. **联合统计独立不是逐组件统计独立的自动推论（不反驳已有逐币强非干涉）。** 对独立均匀值 `Y,R∈{0,…,2^m−1}`（Y 是隐藏目标，R 是共享掩码），组件分别输出 `Y⊕R` 与 `R`。单独观察任一组件对 Y 的最优猜测率为 `2^-m`，联合观察恢复 Y 的成功率为 1。因而算法空间契约必须对联合输出、缓存、路由元数据和跨调用持久状态作整体观察/非干涉声明；只审计每个工具的局部字段白名单不够。
2. **描述预算必须计入组合选择/配对/路由。** 长度≤b的二进制描述共有 `2^(b+1)-1` 个，而精确长度 b+1 的字符串已有 `2^(b+1)` 个；所以“每个成员≤b”并不推出无预算的组合闭包。若闭包允许组合，必须明确新增描述位、代码/权重/索引/序列化成本以及是否可复用；不能把组合器或路由器视为免费。
3. **d-bit selective advice 的有限模型核验。** 对均匀 m-bit 隐藏值，仅保留 d 个高位的 advice，最优恢复率恰为 `2^d/2^m`；d=0 到 m 均做穷举。该式只是信息容量 sanity check，不是计算分离。
4. **安全核的边界。** 若输出确实只依赖公开输入与声明的独立随机币，而不触达隐藏标签，则在给定公开输入后，联合输出仍不额外依赖隐藏值；但这需全生命周期 capability/provenance 审计，不能从“Build 可计算”推出。

## 可复核证据

- `probe_closure_advice_v1.py`：普通 shell/任意 cwd 兼容的 Python 3.13 stdlib 程序。
- `closure-probe-results-v1.json`：实际命令 `env -i PATH=/run/current-system/sw/bin /run/current-system/sw/bin/python3 probe_closure_advice_v1.py` 返回 `status: pass`。
- 覆盖：XOR 8 个 m 值（总行数 4 至 65536）；有限泄漏映射穷举 860 个；d-bit 紧性 44 个；描述闭包 b=1..12；安全核 16 行。
- 源 SHA-256：`04013a4af3033b60421d29bd639dc9dad2b8ca656cdd9e8303bba8daf1a87903`。

## 严格边界

这是 `proved-candidate` 级局部审计候选，不是 T3-v2、现实覆盖、标准 P/NP 分离或人类能力保全证书。有限穷举没有证明真实编译器/物理成本/数据分布。仍需：冻结联合算法类型与计费向量；证明组合器、元数据、缓存、持久状态均纳入预算；在同一 Build/Query 权限下核对真实能力保全；再讨论任何分离。

## 完整推导与可消费契约 v1

### A. 固定描述球不是无条件闭包：语义不可能定理

固定确定性解码器 U、固定环境 e 和相同输入 x0。令 C_b 为所有能由长度至多 b 的二进制程序产生的确定性行为；程序可含字符串常量，但 e 中不许藏入随程序增长而未计费的库/文件/参数。每个停机程序在 x0 上只有一个有限输出。因此 C_b 在 x0 上至多有 2^(b+1)−1 种输出。

假设 C_b 包含一个输出非空字符串 s 的程序，且对任意两个成员的**输出拼接**闭包仍留在 C_b：存在成员在相同 x0 上输出二者输出的拼接。反复拼接得到 s,s²,s³,…，长度不同，因而输出两两不同。这与有限描述数矛盾。故任意非空输出常量能力加任意次输出拼接，不可能在同一有限描述球中完全闭包。即使不计运行时间，这一矛盾已经成立。

限制：不是说每一个具体 pair 都必然需要更长最短程序（压缩可能成功），也不是说函数**复合**的每个有限集合都不闭合；例如常值零函数的单元素集合对函数复合闭合。证明针对包含非空常量、任意多次配对/拼接的能力要求。引入最大输出长度或调用次数可消除该前提，但此时闭包类型改变，必须披露。允许未计数的外部环境增长则不是原 C_b。

### B. 修复为有等级/有预算的闭包，而非禁止组合能力

采用固定的一段解析器、解释器和组合标签作为环境，给它们一个只付一次但显式记录的描述预算 c_U。一个可自行分界的程序列表可编码为

`tag || 1^k 0 || (1^|p1| 0 p1) || ... || (1^|pk| 0 pk)`。

这里 tag 固定 c_tag 位，k 为程序个数。额外描述长度**恰为**

`c_tag + (k+1) + Σ_i (2|p_i|+1)`，

再加环境 c_U。解码后逐一运行并拼接结果给出完全可计算的组合器（这里只给描述构造，不声称已实现高性能编译器）。可改用更紧自分界编码，但不能把长度字段、k 或路由代码删除。若程序含固定库引用，须同时冻结库版本/内容及地址宽度；共享库可全局只计一次，但未计共享库的“本地小代码”不能当完整算法描述上界。

正确契约是 `Comp:C[b1,r1]×...×C[bk,rk] -> C[B_comp,R_comp]`，允许预算随组合变化；欲留在统一上限 (B*,R*)，必须另验 B_comp≤B* 和 R_comp≤R*。时间包括调度、调用、读取、输出/复制；工作空间包括同时存活缓冲、解释器与路由状态。若中间结果能流式输出或复用存储，可以据具体语义减账，不能预先一律取 max。此处未证明任何近线性编译开销或任意 RAM 指令的位成本。

这保留“可以组合”的现实能力，但拒绝“无成本无上限组合”。对固定有限 reference portfolio，可逐组件构造一个预算内统一策略；这不是对所有未来 portfolio 的免费闭包保证。

### C. 联合预处理独立性的确切反例与修复

Y、R 独立均匀 m-bit。设 A=Y XOR R，B=R。对任意 y,a 有 Pr[A=a|Y=y]=2^-m，对任意 y,b 有 Pr[B=b|Y=y]=2^-m，故 Y 与 A、Y 与 B 分别独立。然而 Y=A XOR B，联合猜测成功率 1。两个程序都是固定、短且输入规模一致的程序；冻结代码和预处理时间先后都没有使它们成为合法的隐藏标签输入渠道。

该反例是**单组件输出分布独立性**不闭包，不是对 IDX 的强非干涉引理的反驳：固定共同随机币 r 后，A(y,r) 随 y 改变，所以 A 本就不满足“固定合法视图及随机币、替换秘密仍输出不变”的逐币非干涉。把“分布上不泄漏”和“逐币强非干涉”混称会误判已有结果。

令 V 为全部合法共同观察，H_i 为第 i 次输出后的完整联合可见历史。若对每个正概率 v,y,h，下一输出的条件核均满足

`Pr[Z_i=z | V=v,Y=y,H_(i-1)=h] = K_i(z | v,h)`，

则展开联合概率为 `Pr[Y=y|V=v] × Π_i K_i(z_i|v,z_<i)`，得到 `Y ⟂ H_k | V`。这是逐历史、条件于已有联合历史的核保证；自适应调用次数的决定若只依赖 V,H 和独立币，也作为核的一部分计入终止符即可。无限循环或未声明终止时间不在有限 transcript 定理内。

XOR 反例中第一个输出虽满足独立性，但第二个在给定第一个后不满足该核条件。共享随机币不是“每次都与已有历史条件独立”的免费资源。一个充分实施条件是：整个组合程序只接触 V、固定代码和与 (Y,V) 联合独立的随机源；隐藏的种子、cookie、预装权重、服务端状态若另带标签相关信息，必须纳入总输入/视图审计。

此条件是来源/信息流规则，不是要求合法索引与答案无相关。若答案本就是 V 的确定性函数，则所有信息论猜测下界退化为 1，完全不能阻止昂贵计算或推出算法困难。

### D. 代码选择与 advice 的完整容量界

对有限 Y,V 定义

`Pguess(Y|V) = Σ_v max_y Pr[Y=y,V=v]`。

给任意相关辅助变量 Z，若给定每个 v 后 Z 至多 K 种可能，则

`Pguess(Y|V,Z) ≤ min(1, K·Pguess(Y|V))`。

证明：对每个 v,z，`max_y Pr[y,v,z] ≤ max_y Pr[y,v]`；每个 v 求和至多 K 项，再对 v 求和。无需 Z 独立、均匀或确定性，故它也覆盖依赖标签的程序选择。这是平均条件最优猜测率，不是逐 v 的无条件熵声明。

若有 d-bit **固定宽度**选择串，K≤2^d。若为任意长度≤d的裸二进制串且长度可见，K≤2^(d+1)−1，不能错写2^d；若采用前缀自由编码且所有长度≤d，则 Kraft 给 K≤2^d。变长消息的长度、停止标志及可见时间若未包含于 Z，不能援引这个 K。

紧性：Y 均匀 m-bit，d≤m，Z 为 Y 的前 d 位，每个 Z 后有2^(m−d)个等可能 Y，故最优成功率2^(d−m)。把 Z 移到程序常量、程序 ID、权重文件、路由配置或“预处理选择的实现”不改变它作为可见 advice 的角色；代码选择过程本身须有合法来源且付费。

多组件时应给**联合**可见变量的基数上界（固定 d_i 位串总上界2^Σd_i），不能因每个边际互信息为0就把总泄漏记0。XOR例的联合形式恰是反例。容量界也不等于现实能力界：它只约束未知 Y 的信息获取，不刻画给定公开输入后的计算难度。

### E. 需要冻结的六项契约

1. 总环境：解释器、库、权重、服务、raw data、缓存与可见反馈的内容/版本/来源。
2. 算法描述类型：裸码还是前缀码；代码选择和 router 是否可依赖任务实例/标签；所有元数据如何计数。
3. 组合闭包类型：允许次数、输出类型和变化后的预算；不是宣称同一个固定球免费闭包。
4. 合法观察 V 与秘密/测试标签 Y 的边界；每步核对完整历史，或逐币强非干涉的可组合实现。
5. Build/Query 的共同权限与全生命周期资源；两边同预算方可谈分离。
6. 能力保全需另给统一 reference 模拟和真实分布证据；本文不补造这两项。

### F. 复现、版本与审计边界

owner pnp-sol-e，版本 v1。稳定发现通过共享 board 节点及其 immutable evidence 引用；不是部署新系统或新消费 CLI。现有 board CLI 未修改。正文推导是主要证据，下面封存完整 finite-control 源与实际 JSON 结果，消费者不依赖 agent 私有环境或临时缓存。用 Python 3 标准库将源码块保存后运行即可；校验脚本失败会非零退出。已实际以空环境普通进程运行，未做独立同行验收，也未核任何桌面/网络服务（本产物不涉及这些接口）。如需更正，只另发 v2、保留原 hash，不覆盖引用证据。

#### Frozen probe source

```python
#!/usr/bin/env python3
"""Finite negative controls for E-CLOSURE-ADVICE-1. Stdlib only; fail nonzero."""
import json
from collections import Counter
from fractions import Fraction
from itertools import product


def pguess(rows, obs):
    counts = Counter((tuple(row[i] for i in obs), row[0]) for row in rows)
    groups = {}
    for (v, y), count in counts.items():
        groups[v] = max(groups.get(v, 0), count)
    return Fraction(sum(groups.values()), len(rows))


def main():
    xor = []
    for m in range(1, 9):
        n = 1 << m
        rows = [(y, r, y ^ r) for y in range(n) for r in range(n)]
        base = pguess(rows, [])
        assert base == pguess(rows, [1]) == pguess(rows, [2]) == Fraction(1, n)
        assert pguess(rows, [1, 2]) == 1
        xor.append({'m': m, 'rows': len(rows), 'single_guess': str(base), 'joint_guess': '1'})
    # Enumerate ALL deterministic leaks of alphabet K, not just one chosen function.
    capacity_cases = 0
    for n in range(1, 6):
        for k in range(1, 4):
            for weights in (tuple(range(1, n + 1)), (1,) * n):
                base = Fraction(max(weights), sum(weights))
                for f in product(range(k), repeat=n):
                    rows = [(y, f[y]) for y in range(n) for _ in range(weights[y])]
                    assert pguess(rows, [1]) <= min(1, k * base)
                    capacity_cases += 1
    # Tight d-bit selective-code/advice example, including d=0 and full disclosure.
    tight_cases = 0
    for m in range(1, 9):
        n = 1 << m
        for d in range(m + 1):
            rows = [(y, y >> (m - d)) for y in range(n)]
            assert pguess(rows, [1]) == Fraction(1 << d, n)
            tight_cases += 1
    # Finite semantic constant class: all bitstrings length <= b. Each component
    # is admitted, but concatenating two length-b outputs exits for every b>=1.
    closure = []
    for b in range(1, 13):
        a = '0' * b
        assert len(a) <= b and len(a + a) > b
        # Generic finite code-count obstruction: <=d-bit raw codes have <2^(d+1)
        # possibilities, whereas strings of exact length d+1 have 2^(d+1).
        assert sum(1 << i for i in range(b + 1)) < 1 << (b + 1)
        closure.append(b)
    # Adaptive safe kernel: outputs depend on public v and fresh coins only.
    safe = [(y, v, v ^ r, (v ^ r) ^ s)
            for y, v, r, s in product(range(2), repeat=4)]
    assert pguess(safe, [1, 2, 3]) == pguess(safe, [1])
    print(json.dumps({'status': 'pass', 'xor_cases': xor,
                      'capacity_exhaustive_maps': capacity_cases,
                      'tight_code_selection_cases': tight_cases,
                      'finite_closure_cases': closure,
                      'safe_kernel_rows': len(safe),
                      'limits': 'finite controls only; no implementation compiler, physical budget or real coverage certification'}, indent=2))


if __name__ == '__main__':
    main()

```

#### Actual probe output

```json
{
  "status": "pass",
  "xor_cases": [
    {
      "m": 1,
      "rows": 4,
      "single_guess": "1/2",
      "joint_guess": "1"
    },
    {
      "m": 2,
      "rows": 16,
      "single_guess": "1/4",
      "joint_guess": "1"
    },
    {
      "m": 3,
      "rows": 64,
      "single_guess": "1/8",
      "joint_guess": "1"
    },
    {
      "m": 4,
      "rows": 256,
      "single_guess": "1/16",
      "joint_guess": "1"
    },
    {
      "m": 5,
      "rows": 1024,
      "single_guess": "1/32",
      "joint_guess": "1"
    },
    {
      "m": 6,
      "rows": 4096,
      "single_guess": "1/64",
      "joint_guess": "1"
    },
    {
      "m": 7,
      "rows": 16384,
      "single_guess": "1/128",
      "joint_guess": "1"
    },
    {
      "m": 8,
      "rows": 65536,
      "single_guess": "1/256",
      "joint_guess": "1"
    }
  ],
  "capacity_exhaustive_maps": 860,
  "tight_code_selection_cases": 44,
  "finite_closure_cases": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12
  ],
  "safe_kernel_rows": 16,
  "limits": "finite controls only; no implementation compiler, physical budget or real coverage certification"
}

```
