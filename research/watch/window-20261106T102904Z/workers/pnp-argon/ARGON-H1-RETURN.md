# pnp-argon H1 有界发散审查交回报告（含 v2 合同与 Round 26 新叶增量审计）

- **审计员身份**：`pnp-argon`（`project:pnp-research`, `window:20261106t102904z`, `role:divergent`）
- **绝对截止时间**：`2026-11-07T01:29:04+08:00`（epoch `1793986144.3940156`，严格遵守不延长）
- **会话与 Mail 状态修复核验**：
  1. 已执行 `mail_identity(action="configure_watch", mode="paused", delivery="followUp", pollIntervalSec=60)` 并持久化；
  2. 已将私有目录 `/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/.pi/settings.json` 中的 `agentMail.enabled` 设为 `true`（未改动全局配置）；
  3. 已调用 `mail_identity(action="claim", agentId="pnp-argon", forceTakeover=true)` 重新绑定会话租约（保持心跳但 `mode=paused` 不自动抢先触发回合）；
  4. 已手动读取主题群 `#pnp-7h-20261106` 最新 v2 通知、个人收件箱（0 封待处理），并在群内及向 `pnp-chief` 发送了原子 `notice` 交回。

---

## 一、 v2 合同与 Round 26 新增 7 节点（16 → 23 节点）增量审计

在首轮 `round1-audit-v1.md`（针对 Round 14 前 16 个节点：D8/D9, M21–M24, E47–E53, B54, C55, A56）的基础上，本轮重点审计了 `current-contract-v2.json`（`goal_spec_revision: 2`）及新增的 7 个第三层叶节点：

### 1. 已完成新叶（5 个 `done`）的价值与模型盲区

| 节点 ID | 作者 / 分类 | 已确立的核心结论（经 SHA256 证据核验） | 暴露的深层盲区 / 下一阶段缺口 |
| :--- | :--- | :--- | :--- |
| **E-chief-cert-1** | `pnp-sol-c` (`conditional`) | 严格区分 read-once 证书（对应 NL）与 two-way 只读证书（通过完整计算 tableau 恢复整个 NP）；给出全证书存储 $O(c+s)$ 与懒一致性字典 $O(q \log c)$ 的真实空间开销，并用 $(z)\land(\neg z)$ 反例证伪“按需独立重猜”。 | 证明了小空间验证器不能免费变成同空间 NTM，但未给出当工作空间受限于 $M = o(n)$ 而允许 $O(n)$ 全输入扫描时，哪些自然问题拥有真正的短证书 $O(\log n)$ 同空间 ND 算法。 |
| **E-chief-dom-1** | `pnp-sol-a` (`proved-candidate`) | 实现可执行有界 word-RAM（`bounded_vm_v1.py`，含 16 个 $w$-bit 寄存器、$M$ 个工作字、只读 `INPUT`/`DATA`、显式 `bit_charge`），证明原生 `SUM`（$7n+9$ 步）、`DOT`（$11n+10$ 步）零开销精确包含，以及 $k$ 带确定性 TM 的显式付费编译。 | 将静态初始化 `DATA` 字节与程序代码 `code` 合并计入同一个单次预算上限 $B$，且未区分**跨任务摊销的只读预计算索引 `DATA_idx`** 与单次查询步数 $F$，导致大容量知识库/代码库的 $O(\log N)$ 检索无法在合理单次 $F$ 下表达。 |
| **A57** | `pnp-sol-a` (`proved-candidate`) | 在 BRAM 上扩展逐 bit 计费指令 `GUESSBIT`（`bounded_vm_nd_v1.py`），证明在 $\Gamma=(w, F=6w+12, M=0, B=512, O=1)$ 下 `ND_OR` 恰需 $6w+12$ 步，而确定性 $D$ 必读 $n$ 次、随机化需 $\ge n(1-2\epsilon)$ 次，实现同预算严格分离；同时证明该亚线性预算**无法包含全输入 `SUM`（需 $7n+9$ 步）**，而放宽到 $F \ge 7n+8$ 后 `OR_SCAN` 消除了该分离。 | **极其关键的转折点**：A57 用严密反例证明了“靠卡亚线性输入读取（$F = O(\log n)$）制造的 `OR` 分离与全输入基础能力（`SUM`/`DOT`）互斥”。下一步必须回答：**当预算放宽到 $F \ge 11n+10$（足以完整包含 `SUM` 和 `DOT`）时，如何在同一个 BRAM($\Gamma$) 上证明严格的 D vs ND 分离？** |
| **C56** | `pnp-sol-c` (`conditional`) | 在结构化 $m=2^k$ 随机访问数组上独立构造了无免费长证书的 `OR` 同预算分离（ND 猜 $k$ 位地址 $O(k^2)$ 时间/$O(k)$ 空间 vs D 需 $m$ 次探针、随机需 $m/3$ 次），并系统列出全量加载、允许全扫描、预计算摘要对子线性见证的消解。 | 与 A57 共同封闭了“亚线性探针 `OR`”路线，明确指出下一义务是**在允许全输入扫描（Full Input Scan）和付费可复用预处理之后**寻找同预算分离候选。 |
| **C57** | `pnp-sol-c` (`proved-candidate`) | 证明在同一个多项式长度只读证书上仅放置**两个独立单调只进读头（Two Monotone Heads）**配合 $O(\log n)$ 私有空间即可通过相邻行锁步比对恢复整个 $\text{NP}$（$\text{V}_{\text{2mono}} = \text{NP}$），堵死了“每个游标只读一次就等于 NL”的协议漏洞。 | 揭示了多游标/可重开句柄对证明带的隐式空间放大；同样需要在交互式工具/外部测试器场景下审计类似的“多轮重放隐式状态”。 |

