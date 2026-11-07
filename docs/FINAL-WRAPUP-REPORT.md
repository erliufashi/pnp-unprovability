# P/NP 相对不可证性与能力保全受限分离：阶段性收官总报告

- **收官日期**：2026-11-07
- **顶层状态声明**：
  - **T1（ZFC 不证明标准 $P=NP$）**：`UNRESOLVED`（未解决）
  - **T2（ZFC 不证明标准 $P \ne NP$）**：`UNRESOLVED`（未解决）
  - **T3-v1（封闭有限单遍 LLM 代理空间分离与模拟）**：`proved_conditional_proxy`（仅限显式单遍无外存有限 profile 历史记录，**不代表现实任务或人类能力覆盖**）
  - **T3-v2（能力保全算法空间下的同预算分离与现实大多数问题覆盖）**：`UNRESOLVED`（形式化契约、多条紧致能力/信息边界与候选分离已确立，但显式可行阈值、常数错误率随机化下界及外部现实任务抽样实测尚未闭合）

---

## 一、研究演进脉络与四分支总览

本项目围绕三层单向依赖里程碑网络（第 1 层研究方向 $\leftarrow$ 第 2 层工具/引理 $\leftarrow$ 第 3 层可验推导/实验，按当前价值 $C$、预期余值 $R$、衰减新鲜度 $F$ 与邻接信号动态调度，SHA256 锁定不可变证据）经历了四个阶段、共 **127 个里程碑节点**的推进：

| 阶段与目录 | 节点 / 边 | 核心问题 | 阶段收官结论 |
| :--- | :---: | :--- | :--- |
| **1. 标准不可证性主线**<br>`research/` · `notes/` · `proof/` | 25 / 32 | 能否用哥德尔式自指门控计算系统或怪 oracle 证明标准 $P=NP$ 或 $P\ne NP$ 相对 ZFC 不可证？ | 纯门控自指被洛布定理精确剪枝；怪 oracle 卡在标准表示转移（否则推出 $\mathrm{Con}(\text{ZFC})$）；归约为待证的 **SAT 特有反例函数增长引理** |
| **2. 封闭单遍代理（T3-v1）**<br>`alternatives/closed-llm/` | 10 / 11 | 若限制为单遍只读输入 + 固定有限状态预算，能否分离 $D/ND$ 并模拟无外存封闭推理核？ | 单遍 `INDEX` 严格分离成立，条件性代理模拟闭合；但禁重读假设过强，不代表现实问题求解能力 |
| **3. 次线性单遍流深度探索**<br>`alternatives/sublinear-stream/` | 38 / 41 | 能否通过前缀归约树、静态参数剪枝、固定阈值混合将多层因果模型压入次线性状态？ | 给出精确二进参数森林与静态 `selected` 证书剪枝（$3996 \to 752$ 森林），同时构造紧凑 ReLU 检索族证出 $\Omega(2^d)$ 状态硬下界，并揭示固定 $H$ 巨常数非空洞性陷阱 |
| **4. 现实能力保全核心（T3-v2）**<br>`alternatives/practical-core/` | 54 / 88 | 放弃不准确的“200B 参数量”口径，恢复重读、全扫描算术、可复用索引、动态更新与验证闭环后，算法空间如何严格收缩并保持分离？ | 证伪亚线性探针 `OR`、免费只读证明带与黑盒换协议三条伪路线；确立全扫描 BRAM 分离候选（及其 $2^{3315164}$ 维度与 $1/3$ 随机误差两大诚实瓶颈）、CCC 2024 文献修补、非线性索引/动态更新/批验证三条紧界与六维可比性矩阵 |

---

## 二、核心负面剪枝与“伪捷径”证伪（避免无效研究方向）

1. **哥德尔门控自指的精确坍缩（`notes/01-gate-v1.md`, `notes/02-reflection-v1.md`）**
   - 将 $E = (P=NP)$ 置于证明门控 NP 编译器 $L_\sigma$ 的对角化不动点后，算术内部恒等式满足 $\mathrm{Poly}(L_\sigma) \leftrightarrow (\mathrm{Prov}_T(\sigma) \to E)$。对角化所得自指命题 $S$ 在 $T$ 中精确等价于局部反思 $\mathrm{Prov}_T(\ulcorner E \urcorner) \to E$；由洛布定理，$T \vdash S \iff T \vdash E$。因此**任何同类门控不动点包装均不产生超越直接证 $E$ 的新数学力量**。
