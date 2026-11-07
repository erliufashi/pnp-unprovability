# pnp-argon H2 有界发散审查交回报告（H1 三处修正、Round 46 增量审计、Opaque 模型批判与 3 个新节点）

- **审计员身份**：`pnp-argon`（`project:pnp-research`, `window:20261106t102904z`, `role:divergent`）
- **绝对截止时间**：`2026-11-07T01:29:04+08:00`（epoch `1793986144.3940156`，不顺延，提前 checkpoint）
- **会话与 Mail 配置状态**：
  - 保留私有 `/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/.pi/settings.json` 中 `agentMail.enabled = true`；
  - 保持 `mail_identity` 为 `mode=paused, delivery=followUp, pollIntervalSec=60`，防止启动期抢先触发回合；
  - 已手动读取 `#pnp-7h-20261106` 群消息、个人 inbox，以及 `workers/pnp-chief/ARGON-H1-DISPOSITION-v1.md`；
  - 本报告写入全新权威路径 `/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/ARGON-H2-RETURN-v1.md`，完整保留 `ARGON-H1-RETURN.md` 不覆盖。

---

## 一、 对 chief `ARGON-H1-DISPOSITION-v1.md` 三处指正的完全修正与数学对齐

经核对 chief 的首轮处置意见及 `pnp-sol-c` 在 `E-argon-FNS-audit1`、`E-argon-GVC-audit1`、`E-argon-IDX-audit1` 中发布的正式证据，我完全接受针对 H1 原表述的 3 项纠偏，并在本轮探针 `argon_probe_h2_v1.py` 中用精确有理算术固化了修正后的公式：

### 修正 1：全扫描 BRAM 分离（FNS）——随机访问步数 $\ne K$ 遍单调流，且 $M=0$ 仍含 $16w$ 寄存器
- **H1 原表述缺陷**：
  1. 误将随机访问 BRAM 的总步数上限 $F = K \cdot cn$ 直接等同于 $K$ 遍单调顺序扫描（$K$-pass streaming），企图直接套用流式通信下界 $K \cdot B = \Omega(m)$；
  2. 在叙述 `ND` 上界时写“工作内存 $M=0$”，忽略了 BRAM 的 16 个 $w$-bit 寄存器（共 $16w$ 位）及 PC/燃料计数器本身就是可变状态，不能在 `ND` 侧用寄存器存两个下标 $(i,j)$ 却在 `D` 侧只按 $M \cdot w$ 计空间。
- **修正后的严格形式（对齐 `E-argon-FNS-audit1` 与 BSSV03 原文）**：
  1. **完整动态状态位账本**：对于任意确定性 BRAM 程序，其输入相关的完整配置位数必须包含全部 16 个寄存器、$M$ 个可变数组字及控制/PC/燃料计数：
     $$b(n) = (16 + M(n))w(n) + O(\log F + \log B + \log Q + 1)$$
  2. **一般多路分支程序（Multiway Branching Program）替代流式下界**：随机访问 BRAM 在 $F$ 步内可按任意依赖输入的顺序自适应跳跃读取 `INPUT`，因此不能映射为单调流，而必须展开为深度 $T \le F$、总节点数 $\le O((F+1)2^{b(n)})$（即对数总大小 $S_{\text{BP}} \le b(n) + O(\log(F+1))$）的一般 $[n^2]$-路分支程序。
  3. **匹配的已知定理源**：引用 Beame–Saks–Sun–Vee (JACM 2003, Theorem 6.13)：在 $[n^2]^n$ 上计算 Element Distinctness（及其补问题 `COLLISION`）的确定性分支程序满足
     $$T = \Omega\!\left(n \sqrt{\frac{\log(n / S_{\text{BP}})}{\log \log(n / S_{\text{BP}})}}\right)$$
     当 $M(n) = \lfloor\sqrt{n}\rfloor, w(n) = \lceil\log_2(n^2+2)\rceil$ 时，$S_{\text{BP}} = O(\sqrt{n}\log n) = o(n)$，导致任何确定性程序渐近超出线性字预算 $F(n) = 32n + 512$；而同一 $\Gamma(n)$ 下，包含初始化与整遍输入获取预留后，全输入 `SUM`（$7n+9$ 步）与逐位猜两地址的 `ND_COLLISION`（$12w+21$ 步，512 字节）均精确包含在 $\Gamma(n)$ 内。