### 2. 正在执行中的新叶（2 个 `leased`）审计
- **`E-chief-compose-1`**（`pnp-chief` 持有租约）：研究自适应调用组合闭包与“工具 benchmark 平均误差小、但自适应多步流程全错”的反例。
  - **Argon 补充诊断**：除错误率累积外，自适应组合还有两个关键维度值得关注：① **正向放大（Generate-and-Verify）**：当组合中的下游组件是高 soundness 的确定性验证器 $V$（如编译器/类型检查/解核验器）时，$K$ 次自适应重试会将单次成功率 $p$ 放大为 $1-(1-p)^K$；② **环境隐式状态泄漏**：若被调用的工具/环境跨调用保留可变状态，自适应调用序列会绕过主控机器的本地内存限制 $M$。
- **`E-chief-PPST-1`**（`pnp-sol-b` 持有租约）：查证 PPST（Paul–Pippenger–Szemerédi–Trotter）多带线性时间分离及 SAT 时间-空间下界的原始模型限制。
  - **Argon 补充诊断**：PPST $\text{DTIME}(n) \subsetneq \text{NTIME}(n)$ 高度依赖**顺序多带图灵机的磁头局部移动拓扑（无随机访问 RAM）**。在 `E-chief-dom-1` / `A57` 的随机访问 BRAM 模型中，PPST 的块移动与图压缩论证不能直接套用；若要在 BRAM 上获得允许 $\Theta(n)$ 全扫描的同预算分离，更直接且自包含的武器是**有界工作空间 $M = o(n)$ 下的二元匹配/碰撞问题（如 `2-SUM` / `Element Distinctness` / `Disjointness`）**。

---

## 二、 剔除已覆盖项后提出的 3 个真正新节点（供自主选用）

对照 Round 26 已有节点，我们在首轮拟议的 4 个节点中，剔除了已被 `E-chief-cert-1`/`A57`/`C56`/`E-chief-compose-1` 部分覆盖的内容，提炼出 **3 个直击当前瓶颈、完全不依赖未提供外部实测数据的可检验新节点**（JSON 规范已保存于 `/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/proposed-nodes-round1-v2.json`）：

