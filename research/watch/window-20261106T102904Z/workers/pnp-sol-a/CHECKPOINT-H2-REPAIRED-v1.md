# pnp-sol-a — H2 REPAIRED checkpoint v1

时间：2026-11-06 21:46 Asia/Shanghai。固定绝对截止仍为2026-11-07 01:29:04；未续期。本文件是本次新交回入口，不覆盖以前v1数学证据或旧runtime交回。

**全局状态：初始算法空间/同模型分离/现实覆盖仍UNRESOLVED；标准T1/T2也UNRESOLVED。没有宣称新验收通过。**

## 1. 协议修复实际执行

严格按本次指令的顺序：

1. 第一工具操作为mail_identity.configure_watch：mode=paused、delivery=followUp、pollIntervalSec=60。
2. 随后仅在自己的`.pi/settings.json`将`agentMail.enabled`改为true；没有更改模型/工具字段的值，没有读取或打印凭据配置。
3. claim自己的pnp-sol-a身份。工具确认绑定且策略为paused/followUp/60s；之后status再次确认在线、paused、空收件箱。
4. 手动读mail及主题群`pnp-7h-20261106`，无自动prompt回合；仍保留mail调用及heartbeat租约。
5. 核实际时间，执行board refresh/next。next起初无未占用叶；据Argon H2候选自行add/claim RAND-ED-2，完成后再次next，再自行add/claim LOC-SAT-2。没有等待逐项审批，没有启动子代理。

先roster核chief职责后，发送实际启动notice与两个证据增量notice。没有触碰chief持有的OPAQUE模型/输入原语工作，没有重复GVC/IDX/FNS-v1。

手动处理旧邮件`20261106T122754Z-pnp-sol-c-a57-preflight-385421`：C58独立核A57抽象候选未发现免费proof或地址回绕；它同时限定Python输入预检不在fuel内、init与bit_charge相加、PC/fuel控制位另计。已归档acked，无客套回复回环；不把这封邮件说成现实或物理sublinear验收。

## 2. 本次两项数学/模型增量

共享证据根：
`/home/desk/projects/pnp-unprovability/alternatives/practical-core/`

### A. E-argon-RAND-ED-2：原始随机化误差条件与收费放大

终态：**exhausted / conditional**，remaining=0。

不可变证据：
`evidence/E-argon-RAND-ED-2/961ba192e15d159cf20adaa11c50ccf8343a53709768377863ba65dd4046095a.md`

本地完整推导：`RAND-ED-H2-source-audit-v2.md`。

实际核查作者稿BSSV（2002-10-24，JACM2003）§2.3随机BP模型、Prop2.1、§6.2及6.23/6.24证明相关段；独立渲染并目视原p35，避免OCR负号/根号错位。原作者URL：
`https://www.cs.washington.edu/homes/beame/papers/randomts.ps`

只读sol-c已取得的完整PS/PDF，不改他人文件。PS hash `38f9bf0da43a21b4073278a24a4e9fade560562544a597818629383c1dc1295a`；PDF hash `15081a6737b2c141bdad2a83a8e51835af19884397509d36b10ed3d0cb764a51`。

#### 精确修正

原Thm6.23要求每输入错误率

`ε ≤ (T/n)^(-γ(T/n)^2)`，某固定γ>0；所得下界

`T = Ω(n sqrt(log(n/S)/loglog(n/S)))`。

另在`ε≤S/n`条件下，原图第二下界为

`T = Ω(n sqrt(log(n/S) * loglog(n/S)))`。

原Cor6.24针对固定δ的`ε≤n^(-δ)`和对应时间/空间条件，不能令δ事后随n变化来偷换成1/3错误。

**H2建议的误差统一概括为2^-Ω(log²n)不正确。** 对当前F=32n+512，T/n是常数级，第一个门槛是取决于时间系数的小常数级；并非强制随n缩小。若换成T=Θ(n logn)，门槛的负对数则约log²n·loglogn。须用实际时间比率代入。

#### 放大与适用类

- 顺序独立重复r次可以重用scratch，只增加计票/控制空间，但总时间升为约rT。必须把门槛中的T/n也换成约rT/n。标准exp(-Ω(r))多数放大不能自动达到exp(-γ(rT/n)^2 log(rT/n))，不许仍用原时间系数。
- 将常数错误用通常多数压到n^-δ的充分重复数Θ(logn)会把线性时间变成Θ(n logn)，超出该Cor6.24的n sqrt(logn/loglogn)排除范围；该推理没有形成矛盾。没有因此证明所有特殊放大法都不可能。
- **新增局部正结论**：若随机程序每输入零错误，且所有轨迹受同Γ最坏时间/空间限制，固定n的输入集有限，有限个零测错误种子集合的并仍零测，故存在同时对全输入正确的固定随机带；展开为强非统一BP即可用已核确定性下界排除。不把随机带免费作为可读工作ROM。
- 只有期望clock的Las Vegas或单边有错不满足该零错最坏clock前提。一般1/3-error随机Γ仍缺匹配定理或算法。

#### 一个具体hash/采样方案的收费反例

每轮均匀保存m个key再全扫描，对恰一对重复的位置，成功概率精确为

`1-C(n-2,m)/C(n,m) = m(2n-m-1)/(n(n-1)) ≤ 2m/n`。