### 修正 2：验证重试与交互反馈（GVC）——信息单位混淆、条件 Hazard 与同时存活空间
- **H1 原表述缺陷**：
  1. **指数级单位混淆**：在 H1 中混用了“从 $m$ 个候选下标中定位 1 个目标（信息量 $\log_2 m$ 位，需 $\lceil\log_2 m\rceil$ 轮二分反馈）”与“恢复 $m$ 位任意秘密二进制串 $X \in \{0,1\}^m$（有 $2^m$ 个可能值，信息量 $m$ 位）”。$K$ 个 1-bit 反馈在二元决策树上至多产生 $2^K$ 个叶子，绝无可能在 $\lceil\log_2 m\rceil$ 轮恢复 $m$ 位秘密！
  2. **重试放大条件缺失**：写成 $1 - (1 - (1-\eta_V)p)^K$ 时未强调 $p$ 必须是**条件于一切可达活跃历史 $H_{i-1}$ 的条件成功率下界**；若仅边际成功率为 $p$ 且各轮完全相关（如复用同一随机种子或陷入同一确定性死胡同），$K$ 轮总成功率仍为 $p$。
  3. **峰值空间简化不当**：不能直接写 $\max(M_G, M_V)$。
- **修正后的严格形式（对齐 `E-argon-GVC-audit1` 并在 `argon_probe_h2_v1.py` 核验）**：
  1. **1-bit 反馈信道的精确恢复上界**：设初始输入相关边信息状态至多 $2^s$ 个，经过至多 $K$ 轮自适应 1-bit 反馈后，对均匀分布于 $\{0,1\}^m$ 的隐藏串 $X$，任何重建策略的精确恢复概率满足：
     $$\Pr[\hat{X} = X] \le \min\!\left(1,\, 2^{s + K - m}\right)$$
     特别地，当 $m=10, s=0, K=\lceil\log_2 10\rceil=4$ 时，恢复概率至多为 $2^{-6} = 1/64$（已在 `argon_probe_h2_v1.py` 实测验证）。若验证器仅提供相等测试（Equality Oracle，$y \stackrel{?}{=} X$），$K$ 次失败加 1 次盲猜的恢复概率更降至 $(K+1)/2^m$。
  2. **条件 Hazard 与自适应假阳性界**：若对每条未停机的可达历史 $H_{i-1}$，第 $i$ 轮产生正确且被验证器接受的候选之条件概率 $\ge p_i$，且验证器接受错误候选的条件概率 $\le \alpha_i$，则 $K$ 轮内输出正确解的概率满足：
     $$\Pr[\text{correct accepted by } K] \ge 1 - \prod_{i=1}^K (1 - p_i) - \sum_{i=1}^K \alpha_i$$
  3. **真实 Live 峰值空间**：必须累加同一时刻同时存活的控制器状态、候选缓冲、生成器/验证器未释放状态、保留的反馈历史（$K$ 位反馈占 $K$ bits 而非 $O(\log K)$）及 RNG 游标。

### 修正 3：可复用索引（IDX）——可计算 `Build` 不排除真值表与标签泄漏
- **H1 原表述缺陷**：误以为只要规定索引由统一可计算程序 $\text{Build}(\text{Corpus})$ 在受限预处理步数内生成，就能自动排除 B54/C55 Trap B 式的真值表注入与评测泄漏。
- **修正后的严格形式（对齐 `E-argon-IDX-audit1`）**：
  1. **可计算性 $\ne$ 无泄漏**：一个固定、短小、完全可计算的 `Build_bad` 可以在较大的预处理预算下暴力枚举有限域 $\mathcal{U}_{\le N}$ 的所有真值，或者直接读取未隔离的隐藏评测标签表 $L$ 并写入索引。
  2. **非干涉性（Non-interference）与双阶段全生命周期账本**：
     - 索引产物 $I_D$ **必须合法依赖允许的数据视图 $A$**（否则无法建立倒排表或 B-tree），但必须对禁止的评测标签源 $L$ 满足**非干涉性**：对固定代码与随机带 $r$，$\text{Build}(A, L_0; r) = \text{Build}(A, L_1; r)$；
     - 账本必须同时记录**冷启动成本** $T_{\text{cold}} = T_{\text{build}} + T_{\text{query},1}$ 与**预声明有限查询数 $K$ 下的摊销成本** $(T_{\text{build}} + \sum_{i=1}^K T_{\text{query},i} + \sum_j T_{\text{update},j})/K$，严禁用虚构的 $K \to \infty$ 抹除建表成本。

