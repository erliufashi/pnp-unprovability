# 本轮共享自主研究合同 v1

## 用户最新授权（不是旧200B停止条件）

- 恢复7小时：固定2026-11-06 18:29:04 → 2026-11-07 01:29:04 Asia/Shanghai，deadline epoch 1793986144.3940156；所有进程共用，启动晚不顺延。
- 参数量200B定义不准：重点是收缩算法空间，同时保全足够广泛的现实问题解决能力。不能挑弱baseline或只在小toy上说现实覆盖。
- 三位gateway_responses/gpt-6.1-sol max研究员与chief同样可自行挑节点、创建节点、调整参数；没有固定专职分工或逐项chief审批。chief自己攻克节点且最高指挥/冲突裁决。
- iksvip/gemini-4-argon high发散研究员每小时检查进展、提出新节点。它提出建议，不是三位Sol的审批者。

## 不变的数学边界

标准T1/T2仍是相对ZFC明确一侧标准P/NP不可证性，未解。旧T3只证限定封闭代理，不等当前现实覆盖新目标通过。原104静态文件只读（manifest在alternatives/sublinear-stream/reports/window-static-manifest-v1.sha256）；不改旧35节点或已认证证明。

当前新定义应区分：算法类的结构/计费资源；统一策略/portfolio能力保全；现实任务分布/分层成功指标与覆盖证据；数学分离。不能把待验假设当已达成。重读资料、存储、计算工具是现实常用能力，不能为了旧INDEX证明就随意禁用，也不能让工具成为免费oracle。

## 共享板与自主权限

共享根：/home/desk/projects/pnp-unprovability/alternatives/practical-core
CLI：/run/current-system/sw/bin/python3 /home/desk/projects/pnp-unprovability/alternatives/practical-core/tools/board_v1.py

所有shared-board/graph/state/evidence写入只走这个CLI（它在毫秒级事务内加锁）。三位Sol和chief权限相同，允许直接add/update/publish；不需先给chief发审批。Argon读板、在自己的cwd写建议并mail。

- `next --actor <id>`：按既有C/R/F/邻接公式及T1/T2=1、T3=.25权重推荐未被他人占用叶。
- `show --actor <id> --node E47`：看职责、验收、revision、租约。
- `claim --actor <id> --node <自行选的节点> --op <本次唯一稳定ID> --note <依据>`：只保护该节点产出，默认90min，可同actor续租。不影响跨节点有证据的参数调整权。
- `add --actor <id> --spec <自己的JSON文件> --op <稳定ID> --note <新信息价值>`：spec为nodes/edges。节点含id/layer/title/role/acceptance/artifact/seed；ID用自己前缀避免冲突，edges只3→2→1，不能孤立。可一批创建工具与叶/方向，结构校验即生效，不等chief。
- `update --actor <id> --node <id> --expect-revision <刚读revision> --current ... --remaining ... --novelty ... --confidence ... --cost ... --status ... --op ... --note ...`：任何研究员均可调参，CAS避免旧读覆盖新改。worked/gain只为真研究操作，非管理重复。
- `publish --actor <id> --node <自己的租约节点> --file <自己cwd里的产物> --status done|exhausted --classification hypothesis|conditional|proved-candidate|counterexample|blocked --worked --gain --op ... --note ...`：拷贝成不可变hash证据，terminal余值自动0，立即重选。候选证明不等独立验收通过，不能自行关闭全局目标。
- `release ...`：释放自己的产出租约；chief可作带记录的冲突裁决。
- `check`：核三层结构/证据及输出投影。shared-board.json是权威；不要用旧pnp CLI mutation绕过它。projection仅兼容读取。

每个真实动作一个稳定op ID；相同op重复会无副作用返回，换payload复用op会拒绝。不要持锁研究。源文件/实验在自己的隔离cwd写；只经publish入共享证据，不覆盖别人文件。参数有争议在mail里举证，不互相无理由反复改。

## 协作/mail

先读agent-mail技能并自行注册自己身份；project:pnp-research、window:20261106t102904z、role:researcher或divergent，身份ID见派单。所有人先mail_roster发现chief/边界，再联系。chief=pnp-chief；主题群pnp-7h-20261106按标签自动纳入。

启动后先向chief发一条notice，说明自己实际身份、选中节点/工作目录；完成关键节点发有证据的增量。需要动作的request只点名一个owner；群内普通事实静默，别用无内容@互回。可用contact_supervisor处理真实阻塞，但不要再启动任何代理/额外Pi。

## 研究与停止

同权研究员先看next，自行claim。不要复制另一人的同一研究任务；claim冲突就选别的或沟通。可创造节点并调优，旧模板若无余值必须0并换，不拿重复总结算新鲜。取得节点结果后继续自主选下一项，直到截止前checkpoint或具体客观阻塞；不空转/睡眠伪造工作。

每小时chief会检查全板和mail，恢复或请求Argon做本轮审查；已完成Argon会恢复同一角色session，不谎称同一OS进程一直在线。Argon初次现在完成一次有界审查即可交回，不为了等下一小时空跑。

截止前5分钟保存产物/状态、释放或交接claim，不开长实验。到01:29:04停止新研究，未完成也照实交接；chief只停止本窗口任务，不续期。当前Pi会话监测已开，关闭主会话不保证继续在场。

## 参考入口

- 旧整体报告：/home/desk/projects/pnp-unprovability/alternatives/sublinear-stream/reports/window-final-v1.md
- 原目标义务：/home/desk/projects/pnp-unprovability/proof/obligations.json
- 上轮能力分层/风险：alternatives/sublinear-stream/proof/ADEQUACY-TIERS-v1.md 与 APPROX-TRANSFER-v1.md
- 上轮非空洞性：alternatives/sublinear-stream/proof/NONVACUITY-v1.md

旧仓库AGENTS里的10h/200B段落属于旧合同，当前用户新授权和本轮ACTIVE优先；不把这理解为可以改写旧史料。
