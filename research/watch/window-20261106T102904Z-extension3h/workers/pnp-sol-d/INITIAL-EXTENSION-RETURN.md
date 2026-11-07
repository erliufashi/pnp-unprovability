# pnp-sol-d：首次自主研究交回

时间：2026-11-06 22:26 +08:00，仍在原7h窗口内。

## 已完成结果

自主新增并完成共享三层板叶 **D-GVC-BATCH-1**，连接 M21/M22。分类为 **proved-candidate（局部候选定理，未独立验收）**。

### 有界候选批验证的精确容量

设隐藏答案属于 N 个已知候选；每轮可提交至多 L 个完整候选，验证器只返回一个“答案是否在该批中”的 bit。最多 K 轮，允许最后再输出一个未经验证的猜测，无额外输入依赖信道。

定义

\[
F(K,L)=1+\sum_{j=0}^{K-1}\min(L,2^j).
\]

**结论：**任意先验下，最优精确恢复概率恰好是最大的 `min(N,F(K,L))` 个先验质量之和；均匀先验下恰为 `min(1,F(K,L)/N)`。独立随机化不能提高此最优值。

证明给出正分支至多 L 个候选、负分支递归容量的归纳上界，以及选取最大先验候选、按两子树容量划分的匹配构造。逐轮不同上限 L_i 时，精确递推为 `C_(K+1)=1; C_i=C_(i+1)+min(L_i,C_(i+1))`。

**信息增益：**先前 GVC 产物只有 singleton 等值验证 `K+1` 与任意二元查询 `2^K` 两端；本叶证明两者之间由实际批大小决定的紧致插值，而非重复原稿。例如 K=10、L=1/2/3/4/16 时，容量分别为 11/20/28/36/112，不是统一的 1024。

## 可核验证据

稳定发现入口：共享板节点 `D-GVC-BATCH-1`。

不可变发布证据：

`/home/desk/projects/pnp-unprovability/alternatives/practical-core/evidence/D-GVC-BATCH-1/9d22dc34a9a116e0f6e09d54e16884d3679a298a36453d917a579fd9ceac1bd5.md`

此文件整体包含证明、完整 Python 源码和实际 JSON 输出。

独占cwd内文件：

- `BATCH-VERIFICATION-CAPACITY-v1.md`：证明正文。
- `BATCH-VERIFICATION-EVIDENCE-v1.md`：实际发布的完整冻结证据。
- `probe_batch_capacity_v1.py`：仅标准库、完整枚举合法小型自适应决策树的核验器。
- `batch-capacity-results-v1.json`：实际结果。
- `batch-capacity-node-v1.json`：建图事务输入。
- `board-check-initial-v1.json`：结构及所有已发布证据hash检查结果。

实际核验：

1. 固定cap、N=1..8、K=0..4、三组整数先验：**510/510** 精确树优化结果与公式一致。
2. 三轮各cap属于 `{0,1,2,3}` 的全部序列，N=1..8：**512/512** 与逐轮递推一致。
3. `env -i /run/current-system/sw/bin/python3 <本cwd>/probe_batch_capacity_v1.py` 清洁环境复跑：同样通过；无网络、安装、凭据或agent API依赖。
4. `board check --actor pnp-sol-d`：`ok=true, nodes=38, edges=52, round=59`。

这些穷举支持一般归纳证明，不是现实任务实验。

## 协作和事务状态

- 已完整读取 TEAM-CONTRACT-v1、extension README、current-contract-v2、ACTIVE及原窗口state，并手动读取主题群/inbox。
- mail身份已注册为 `pnp-sol-d`，标签为 project:pnp-research / window:20261106t102904z / role:researcher。
- 私有 `.pi/settings.json` 已启用agentMail；watch为 paused/followUp/60，保留身份租约机制，无主动打断。
- 初始 `board status/next` 实际因 `unknown actor` 失败；已向配置owner pnp-chief举证，由chief加入actors/research_writers后恢复。未冒用别人的actor、未越权自行改共享配置。
- 自主事务：`sol-d-batch-add-v1`、`sol-d-batch-claim-v1`、`sol-d-batch-publish-v1`、`sol-d-batch-release-v1`。节点 done、remaining自动为0；无遗留本actor产出租约。
- 发布后 `next` 返回 null，唯一ready旧叶 E-chief-OPAQUE-1 仍由chief持有；未抢占或重复研究。
- 已向chief发送含共享hash证据的增量notice，修复通知已归档done；没有客套回环。
- 未启动子代理/额外Pi；未修改旧104文件或旧证明；未执行尚未开始的extension ack-hour，未改变任何窗口起止时间。

## 边界与未解义务

本结果只针对真正隐藏对象的指定反馈接口。已知明文输入上的计算可产生其他输入依赖信息；SAT验证器也不自动等于本模型的隐藏答案成员oracle。本定理因此**不构成标准SAT计算下界、同预算D/ND分离、现实覆盖证书，或T3-v2验收**。批提交的构造、序列化、验证时间、候选存储和服务隐状态仍须真实计费；positive batch reply不等于已识别具体正确答案。

当前合同仍缺：正式接受的强算法模型与闭包、统一参考策略/路由实现、现实人群及分层分布与权重阈值、数值资源包络、表示/迁移/执行证据及同预算分离见证。未提供这些输入时，不能把本叶容量曲线转成任何现实覆盖百分比。

**T1/T2/T3-v2：UNRESOLVED。** 后续可独立复核本叶，或在真实验证API明确候选批大小、回复内容及成本后将该紧界纳入资源契约；尚未声称这两项已完成。
