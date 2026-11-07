# pnp-sol-b — H2 checkpoint v1

时间：2026-11-06 21:33 +08:00。固定截止 **2026-11-07 01:29:04 +08:00**，未续期。本报告是提前checkpoint，不冒称会话一直运行到截止。

## 1. 本轮结果

读过Argon H1处置和新证据后，当前next没有未占用叶；没有重写C的FNS/GVC/IDX，也没有重复PPST摘要或“缺μ”结论。本人自主新增并完成两个修复型后继：

| 节点 | 状态 | 实际增量 |
|---|---|---|
| **B56** | done / proved-candidate / remaining=0 | 静态一bit OR索引不能免费保全未来SET更新；给有界更新次数U的紧初始状态类数、普通raw+counter实现和生命周期账本 |
| **B57** | done / proved-candidate / remaining=0 | 支付随机常数错误缺口：动态OR逐坐标解码导致`b≥N(1−h₂(ε))`，无需一次恢复全串 |

两者为局部候选证明，仍需独立复核；**不是新D/ND分离，不是实测human，不是现实大部分覆盖**。标准T1/T2和T3-v2均保持 **UNRESOLVED**。

## 2. B56：未来更新能力的初始状态价格

### 消费入口

`/home/desk/projects/pnp-unprovability/alternatives/practical-core/evidence/B56/6bf6f2e95c5c20b0467da038e2d6f6d008657d82de6235c92406b8197862bb16.md`

该不可变证据内嵌完整研究源码、测试输出和账本JSON，不依赖临时脚本路径才能审查。

### 精确模型与候选定理

Build读取任意N-bit数组x，之后**不再保留raw数据或别的输入相关外部状态**。Update输入仅为`(i,newbit)`，不额外给可信oldbit；Query输出当前OR。程序确定且精确，允许最多U次SET，`0≤U<N`。

完整初始可访问状态至少有

`M(N,U) = 1 + Σ_{k=0}^U binom(N,k)`

种，即至少`ceil(log₂ M(N,U))` bit。这计的是全部未来可读的寄存器、PC、索引、外存、日志/输出、时钟/游标等输入相关状态，不只是局部RAM数组。

**自含下界：** 任意两个大小≤U的不同1-support集合S、T，可把其中一个集合全部置0，至多U次共同更新后OR不同；任何小集合与大小>U的集合也由清空小集合区分。因此每个小集合必须有不同状态，另须至少一个大集合状态。

**紧初始类数上界：** 所有`|S|>U`的输入在未来U次更新内不可能清空，可合并成ALWAYS_ONE。小support保留其精确集合；更新后若support大小超过剩余更新次数，也可转ALWAYS_ONE。这里紧的是初始信息容量，不声称转移不需额外scratch或可零成本编码。

例N=8：

| U | 状态数 | 至少bit |
|---:|---:|---:|
| 0 | 2 | 1 |
| 1 | 10 | 4 |
| 2 | 38 | 6 |
| 4 | 164 | 8 |
| 7 | 256 | 8 |

这不同于旧静态INDEX：查询始终只是OR一bit，新增负担来自**未来编辑的组合能力**，而非多输出或禁止重读。

### 两个实际反例

- `(1,0)`和`(1,1)`的静态OR都为1；相同`SET(0,0)`后一个OR为0、一个为1，所以只存OR不够。
- `(1,0)`和`(0,1)`的count都为1；相同`SET(0,0)`后的正确count不同，所以“只存count”也不够，除非另有raw或可信oldbit信道。

### 最小可执行能力底线

`dynamic_or_h2.py`给出普通确定实现：保留packed raw bits和binary ripple counter，SET先回读旧bit再更新count，Query不必重扫raw。

关键边界：
- counter宽度是`ceil(log₂(N+1))`，N为2的幂时不能只用log₂N位，否则全1计数溢出；
- Build、raw零初始化、copy、counter初始化和读写全部有cell账本；
- expected_version仅拒绝过期调用，**不承诺并发线性化、磁盘原子提交或崩溃恢复**；单调用同步语义明示；
- packed payload字节数不是Python RSS/全部peak live，version、ledger、源输入副本及host对象开销未测且不是0；
- 完整生命周期分母是Build+实际updates+实际queries+失败/拒绝成本，不用无限未来query摊薄cold请求。

N=64交替1/0，删除32个1后Query=false：input_reads=64、raw_reads=32、raw_writes=160、counter_reads=133、counter_writes=133。packed raw+counter payload=9 bytes，但不冒称全物理内存只有9 bytes。

## 3. B57：随机误差不能让动态能力免费压缩

### 消费入口

`/home/desk/projects/pnp-unprovability/alternatives/practical-core/evidence/B57/7f7f8a398a21f333f91234a172336a8f62ca4f79eca613fbab618b36d2d7185e.md`

### 前提和结论

Build后只有最多`2^b`种完整输入相关状态M，没有raw或额外信息信道。允许独立随机性，甚至可把与X独立的公共随机带R免费公开；任何输入相关游标/选择仍须算入M。

要求对**每个固定输入和合法更新历史**，Build→至多N−1次SET→OR查询的端到端错误率≤`ε<1/2`。这不能由query的benchmark平均分或每一步单独边际成功率免费推出。

则：

`b ≥ N(1 − h₂(ε))`。

ε=1/3时系数约.081704；ε=.1时约.531004；零错误得到b≥N。

### 自含证明要点

要解码原始X_j，只需把除j之外的全部位置SET为0，再Query OR。因此动态接口提供任一坐标的可靠decoder，而不是一次运行恢复整串。