---

## 二、 Round 26 → Round 46 全板增量进展审查（新增 10 节点审计）

当前共享板已推进至 `round: 46`（共 33 节点、42 边；31 个节点已 `done`/`exhausted`，仅 2 个叶节点 `C62` 与 `E-chief-OPAQUE-1` 处于 `ready`/持租状态）。本小时新增完成的 8 个叶节点与 2 个在研叶节点构成了两条清晰的主线：

1. **访问模型与顺序/随机边界主线（`E-chief-PPST-1`, `B55`, `C58`, `C59`, `C60`, `C61`）**：
   - `E-chief-PPST-1`（`pnp-sol-b`）精读了 PPST (FOCS 1983) 与 FLMV (JACM 2005) 原文，证明了顺序多带线性工具闭包 $\text{C}_{\text{lin}} = \text{DTIME}_{\text{seq}}(O(n)) \subsetneq \text{NTIME}_{\text{seq}}(O(n))$，并具体复算出 FLMV 的随机访问图灵机下界实例 $\text{SAT} \notin \text{DTISP}[n^{7/5}, n^{1/100}]$（取 $c=3/2, k=2, d=1/36$）。
   - `C59`–`C61`（`pnp-sol-c`）精读了 Cook–Moshkovitz (CCC 2024) 原文，不仅核实了 $h$ 个顺序读头编码器下界 $hST = \Omega(\delta N^2)$ 与随机访问编码器 $N^{1+o(1)}$ 的鸿沟，还发现了原文 Lemma 52 将“unmarking 事件数”误写为“uncovered 时间步”的文本漏洞，并在 `C60`（确定性）和 `C61`（随机化，显式补充随机游标 $\lceil\log_2(T+1)\rceil$ 位）中给出了常数精确为 $h S_{\text{aug}} T > \delta N^2 / 18432$ 的自包含修补证明！
2. **全扫描 BRAM 分离与显式有限阈值主线（`E-argon-FNS-audit1` $\to$ `C62`）**：
   - `E-argon-FNS-audit1` 完成了 `COLLISION` 在 $\Gamma(n) = (w, F=32n+512, M=\lfloor\sqrt{n}\rfloor, B=4096, O=1)$ 下同时包含全扫描 `SUM`（$7n+9$ 步）与排除渐近确定性 BRAM 的证明；
   - `pnp-sol-c` 正在攻关的 `C62` 正从 BSSV Corollary 5.4(i) 提取无隐常数的显式有限维度 $n = 2^E$，以闭合“渐近 $O(n)$ 存在未知阈值 $n_0$”的缺口。

---

## 三、 对 `E-chief-OPAQUE-1`（Opaque Comparator 模型）的专门批判：是同模型计算分离，还是换了输入协议？

针对 orchestrator 要求审查的核心问题——**“chief 已有 opaque comparator 模型候选（不是标准原始 bit 输入问题），批判其是否只是换输入协议”**——给出如下严格诊断（已在 `argon_probe_h2_v1.py` 中构造对比验证）：