### 1. `E-argon-FNS-1` — 全输入扫描（$F \ge cn$）下的精细同预算分离：`2-SUM` / 碰撞检测在有界内存 BRAM 下的 D vs ND 鸿沟
- **层级与依赖**：Layer 3 $\to$ `M22`, `M23`
- **建议参数**：`current=0.92, remaining=0.92, novelty=1.0, confidence=0.88, cost=0.9`
- **解决的核心矛盾**：
  - `A57` 证明了当预算 $F = 6w+12$ 时，`ND_OR` 与 `D` 分离，但连 `SUM`（需 $7n+9$ 步）都无法包含；而一旦将预算放宽到 $F = 11n+10$（足以完整包含 `SUM`、`DOT`、`OR_SCAN` 等全部线性扫描基础算子），`OR` 的 D/ND 分离立即消失。
  - **新构造方案**：在同一个允许完整扫描输入的预算包络 $\Gamma = (w, F = cn + d, M, B, O)$（其中 $c \ge 12$，完整包含原生 `SUM`、`DOT`、`OR_SCAN`）下，考察**成对相等/互补检测问题 `COLLISION_n` 或 `2-SUM_n`**（给定 $n$ 个 $w$-bit 字 $x_0, \dots, x_{n-1}$，判定是否存在 $0 \le i < j < n$ 使得 $x_i = x_j$ 或 $x_i + x_j \equiv target \pmod{2^w}$）：
    1. **ND 同预算上界（$O(\log n)$ 步，远小于 $cn$）**：`ND` 机器仅需用 $2w$ 次 `GUESSBIT` 猜出两个下标 $(i, j)$（存入寄存器），检验 $0 \le i < j < n$，然后执行 2 次 `INPUT` 随机读取 $x_i, x_j$ 并比较，总步数仅为 $12w + O(1) \ll cn$，工作内存 $M = 0$！
    2. **D / 随机化下界（在 $M = o(n/K)$ 工作字与 $K$ 遍扫描/受限步数下）**：即使允许完整读取输入 $K$ 遍（$F = K \cdot cn$ 步），只要可写工作内存 $M$（含寄存器与可写外存字）满足 $M \cdot w = o(n / K)$，由多轮流式集合不相交/碰撞通信下界（在无预排序输入上），任何确定性或有界错误随机化算法都无法在 $F = K \cdot cn$ 步、$M$ 工作字内解决 `COLLISION_n` / `Disjointness_n`。
- **验收标准**：在 `bounded_vm_nd_v1.py` 上实现 `ND_COLLISION`（验证 $12w+O(1)$ 步与 $M=0$），给出固定 $M$ 与线性步数 $F \ge 11n+10$ 下同时包含 `SUM`/`DOT` 且严格分离 `D-BRAM(Γ)` 与 `ND-BRAM(Γ)` 的自包含证明。

### 2. `E-argon-GVC-1` — 可执行 Generate-and-Verify（验证器引导重试）闭环与环境隐式状态信道审计
- **层级与依赖**：Layer 3 $\to$ `M21`, `M22`
- **建议参数**：`current=0.90, remaining=0.90, novelty=0.98, confidence=0.90, cost=0.85`
- **解决的核心矛盾**：
  - `A57` 和 `C56` 指出，`ND` 的存在性接受（猜中见证概率 $2^{-w}$）不是物理可执行求解器；而现实代理之所以能用受限模型解决复杂任务，核心在于**可执行验证闭环（Generate-and-Verify：候选生成器 $G$ + 确定性验证器 $V$ 如编译器/单元测试/约束检查器 + $K$ 次有界重试）**。
  - 同时，若验证环境 $V$ 在多轮重试间保留状态或返回针对隐藏数据的 1-bit 反馈，代理即使本地可写内存 $M=0$，也能在 $K = \lceil \log_2 m \rceil$ 轮交互内通过二分探测恢复 $m$ 位秘密（已在 `argon_probe_v1.py` 核验）。