2. **怪 Oracle 表示依赖与第二不完备定理屏障（`notes/05-models-v1.md`）**
   - 证明阶段构造的稀疏怪 oracle $O$ 虽能制造表示依赖的独立性，但一旦试图将结论转移回标准空 oracle（证明 $O = \emptyset$），在理论内部即蕴含 $\mathrm{Con}(T)$，被哥德尔第二不完备定理直接阻断。
3. **恢复现实基础能力后，旧单遍与亚线性探针路线失效（`E49`, `A57`, `C56`, `ASTRA-CHIEF-CUTOFF-AUDIT-1`）**
   - **一次重读击穿单遍 `INDEX`（`E49`）**：允许收到查询下标后再扫描一次输入，仅需 $O(\log m)$ 工作空间即可零误差解决全部 `INDEX`（$90,114$ 个有限实例核验一致）。
   - **亚线性燃料 `OR` 与全输入 `SUM` 互斥（`A57`, `C56`）**：在可执行有界字长 RAM（`bounded_vm_nd_v1.py`）中，逐位计费指令 `GUESSBIT` 虽能在 $F = 6w+12 = O(\log n)$ 步内严格分离 `ND_OR` 与确定性/随机化程序，但该预算**连最基础的全输入求和 `SUM`（恰需 $7n+9$ 步）和内积 `DOT`（$11n+10$ 步）都无法容纳**；一旦把燃料放宽至 $F \ge 7n+9$，确定性 `OR_SCAN`（$7n+8$ 步）立即消解分离。
   - **充足工作内存下的基数直接寻址逃逸（`ASTRA-CHIEF-CUTOFF-AUDIT-1`）**：在明文 $w$-bit 字输入（值域 $U = 2^w$）上，只要可写内存满足 $M \ge \lceil U/w \rceil + M_{\text{ctrl}}$ 且燃料满足 $F \ge I + N(r+c+u)+O(1)$，确定性直接寻址算法即可精确判定碰撞。
4. **免费只读长证书带与黑盒接口偷换（`E-chief-cert-1`, `C57`, `OPAQUE-v2`, `ASTRA-F`）**
   - **双单调读头恢复整个 $\mathrm{NP}$（`C57`）**：在多项式长度只读证书带上仅设置**两个单向只进读头**，配合 $O(\log n)$ 私有工作空间即可逐行锁步比对计算 tableau 从而刻画整个 $\mathrm{NP}$。这严格堵死了“拿 FLMV 的 $\mathrm{SAT} \notin \mathrm{DTISP}[n^{1.4}, n^{0.01}]$ 配小空间验证器冒充同空间 $D/ND$ 分离”的漏洞；同时小见证归约（`E-argon-LOC-SAT-2`）因 3-SAT 转团的平方输入膨胀 $N = 9m^2$ 亦无法保住 FLMV 指数。
   - **黑盒 `CMP` 与隐藏响应位宽属于信道限制（`E-chief-OPAQUE-1`, `ASTRA-F`）**：仅暴露三值比较 `CMP(i,j)` 虽给出 $\lceil\log_2(n!)\rceil$ 确定性查询下界与 1 次查询 $ND$ 上界，但本质是剥夺了明文位表示；且 `ASTRA-F` 证明若不限制黑盒响应位宽（允许返回 $k$-bit 证书），单次查询成功率即可从 $(q+1)/N$ 跃升为 $1$。

---

## 三、经严格证明与代码核验的正面局部成果

### 1. 标准不可证性主线的精确算术桥（`notes/03-arithmetic-v1.md`, `notes/07-frontier-v1.md`）
- 确立了不依赖门控包装的干净元数学等价桥：对一致递归公理化理论 $U \supseteq \mathrm{PA}$ 与 $\Pi_2$ 命题 $\neg E = (P \ne NP)$，
  $$
  U \vdash \neg E \;\Longleftrightarrow\; \text{对每个标准编码下统一的候选求解器 } M_k,\; \text{存在 } U\text{-可证全函数 } g_k \text{ 使 } \forall n\, W(k, n, g_k(n)) \text{ 为真},
  $$
  即 $U \nvdash (P \ne NP)$ 当且仅当某个实则非多项式时间的算法，其最坏反例出现位置超越 $U$ 的可证递归函数包络（对应无限多输入长度上存在近多项式规模电路线索，`notes/06-growth-v1.md`）。