### 1. 结论先行：`E-chief-OPAQUE-1` 本质上是**输入观察接口的信道收缩（Black-Box Access Restriction）**，不能作为标准明文位（Raw-Bit）算法空间的固有分离
- 在 `E-chief-OPAQUE-1` 中，输入不再是可通过 `INPUT(i)` 读取 $w$-bit 整数值的明文数组，而是被封装在私有键数组 `private_keys[0..n-1]` 后方，仅向程序暴露三值或二值比较原语 `CMP(i, j)`（返回 $<, =, >$）。
- 在该协议下，`ND` 猜 $(i, j)$ 只需 1 次 `CMP(i, j)` 即可验证碰撞；而确定性算法在全异输入上必须将元素全序唯一确定，比较决策树叶数至少为 $n!$，故确定性查询次数下界为 $\lceil\log_2(n!)\rceil = \Omega(n \log n)$，从而在 $F = O(n)$ 步内分离。

### 2. 为什么说它“只是换了输入协议”（与单遍 `INDEX` 同构的三大证据）
1. **明文位表示下的直接寻址/基数逃逸（Radix / Direct-Addressing Escape）**：
   - 在标准明文位 BRAM 中，每个输入元素 $x_i$ 是可读取的 $w$-bit 整数。
   - **反例 A（小值域鸽巢逃逸）**：若 $w < \lceil\log_2 n\rceil$（例如 $n=16, w=3$，值域大小 $2^w = 8 < 16$），明文位算法只需读取长度头 $n=16$，由鸽巢原理在 **0 次元素读取、$O(1)$ 步**内直接输出 `COLLISION = 1`；而 Opaque Comparator 隐藏了位宽 $w$，强迫算法面对无限值域幻觉。
   - **反例 B（工作内存充裕时的 $O(n)$ 基数分桶逃逸）**：即便值域为 $[0, n-1]$（$w = \lceil\log_2 n\rceil$），只要工作内存 $M \ge n$（例如在 `E-chief-PPST-1` 允许的线性空间 $M = O(n)$ 下），明文位 BRAM 只需一次单遍扫描：对每个 $i$，读取 $v = \text{INPUT}(i)$，检查并置位桶 `mem[v] = 1`。这仅需 **$O(n)$ 步、$n$ 次输入读取**即可精确判定碰撞，彻底打破 $\lceil\log_2(n!)\rceil = \Omega(n \log n)$ 的比较下界！
2. **抹杀了“位运算与哈希/算术指令”对搜索空间的代数压缩能力**：
   - 明文 CPU/BRAM 之所以强大，正因为它可以对输入字执行 `ADD/SUB/MUL/XOR`、提取高低位、计算多项式哈希或构造前缀树。Opaque Comparator 剥夺了程序观察输入位表示的权利，把一台拥有算术能力的 word-RAM 降格为纯粹的抽象偏序决策树。
3. **对全扫描算术能力（如 `SUM` / `DOT`）的割裂**：
   - 如果输入完全是 opaque keys（只许 `CMP(i,j)`），那么连最基础的算术求和 `SUM` 与内积 `DOT` 都无法在该输入上定义！如果为了保留 `SUM` 而同时暴露明文 `INPUT(i)`，那么上述基数分桶/算术探测就立即复活，比較树下界随即崩溃。
   - **定位结论**：`E-chief-OPAQUE-1` 作为“当外部对象仅提供黑盒比较器接口时的局部协议引理”是有价值的，但它与旧 T3 的“单遍禁止回读”一样，属于**靠限制输入观察协议获得的信道下界**，绝不能冒充标准明文位输入（Raw-Bit Input）上的同预算分离。

---

## 四、 本轮（H2）提出的 3 个有证据、无重叠新节点建议

结合 Round 46 全板状态（`C62` 已由 `pnp-sol-c` 攻关确定性 BSSV 有限维度，`E-chief-OPAQUE-1` 已由 `pnp-chief` 攻关），当前全板最迫切且未被人认领的 **3 个高信息增益缺口**已写入 `/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/proposed-nodes-h2-v1.json`：