- **验收标准**：
  1. 在 BRAM 框架下证明闭环策略 $\text{Loop}_K(G, V)$ 的精确资源包络（步数 $\le K(F_G + F_V) + O(K)$，空间 $\max(M_G, M_V)$）与成功率放大公式 $1 - (1 - (1-\eta_V)p)^K - K\epsilon_V$；
  2. 给出环境跨轮反馈对切状态熵界 $B$ 的修正引理 $B_{\text{eff}} = B_{\text{local}} + \sum_{t=1}^K \lceil \log_2 |\mathcal{R}_t| \rceil$ 及无状态重置（Stateless Reset）计费准则。

### 3. `E-argon-IDX-1` — 摊销预计算索引（`DATA_idx`）与单次查询预算的二阶段 BRAM 合同
- **层级与依赖**：Layer 3 $\to$ `M22`, `M23`
- **建议参数**：`current=0.88, remaining=0.90, novelty=0.95, confidence=0.88, cost=0.85`
- **解决的核心矛盾**：
  - `E-chief-dom-1` 将只读初始化 `data` 字节直接加进单次程序描述预算 $B$，而 `C55` Trap B 与 `B54` 证明若允许任意大的静态 `data` 表则会把测试集答案表硬编码进去。
  - 现实工程中，代码库符号表、B-tree 索引、RAG 倒排表既不是“零字节免费 oracle”，也不是“针对测试题答案硬编码的作弊表”，而是**由统一、答案无关的确定性预处理算法 $\text{Build}(\text{Corpus}) \to \text{DATA}_{\text{idx}}$ 在受限预处理燃料 $F_{\text{prep}}$ 内生成的结构化索引**。
- **验收标准**：
  1. 定义二阶段 BRAM 合同 $(\Gamma_{\text{prep}}, \Gamma_{\text{query}})$：要求 $\text{DATA}_{\text{idx}}$ 必须由固定小代码 $B_{\text{builder}}$ 在 $F_{\text{prep}}(N)$ 步内从原始语料确定性生成（从而彻底排除 B54/C55 Trap B 中不可计算的真值表注入）；
  2. 在 `bounded_vm_v1.py` 中实现有序索引二分查找 reference（`BINSEARCH`），证明在预处理排序/建表后，在线查询仅需 $F_{\text{query}} = O(\log N)$ 步与 $M=0$ 工作空间即可精确检索，而在未建索引的动态对抗输入上仍需 $\Omega(N)$ 步。

---

## 三、 本机已验证探针与产物清单（Provenance & Unknowns）

1. **本轮在独占 `cwd`（`/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/`）保留的完整文件**：
   - `ARGON-H1-RETURN.md`：本次运行权威交回报告（本文件）。
   - `round1-audit-v1.md`：首轮针对前 16 节点的详尽审计与 4 条局部引理推导。
   - `proposed-nodes-round1.json` & `proposed-nodes-round1-v2.json`：首轮及对齐 v2/Round 26 后的新叶节点 JSON 规范（可直接供 `board_v1.py add --spec` 使用）。
   - `argon_probe_v1.py` & `argon-probe-v1.json`：标准库验证脚本（4/4 测试通过，耗时 0.000s，验证交互式反馈信道、验证-搜索工作量比、多遍扫描空间下界 $m/K$ 与 Anytime 置信序列半径）。
2. **明确未知项与边界**：
   - 标准数学主目标 T1/T2（ZFC 下明确一侧 $P=NP$ 或 $P \ne NP$ 不可证）及新目标 `T3_v2` 均保持 **UNRESOLVED**；
   - 真实人类任务分布 $\nu$、分层权重与外部大模型端到端实测数据仍属缺失外部输入；
   - 本发散研究员不直接写共享板，所提 3 个新叶节点已通过 `#pnp-7h-20261106` 主题群与 `pnp-chief` 邮件交回，由三位 Sol 与 chief 自主选用。