令X均匀独立，MAP单bit错误率`p_j≤ε`，得

`H(X_j | M,R) ≤ h₂(p_j) ≤ h₂(ε)`。

由条件熵次可加性：

`H(X | M,R) ≤ N h₂(ε)`。

X独立R给`I(X;M|R)≥N(1−h₂(ε))`，但状态数又给`I(X;M|R)≤H(M|R)≤b`。无需对N次错误取union bound，不假设一次同时恢复全串。

### 不能隐藏的接口变化

- 若保留raw，已有Nbit输入相关状态，不能只算辅助index。
- 若每次更新额外提供可信oldbit，update流本身注入原输入信息；只存count可以合法更新，但已经违反“decoder只从M获得输入信息”的前提。
- 若只保证dense现实分布的平均分，常数OR=1可能高分，不能用这里逐输入/历史定理直接宣布它失败。
- 若只允许U≪N−1次更新，本随机引理不直接给同一线性界；B56处理确定精确有界U，容错有界U的最优容量仍是具体开放义务。

## 4. 实际验收与复现

本轮 **11项测试全部通过**，均仅Python标准库，并在清洁普通shell、cwd=/以绝对路径复现：

- `dynamic_or_h2.py`：7项。枚举N=1..7各U的全部输入/reset signatures；穷举N=4全部允许SET历史；全部小数组单步更新；计数宽度；两种摘要反例；stale拒绝；cold资源账本。
- `random_dynamic_capacity_h2.py`：4项。h₂常数；N=3全部256种one-bit encoder的MAP/条件熵关系；零错误；独立公共随机坐标编码的sanity。

原始日志：
- `dynamic-or-h2-tests-v1.txt`
- `dynamic-or-h2-clean-shell-v1.txt`
- `dynamic-or-h2-result-v1.json`
- `random-dynamic-h2-tests-v1.txt`
- `random-dynamic-h2-clean-shell-v1.txt`

有限测试不承担全算法量词；通用结论由两份证据的自含证明承担。未安装新软件/CLI/服务，未修改PATH、桌面、凭据或网络配置。

## 5. 共享板、来源和所有权

实际读取的新输入：
- chief：`workers/pnp-chief/ARGON-H1-DISPOSITION-v1.md`；
- C的GVC证据：`evidence/E-argon-GVC-audit1/fde5f576003fb266440345a9499fbca9d427cd5ac92ce1670dc9f4052e33d6b8.md`；
- C的IDX证据：`evidence/E-argon-IDX-audit1/980b57f1419390198f3a38937d9db7982716eb26795ba5e95e625808e65e6d5f.md`；
- C的FNS证据：`evidence/E-argon-FNS-audit1/2f0d4473e479c7171950d600548950d618016819ddf4251cb44cb169a06cc64b.md`。仅阅读该证据，没有冒称本轮重新独立核验它所用全部原始BP下界。

本轮结论是局部自含推导，不主张文献原创性，无新增外部来源依赖。

节点边：B56/B57各自指向M22、M23；全部共享写入只经事务CLI。以B56/B57新证据CAS调整M23 revision0→1：

`current=.94, remaining=.85, novelty=.95, confidence=.9, cost=1.2, status=open`。

余值聚焦真实reference完整runtime/生命周期及更广能力，不是覆盖成功概率。没有给已有终止叶无新证据加轮次。

最近`board check`：**ok，35节点、46边、round53**。最近next无未占用叶，仅chief OPAQUE仍由其owner持有；这是当时快照。本人B56/B57发布后均无活动租约。关键选点和结果已发chief notice，不跨owner写文件。

## 6. 剩余的真正研究义务

1. 把动态更新能力纳入候选profile前，冻结更新种类/次数、raw是否保留、oldbit来源、版本/并发/故障协议；静态索引证书不能无证明转移。
2. 将cell账本编译到完整固定bit/word/硬件模型，计地址准备、序列化、日志、版本增长、源输入驻留及peak live。当前9-byte payload不替代此项。
3. 研究有界U、允许ε错误时的容量—时间—状态前沿；不能把B57的N−1更新结果套到短窗口。
4. 若要D/ND同预算分离，双方必须同样拥有raw、Build、更新和索引权限；本轮容量引理不是新的分离证书。
5. strong reference广度、任务阈值和实际覆盖仍单列；没有借数据缺失停掉所有定义研究，也没有借局部可执行底线声称现实大部分已测。

## 7. 冻结摘要及不变项

| 文件 | SHA256 |
|---|---|
| B56-DYNAMIC-OR-H2-v1.md | 6bf6f2e95c5c20b0467da038e2d6f6d008657d82de6235c92406b8197862bb16 |
| B57-RANDOM-DYNAMIC-H2-v1.md | 7f7f8a398a21f333f91234a172336a8f62ca4f79eca613fbab618b36d2d7185e |
| dynamic_or_h2.py | 9e4c91f67e310424de252c5fd38b0f664a5c0469cae8be99ce304e8901cc2b75 |
| random_dynamic_capacity_h2.py | 1da1cb1692a5f85f4490d1bd472ad27fe893e6b8fff710dbe184e963c628b9c8 |
| dynamic-or-h2-result-v1.json | fbaa61ebf1c1fd48e513a492c86186481462b4768b9dc0a1c3cfcfb6ab1fc078 |

只写本人cwd及本H2输出。旧v1交回文件、E48/B54、PPST/B55及已发表证据未修改，原104静态文件和旧证明未修改。未启动任何额外代理或Pi；没有自称新覆盖/分离已验收。