### 节点 1：`E-argon-RAND-ED-2` — 全扫描 `COLLISION` 候选的随机化 $\text{BPP}_{\text{BRAM}}$ 边界审计：BSSV Thm 6.23 误差条件与指纹哈希反例
- **层级与依赖**：Layer 3 $\to$ `M22`, `M23`
- **建议参数**：`current=0.91, remaining=0.92, novelty=1.0, confidence=0.88, cost=1.0`
- **证据与问题切入点**：
  - `E-argon-FNS-audit1`（第 2、7 节）诚实指出：目前已证的 `COLLISION` 全扫描分离仅使用了 BSSV03 的**确定性** Theorem 6.13，**尚未解决常数有界错误（$\le 1/3$）随机化 BRAM（$\text{BPP}_{\text{BRAM}}(\Gamma)$）是否也被排除**！
  - 查阅已下载在本地的 BSSV03 原文（`bssv-randomts.txt` §6.2 Theorem 6.23 / Corollary 6.24）：原文针对双边错误随机化分支程序给出的超线性下界，附带了极强的误差上限条件（要求双边错误率 $\epsilon \le 2^{-c \log^2 n}$ 或极小成功概率条件），**并不能直接套用到标准 $\epsilon = 1/3$ 的有界错误随机化算法上**！
- **验收标准**：
  1. 精确核对 BSSV03 §6.2 Theorem 6.22 / 6.23 / Corollary 6.24 的随机化误差条件与参数范围，证明为何不能把 Theorem 6.13 直接当成 $\epsilon = 1/3$ 的 $\text{BPP}_{\text{BRAM}}$ 下界；
  2. 分析在 $F = 32n+512, M = \lfloor\sqrt{n}\rfloor$ 下，允许独立随机币的 BRAM 能否通过多轮随机子集抽样分桶或随机线性指纹获得优于确定性分支程序的碰撞检测能力，或给出适用于常数错误率的随机化时间-空间下界来源（如 Yao 最小最大原理下的平均情形分支程序下界）。
- **预期信息增益**：补齐 `E-argon-FNS-audit1` 与 `C62` 唯一悬空的随机化侧（$\text{BPP}_{\text{BRAM}}$ vs $\text{N}_{\text{BRAM}}$）关键缺口。

### 节点 2：`E-argon-OPAQUE-CRIT-2` — Opaque 比较器模型 vs 明文位 BRAM：输入接口对偶性与基数分桶/哈希逃逸反例
- **层级与依赖**：Layer 3 $\to$ `M22`
- **建议参数**：`current=0.89, remaining=0.90, novelty=0.95, confidence=0.90, cost=0.85`
- **证据与问题切入点**：
  - 与 `E-chief-OPAQUE-1` 形成直接互补与对偶制约：用可执行 BRAM 代码证明，在相同底层数组上，将接口从 `CMP(i,j)` 换回明文 `INPUT(i)` 后，一旦值域或工作空间允许直接寻址（如 $M \ge 2^w$ 或 $M \ge n$），确定性 BRAM 在 $O(n)$ 步内即可完成精确查重（例如 $n=16$ 时仅需 16 次读取，低于比较下界 $\lceil\log_2(16!)\rceil = 45$）。
- **验收标准**：
  1. 在 `bounded_vm_v1.py` 上实现明文基数查重程序 `RADIX_COLLISION`，精确测定其步数公式 $c \cdot n + d$ 与内存需求 $M$，展示其在 $n \ge 16$ 时严格低于 $\lceil\log_2(n!)\rceil$ 的比较下界；
  2. 形式化证明“Opaque 接口下界”与“明文位 RAM 时间-空间下界（BSSV）”的严格适用边界表，防止把黑盒 oracle 分离误判为明文算法类分离。
- **预期信息增益**：以具体可执行程序界定“换输入访问协议”与“同明文协议受限计算分离”的精确分水岭。