K轮成功≤2Km/n；达到2/3需K≥n/(3m)，每轮n次读，故该具体方案需Ω(n²/m)。m≤sqrt n时为Ω(n^1.5)，不满足当前线性fuel。这**不是全部随机RAM下界**。

本次未证明1/3-error问题在整个文献中开放，仅证明当前引用和这些直接修复模板尚未交账。

### B. E-argon-LOC-SAT-2：小见证上界与SAT归约预算失配

终态：**exhausted / counterexample**，remaining=0。

不可变证据：
`evidence/E-argon-LOC-SAT-2/c51c514475b31aa33816c92ea06eeada231f91f9492ed729bc52dd705f4911f7.md`

本地推导：`LOC-SAT-H2-witness-transfer-audit-v2.md`。

#### 收费ND候选

v顶点显式邻接矩阵，N=Θ(v²)个输入word。逐bit猜k个顶点编号并存入普通数组，再核所有k²对的互异/邻接，给ND上界`O(kw+k²)`word步骤、`k·w+O(w+logk)`bit保留状态。完整输入获取、初始化、精度和乘法位收费另列。

尚未编该一般k-clique的完整ISA，**不把O上界冒称恰满足32N+512数值Γ**。

k=Θ(logv)时见证Θ(log²v)bit，并非可统统放进16w=Θ(logv)寄存器；允许M数组时可以收费保留。这与小见证是否足以继承SAT下界是两件事。

#### 归约的明确失败点

标准m-clause 3CNF occurrence graph：

- 顶点v=3m；不同clause的文字且不互反才有边。
- 需要clique大小**k=m**，不是固定k。
- 显式矩阵格数**N=9m²**；构造/写出矩阵须付平方量输出费用。
- 选每clause一个文字可压成2m bit，但仍不是O(logℓ)小证书。

平方新输入使M=sqrtN=3m个工作word，确能装m-word见证；同一平方扩张也让回投SAT的时间约m²、工作状态约m logm bit，远超原SAT ℓ^1.4/ℓ^.01 profile。因此“改成clique后证书能装下”没有自动修复原FLMV预算传递。

若改成虚拟矩阵按需回答邻接，必须逐次换算原文字定位、输入尺度和调用费用，不能同时拿显式/虚拟表示各自的好处。

另证：b位证书可存储枚举，时间O(2^b(t+b+reset))、空间O(s+b+control)。普通有效机器上b=O(logn)、验证多项式便得到P；因此一般SAT若有此类小见证会推出P=NP。固定k-CLIQUE归约也有同类条件障碍，不能未经证明当现成SAT空间修复。这不证明这种归约绝不存在，也不预设P≠NP。

## 3. 实际有限验证与消费入口

全部文件在自己cwd，仅Python标准库，没有安装软件或改公共入口：

| 实验 | 实际通过 | 文件 |
|---|---:|---|
| 多数错误/门槛形状 | 43项 | rand_ed_error_probe_v2.py / rand-ed-error-probe-v2.json |
| sample-key精确概率枚举 | 154项 | 同上 |
| 显式3SAT→clique语义/格数 | 11612个公式 | loc_sat_clique_probe_v2.py / loc-sat-clique-probe-v2.json |

另在`/tmp`、`env -i`、普通系统Python绝对路径重跑两个脚本，输出与原运行JSON逐对象一致；对应`*-clean-v2.json`。这些是公式/归约规范检查，**不是现实任务得分、随机ED算法或全类下界的实证验证**。

最短复现：

```sh
cd /home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-sol-a
/run/current-system/sw/bin/python3 rand_ed_error_probe_v2.py
/run/current-system/sw/bin/python3 loc_sat_clique_probe_v2.py
```

不可变共享报告内嵌源码与原测试输出；此前已发布v1文件未修改。研究脚本不是部署应用，不宣称GUI/生产服务已验。

## 4. 共享板实际更改与mail状态

稳定op：

- sola-h2-repaired-resume-1
- sola-h2-add-randed-v2 / sola-h2-claim-randed-v2 / sola-h2-publish-randed-v2
- sola-h2-add-locsat-v2 / sola-h2-claim-locsat-v2 / sola-h2-publish-locsat-v2

全部共享graph/state/evidence仅经事务board CLI，新增边RAND-ED→M22/M23与LOC-SAT→M22/M24。两节点terminal余值均0，自己的lease已释放。最后board check：**37节点、50边、round57通过**；最后next无未占用eligible叶，chief的OPAQUE仍持有，未覆盖其产物。

已发chief实际启动与两个结果notice，不请求逐节点批准。mail手动读取后为空；暂停策略保持paused/followUp/60，未release身份、未停mail权限。

## 5. 下一缺失输入/可恢复条件

1. 对**相同fullscan BRAM Γ**、常数1/3错误的匹配BP/RAM定理，或真正计费且满足Γ的具体算法；当前原source小错误条件不是它。
2. 对新小见证局部函数的**同函数D全类下界**，或保持所需time/space指数与输入尺度的明确归约；不能只把SAT标签改成clique。
3. 初始自然算法空间、强reference/组合能力、现实总体mass、同预算分离仍须联合审查。数据缺口只挡对应正认证，不被扩大成所有模型研究无动作。

本次已实际攻克两处H2可执行审计问题；不会为等下一小时空转/睡眠，也不会把重复v1或未证BPP/小见证猜想登记成新成功。固定截止前5分钟只checkpoint；本文件不延长窗口。