### 2. 次线性流编译、紧凑神经检索下界与静态特化（`alternatives/sublinear-stream/`）
- **二进前缀参数森林与静态 `selected` 证书剪枝（`PREFIX-FOREST-v1.md`, `SELECTED-PARAMETER-PRUNING-v1.md`）**：在不重结合浮点归约树的前提下，构造对数级块森林并证明“仅需覆盖真实被选中最大值 $m$ 下的分母集合 $Z_{c,m}$（允许未选中分支的反事实分母越界）”即可逐字保持多层因果输出与随机数状态（$54,212$ 次核对照、$2,539$ 步三路策略对比通过，工作森林从 $3,996$ 降至 $752/776$）。
- **紧凑 ReLU 检索族的模型系数下界（`NEURAL-RETRIEVAL-v1.md`, `MODEL-STATE-LOWER-v1.md`）**：用 $O(d)$ 稀疏 ReLU 电路构造精确相等打分与 binary32 下溢归零（$e^{-120}$ 在 IEEE-754 单精度下精确舍入为 `+0.0`），证明通用紧凑模型族若要在单遍流中保持前缀精确（或平均误差 $\le \gamma$），总保留配置位数至少为 $(1 - h_2(\gamma))2^d$（在 $\gamma=1/3$ 下由精确整数不等式 $3^{48} < 2^{77}$ 证得安全系数 $> 1/16$，`FINITE-BUDGET-RANDOM-v1.md`）。

### 3. 全扫描明文 BRAM 同预算分离候选与文献修补（`alternatives/practical-core/`）
- **容纳 `SUM`/`DOT` 的同包络 $D$ vs $ND$ 分离候选（`E-argon-FNS-audit1`, `C62`）**：
  - 在明文有界字长 RAM 包络 $\Gamma(n) = (w=\lceil\log_2(n^2+2)\rceil,\; F=32n+512,\; M=\lfloor\sqrt{n}\rfloor,\; B=4096)$ 下，全输入扫描 `SUM`（$7n+9$ 步）与逐位猜测两下标的 `ND_COLLISION`（$12w+21$ 步，512 字节代码，零免费证明带）均精确落入 $\Gamma(n)$；
  - 将确定性 BRAM 的完整动态配置（含 16 个 $w$-bit 寄存器、$M$ 个工作字、PC 与燃料计数）展开为一般 $[n^2]$-路分支程序，结合 Beame–Saks–Sun–Vee (JACM 2003, Thm 6.13) 排除渐近确定性程序；
  - **诚实量化代价**：`C62` 从 BSSV Cor 5.4(i) 逐步提取出无隐常数的显式有限分离维度 $n = 2^{3,315,164}$；同时 `E-argon-RAND-ED-2` 与 `RAND-BRAM-v2` 证明 BSSV 随机化定理的小误差前提不能直接排除 $\varepsilon=1/3$ 的 $BPP_{\text{BRAM}}$（而朴素随机成对抽样在唯一碰撞输入上从 $n \ge 111$ 起成功率已低于 $2/3$，从 $n \ge 208$ 起低于 $1/3$）。
- **Cook–Moshkovitz (CCC 2024) 顺序多头编码下界的漏洞发现与修补（`C59`–`C61`）**：
  - 核查原文 Lemma 52 时发现其将“unmarking 事件次数”误写为“uncovered 时间步数”且漏计变长转录本前缀编码；`C60` 与 `C61` 独立给出包含完整边界状态与随机游标 $\lceil\log_2(T+1)\rceil$ 位的自包含修补证明，确立确定性与高成功概率随机编码的精确常数下界 $h S_{\text{aug}} T > \delta N^2 / 18432$。