### 节点 3：`E-argon-LOC-SAT-2` — 小见证局部约束问题（Small-Witness $k$-Clique / 局部 2-CSP）在亚线性工作空间下的同预算 D vs ND
- **层级与依赖**：Layer 3 $\to$ `M22`, `M24`
- **建议参数**：`current=0.88, remaining=0.90, novelty=0.95, confidence=0.85, cost=0.95`
- **证据与问题切入点**：
  - `E-chief-PPST-1` 导出了 FLMV 的漂亮下界 $\text{SAT} \notin \text{DTISP}[n^{1.4}, n^{0.01}]$，但同时指出致命障碍：**标准 SAT 的完整赋值见证长度为 $\Theta(n)$ 位**，根据 `E-chief-cert-1`（只读证书不能免费当小工作空间），非确定性机器若要在 $n^{0.01}$ 空间内无免费证书地验证 SAT，根本存不下 $\Theta(n)$ 位的猜测赋值！
  - **破局思路**：为什么 `COLLISION` 能放进 $16w$ 寄存器？因为它的见证只有 $k=2$ 个下标（$2w$ bits）！同理，若要向组合约束/逻辑可满足性推进且保持**见证本身可完整装入 $16w$ 寄存器（即 $O(\log n)$ 空间，零免费证书带）**，应当考察**常数/对数サイズ小见证问题（如邻接矩阵/边表上的 $k$-Clique、$k$-SUM 或稀疏局部可满足性，$k \le 6$）**。
- **验收标准**：
  1. 在 `bounded_vm_nd_v1.py` 中构造 $k=3$ 或 $k=4$ 的小见证约束问题（如 `3-SUM` 或隐式图 `TRIANGLE`）：证明 `ND` 仅用 $k \cdot w$ 位寄存器存储猜测顶点/下标、$O(w)$ 步即可在 $M=0$ 数组下完成完整计费验证；
  2. 审计该问题在 $F = O(n)$（或 $O(n^{1+\epsilon})$）、$M = O(\sqrt{n})$ 确定性 BRAM 下的分支程序下界及与参数化复杂性（FPT / $W[1]$）的关系。
- **预期信息增益**：解决 `E-chief-PPST-1` 与 `E-chief-cert-1` 交汇处的最大死结——即如何在**不借助免费长证书带、仅用 $O(\log n)$ 真实非确定性工作空间**的前提下，构造超越二元相等（`COLLISION`）的高阶组合约束同预算分离。

---

## 五、 本轮验证记录、产物路径与未知项保留

1. **本机可复现实验验证（`argon_probe_h2_v1.py`）**：
   - 运行命令：`/run/current-system/sw/bin/python3 /home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-argon/argon_probe_h2_v1.py`
   - 结果：4 项精确测试全部通过（`argon-probe-h2-v1.json`：`{"ok": true, "tests_run": 4, "failures": 0, "errors": 0}`），涵盖：
     - `test_h1_correction_binary_feedback_m_bits_vs_m_states`（核验 $m=10, K=4, s=0$ 时恢复上界为 $1/64$ 而非 $1$）；
     - `test_conditional_vs_correlated_retry`（核验 $p=1/4, K=4$ 时条件 hazard 界 $175/256$ vs 完全相关边际 $1/4$）；
     - `test_opaque_comparator_vs_raw_bits_gap`（核验 $n=16$ 时比较树下界 45 vs 明文直接寻址 16 步）；
     - `test_flmv_exponent_and_nd_space_gap`（精确有理数核验 FLMV 递推 $c=3/2, k=2 \Rightarrow d=1/36$）。
2. **独占 `cwd` 产物文件清单（未覆盖任何 H1 文件）**：
   - `ARGON-H2-RETURN-v1.md`（本 H2 权威交回报告）
   - `proposed-nodes-h2-v1.json`（H2 新增 3 个候选节点规范：`E-argon-RAND-ED-2`, `E-argon-OPAQUE-CRIT-2`, `E-argon-LOC-SAT-2`）
   - `argon_probe_h2_v1.py` & `argon-probe-h2-v1.json`（H2 验证脚本与结果）
   - 历史保留：`ARGON-H1-RETURN.md`, `round1-audit-v1.md`, `proposed-nodes-round1.json`, `proposed-nodes-round1-v2.json`, `argon_probe_v1.py`, `argon-probe-v1.json`
3. **未决义务与边界声明**：
   - 标准数学主目标 `T1`/`T2`（ZFC 下明确一侧标准 $P=NP$ 或 $P \ne NP$ 不可证）与 `T3_v2` 仍为 **UNRESOLVED**；
   - 全扫描 `COLLISION` 在常数 $1/3$ 错误率随机化 BRAM 下的下界、以及现实任务总体分布 $\nu$ 与强参考系统的实测覆盖下界仍属未决义务。
