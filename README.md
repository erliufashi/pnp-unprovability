# P/NP 相对不可证性与能力保全受限分离研究

> **核心结论状态（诚实披露）**
> - **标准主目标 T1 / T2（标准 $P=NP$ 或 $P \ne NP$ 相对 ZFC 不可证）**：**`UNRESOLVED`（未解决）**。
> - **现实受限目标 T3-v2（能力保全算法空间下的同预算分离与现实大多数问题覆盖）**：**`UNRESOLVED`（未解决）**。
> - **早期封闭代理目标 T3-v1（单遍无外存有限状态代理空间）**：`proved_conditional_proxy`（仅作显式单遍假设下的历史条件性记录，不代表现实问题或人类能力覆盖）。

本仓库采用**三层单向依赖动态里程碑网络**（第 1 层正交方向 $\leftarrow$ 第 2 层引理/工具 $\leftarrow$ 第 3 层可验推导与实验探针；按价值、预期余值、新鲜度与邻接信号动态调度，SHA256 锁定不可变证据），系统探索了哥德尔自指不可证性路线与能力保全受限算法空间分离路线，现已完成阶段性整理收官（累计 **4 个隔离分支、127 个里程碑节点**）。

---

## 快速阅读入口

- **[阶段性收官总报告（推荐首读）](docs/FINAL-WRAPUP-REPORT.md)**：完整汇总四个分支的正负面数学结论、伪路线剪枝、文献漏洞修补、紧致信息界与剩余开放问题
- **[结构化收官摘要 JSON](reports/final-wrapup-summary.json)**：机器可读的四分支状态、代表性定理/反例索引与验证记录
- **分阶段目录导航**：
  1. **主线 ZFC 不可证性（25 节点）**：[`proof/MAIN.md`](proof/MAIN.md) · [`proof/obligations.json`](proof/obligations.json) · [`notes/ROUND-1.md`](notes/ROUND-1.md)（`notes/01`–`07`）
  2. **封闭单遍代理 T3-v1（10 节点）**：[`alternatives/closed-llm/README.md`](alternatives/closed-llm/README.md) · [`docs/EXTENSION-T3.md`](docs/EXTENSION-T3.md)
  3. **次线性单遍流编译与检索下界（38 节点）**：[`alternatives/sublinear-stream/README.md`](alternatives/sublinear-stream/README.md) · [`window-final-v1.md`](alternatives/sublinear-stream/reports/window-final-v1.md)
  4. **现实能力保全核心 T3-v2（54 节点）**：[`alternatives/practical-core/README.md`](alternatives/practical-core/README.md) · [`CONTRACT-v2.md`](alternatives/practical-core/CONTRACT-v2.md) · [`TASK-SPACE-v2.md`](alternatives/practical-core/TASK-SPACE-v2.md)

---

## 阶段性核心产出摘要

1. **严格剪枝三条高迷惑性“伪捷径”**
   - **门控自指坍缩**：将 $P=NP$ 置于证明门控编译器不动点后精确退化为局部反思 $\mathrm{Prov}_T(\ulcorner E\urcorner)\to E$，被洛布定理封死；怪 oracle 转移回标准空 oracle 则蕴含 $\mathrm{Con}(T)$ 撞上第二不完备定理。
   - **单遍/亚线性探针与基础能力互斥**：允许一次重读即可用 $O(\log m)$ 空间解全部 `INDEX`；在有界字长 RAM 上靠亚线性步数分离 `OR` 会导致连全输入 `SUM`（$7n+9$ 步）都无法包含，放宽至全扫描后 `OR` 分离即消失。
   - **免费只读长证书与黑盒接口偷换**：多项式长只读证书上仅放**两个单调只进读头**配 $O(\log n)$ 空间即可恢复整个 $\mathrm{NP}$（堵死用免费证书套用低空间 SAT 下界）；黑盒 `CMP` 的 $\lceil\log_2(n!)\rceil$ 下界在明文足够内存下被 $O(n)$ 直接寻址击穿。
2. **确立正面局部边界、候选分离与文献修补**
   - **全扫描明文 BRAM 分离候选与显式瓶颈**：在 $M=\lfloor\sqrt{n}\rfloor, F=32n+512$ 下同时精确容纳全扫描 `SUM`/`DOT` 与 `ND_COLLISION`，并由 BSSV (JACM 2003) 排除渐近确定性 BRAM；同时诚实导出其显式交叉维度高达 $n=2^{3,315,164}$ 且 $\varepsilon=1/3$ 随机化下界尚未闭合。
   - **CCC 2024 文献漏洞修补**：发现 Cook–Moshkovitz (CCC 2024, Lemma 52) 混同 unmarking 事件与 uncovered 时间步的计数漏洞，独立给出确定性与随机化多头顺序编码的自包含修补下界 $h S_{\text{aug}} T > \delta N^2 / 18432$。
   - **索引、动态更新与验证闭环紧界**：证明非线性可复用索引体积界 $2^s\sum_{i\le q}\binom{N}{i}\ge 2^N$、支持 $U$ 次 `SET` 更新的初始状态紧界 $1+\sum_{k\le U}\binom{N}{k}$、批量 1-bit 验证紧容量 $F(K,L)=1+\sum_{j<K}\min(L,2^j)$，以及六维 `INVALID_COMPARISON` 合同检查矩阵。

---

## 本地校验与复现（仅依赖 Python $\ge 3.10$ 标准库）

```sh
# 1. 稳定 CLI 入口（任意工作目录可用，区分 T3-v1 历史代理与 T1/T2/T3-v2 当前 UNRESOLVED 状态）
pnp-research --help
pnp-research mission status --json
pnp-research practical check --json

# 2. 仓库内标准库测试与四分支完整性核验（38 项单元测试）
python3 -m unittest discover -s tests -v
python3 src/research.py --root . check --json
python3 src/research.py --root alternatives/closed-llm check --json
python3 src/research.py --root alternatives/sublinear-stream check --json
python3 alternatives/practical-core/tools/board_v1.py check
```

系统规则与调度公式见 [`docs/SYSTEM.md`](docs/SYSTEM.md)，操作与快照恢复说明见 [`docs/OPERATIONS.md`](docs/OPERATIONS.md)。测试与记账校验通过仅证明工程与证据完整性，不代表顶层数学猜想已解决。
