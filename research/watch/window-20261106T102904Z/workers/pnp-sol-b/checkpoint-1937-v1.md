# pnp-sol-b checkpoint — 2026-11-06 19:37 +08:00

## 结论与边界

完成两个独占节点的有界理论研究，并经事务CLI发布不可变证据：**E48、B54均为conditional/done，remaining=0，无活动租约**。这里done只表示该叶的有限研究已交付，不表示现实覆盖、新分离或标准P/NP不可证性验收。标准目标仍为 **UNRESOLVED**。

当前没有现实任务总体、权重/未知质量和真实执行轨迹，因此**可认证的现实覆盖下界只有0这个无信息下界；不是测得能力为0**。没有沿用“200B已经充分”的假设。没有修改旧104文件、旧35节点、旧证明；没有启动额外代理或Pi。

固定截止仍是 **2026-11-07 01:29:04 +08:00**，不续期。本次提前checkpoint而非声称已在场研究到截止。

## 1. E48：现实任务分布、未知质量与双层统计证书

共享证据：
`/home/desk/projects/pnp-unprovability/alternatives/practical-core/evidence/E48/e1889e3c910d146aae1125f43f71fd8f8bf46fe6f17be6b8d051b09297bbe628.md`

主要产出：
- 区分任务内执行成功概率、任务合格比例及现实总体任务质量；不能把episode成功率冒充问题族覆盖。
- 给出无分布输入的可辨识性负结果：有限集合内的成功不能无条件推出总体正覆盖。已知未覆盖质量上界u、已知域条件覆盖L时，保守下界为`(1-u)L`；未知u不能默认为0。
- 给出任务内Hoeffding资格认证与任务间Hoeffding覆盖认证的双层候选证明，显式分配内/外置信预算。空层下界0，超时/资源失败不能删除出分母。
- 权重只有区间时，求`min Σw_h L_h`，未知层取L=0。盒约束下按L从小到大填剩余质量，给出交换证明与实现核验。
- 若仅在已知域条件law上有TV漂移γ，未知质量≤u，则转移下界为`(1-u)max(0,L-γ)`。γ不是token误差。
- 完美任务阈值θ=1不能由有限样本Hoeffding下界认证；需要数学保证或正式修改任务标准，不能事后偷换。

示例只是算例：L=(.9,.7,0)，权重区间a=(.3,.2,0)、b=(.7,.5,.2)，最坏w=(.3,.5,.2)，下界=.62，不是现实模型实测。

本地源与实验：
- `E48-COVERAGE-v1.md`
- `coverage_bounds.py`
- `coverage-tests-v1.txt`

标准库单元测试 **7/7通过**，仅核验数学实现与负控制，不验证真实能力。

## 2. B54：自适应选策略、描述长度证书与非oracle过拟合

新节点由本人直接add/claim，边为`B54→M21`、`B54→M23`，继续保持三层结构。创建原因：E53被A领取、next无可用叶，同时E48固定策略前提留下可具体推进的自适应选择义务。

共享证据：
`/home/desk/projects/pnp-unprovability/alternatives/practical-core/evidence/B54/d8883f4d39d38acf0bb5c3bf4cac61c5d03653171d3fce0fa3e7cf46d5738957.md`

已读E47/E51，不把E47已经提到的固定K union-bound重复算作新发现。增量为：
- 对预先固定的可数候选类及先验p_j，Σp_j≤1，证明同时覆盖界：
  `C_j ≥ empirical_true_qualification_j - sqrt(log(1/(αp_j))/(2n))`。
  联合事件容许评测后选择j，避免错误使用单模型置信界。
- 前缀自由代码长度l_j可用p_j=2^-l_j，罚项为`sqrt((l_j ln2+ln(1/α))/(2n))`。候选表/代码必须与认证样本独立，数据依赖的先验不能免费使用。
- 扩展E48：对各候选/任务分配内层资格错误预算，再用先验权重分配外层预算，得到可自适应选策略的双层下界。
- 构造不用运行时答案oracle的可执行记忆反例：N个均匀任务、标签全0，观察n个评测ID后只在这些ID输出0，评测全对而总体成功≤n/N。它与E47不可见真值的oracle selector反例不同：统一程序也能通过认证数据泄漏严重过拟合。
- 外部存储的评测ID集合必须计费；十行程序配免费巨大表不构成真正收缩。
- 明确描述长度/候选数的统计收缩、部署资源收缩、现实能力、计算复杂性分离四者不能互推。大型冻结模型候选数可以为1，但物理资源仍全额计费。

本地源与实验：
- `B54-SELECTION-v1.md`
- `selection_probe.py`
- `selection-tests-v1.txt`

标准库测试 **4/4通过**：记忆负控制、描述罚项、对全部256个小型iid样本序列精确枚举统一坏事件、固定宽度表族Kraft质量。不是现实模型评测。

## 3. 协议与当前阻塞

已完整读取TEAM-CONTRACT-v1、mail技能、ACTIVE/state；注册身份pnp-sol-b并先roster发现chief及边界，向chief发送选点与关键结果notice。E53竞态claim被CLI拒绝后未覆盖A任务，改建B54。所有共享写入仅经board_v1.py，证据引用后未修改。

最近`board check`：**ok，16节点、16边、round13**。最近`next`：无可用叶，仅C55被pnp-sol-c占用；本人无活动租约。此为当时快照，其他研究员可继续更新。

进一步真实覆盖认证有具体输入阻塞：
1. D1：有现实代表性的总体/独立抽样框、分层权重区间及未知质量上界；
2. D2：冻结的强参考、统一portfolio路由和部署策略，完整工具/资源账本；
3. D3：任务资格/质量阈值、真实执行及失败轨迹、验收器；
4. D4：用户接受的覆盖阈值、关键领域下限和联合置信预算；
5. D5：分布漂移及策略/预算转移证据。

未收到这些输入时继续生成数学包装不能产生正的现实覆盖证据。本轮保留失败/边界与可执行认证流程，在此checkpoint；可由新任务/真实数据/协调消息触发后续有界工作，不声称无人时自动持续。

## 4. 复现与摘要

独占工作目录：
`/home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-sol-b`

复现小型研究测试：
```sh
cd /home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-sol-b
python3 coverage_bounds.py
python3 selection_probe.py
```
只依赖Python标准库；没有安装/修改用户CLI、PATH、桌面或服务。共享消费者以board不可变证据为入口，本地脚本仅为研究复现附件，不冒称已发布软件。

| 文件 | SHA256 |
|---|---|
| E48-COVERAGE-v1.md | e1889e3c910d146aae1125f43f71fd8f8bf46fe6f17be6b8d051b09297bbe628 |
| coverage_bounds.py | 26a379f17dd971eed46656dd6c8555ab52488788422c02d06599a7b20fe08302 |
| coverage-tests-v1.txt | 240f9f0b78102a63fd81e56ddd6d8fed5aed1c8998dbab1c1adc5de02b92929e |
| B54-SELECTION-v1.md | d8883f4d39d38acf0bb5c3bf4cac61c5d03653171d3fce0fa3e7cf46d5738957 |
| selection_probe.py | c3e03e9de113e6238cdbc4d7709c7505e37412da415f76a37bda958a41d031b9 |
| selection-tests-v1.txt | ed96f3f699d769832363b15c3714aca4814e75a1c60e510444c0f995099ff174 |

两份理论成果均为候选条件证明，仍需独立复核；没有自称新覆盖/分离已验收。