### 4. 现实索引、动态更新、验证闭环与组合工作流的紧致定理（`alternatives/practical-core/`）
1. **可复用非线性索引 × 自适应探针体积界（`ASTRA-E-PARITY-INDEX-1`）**：对 $N$-bit 数据库上的任意二元内积查询族，即便 `Build` 算力无界且索引任意非线性，$s$ 位持久索引配每次查询至多 $q$ 次自适应原位探针必满足
   $$
   2^s \sum_{i=0}^{\min(q,N)} \binom{N}{i} \;\ge\; 2^N,
   $$
   并由二元线性覆盖码给出紧构造（$N=3, s=1, q=1$ 精确达界）。
2. **动态 `SET` 更新的初始持久状态代价（`B56`, `B57`）**：无原数据副本时，支持至多 $U < N$ 次 `SET(i, bit)` 后精确回答 `OR` 的任何确定性摘要，初始状态数紧界恰为 $1 + \sum_{k=0}^U \binom{N}{k}$；容许逐历史端到端错误率 $\varepsilon < 1/2$ 在 $N-1$ 次更新下仍须满足 $b \ge N(1 - h_2(\varepsilon))$。
3. **批量 Generate-and-Verify 精确恢复容量（`D-GVC-BATCH-1`, `D-GVC-STATE-1`, `D-GVC-RETRY-1`）**：$K$ 轮、每轮提交至多 $L$ 个候选的 1-bit 成员验证器（含末尾一次猜测），在任意先验下最优精确恢复概率恰等于前 $F(K,L) = 1 + \sum_{j=0}^{K-1}\min(L, 2^j)$ 个最大先验质量之和（经 $1,022$ 组决策树穷举验证）；并严格区分了仅耗预算的无信息重试与扩大转录本字母表的环境状态泄漏，以及保守预算预留条件与真实轨迹可行性的差异（`astra-argon` 修正）。
4. **自适应组合工作流与防作弊协议矩阵（`COMPOSITION-v1`, `E47`, `E48`, `B54`, `E-CLOSURE-ADVICE-1`, `ASTRA-CHIEF-CONTRACT-MATRIX-1`）**：详见 [`alternatives/practical-core/CONTRACT-v2.md`](../alternatives/practical-core/CONTRACT-v2.md) 与 [`TASK-SPACE-v2.md`](../alternatives/practical-core/TASK-SPACE-v2.md)。

---

## 四、后续可接续的开放问题清单

若未来重启研究，无需重复本阶段已剪枝模板，可直接从以下三个精确切口切入：

1. **常数错误率随机化全扫描 BRAM 下界（纯理论核心缺口）**：在 $\Gamma(n) = (w, F=O(n), M=\lfloor\sqrt{n}\rfloor)$ 明文模型下，寻找适用于 $\varepsilon = 1/3$ 双边错误的 `COLLISION` / `Disjointness` 分支程序姚氏（Yao）硬分布下界（注意须避开 `A-H3-YAO-PROMISE-1` 揭示的公开多重集模和泄漏），或寻找交叉维度 $n_0$ 可实际落地的自然小见证问题。
2. **标准不可证性主线的 SAT 反例增长引理**：围绕 `notes/07-frontier-v1.md` 的 $W(k,n,g(n))$ 判据，探索不经门控自指与稀疏 oracle 转移的电路/证明复杂性反例构造。
3. **冻结强参考系统与现实任务抽样实测**：给定外部冻结的统一 Agent/工具路由器 $B_*$ 与分层任务抽样框 $\nu$，按 `TASK-SPACE-v2.md` 的双层不等式计算首个非零经验覆盖下界。

---

## 五、本地复现与完整性核验

仓库仅依赖 Python $\ge 3.10$ 标准库，无需联网或外部密钥即可在清洁环境中运行全部结构与单元测试：

```sh
# 1. 运行主调度器、扩展分支隔离与权重传播单元测试（38 项）
python3 -m unittest discover -s tests -v

# 2. 校验主线 25 节点图谱与证据 SHA256 完整性
python3 src/research.py --root . check --json

# 3. 校验次线性流分支 38 节点图谱与证据完整性
python3 src/research.py --root alternatives/sublinear-stream check --json

# 4. 校验现实能力保全分支 54 节点共享事务板与全部不可变证据 SHA256
python3 alternatives/practical-core/tools/board_v1.py check
```
