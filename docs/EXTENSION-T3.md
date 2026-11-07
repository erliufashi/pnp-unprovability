# T3扩展操作与交付（hub 0.2.0）

## 用户授权与不变边界

本次新增用户entry bd6c15b6授权的第三备用条件。原T1/T2标准不撤销；原research/graph.json、state.json、history.jsonl、全部旧节点参数与派生评分不变，旧notes/sources/proof及原内核源码/25项测试也列入SHA256保护。报告reports/extension-preservation.json保存扩展前基线与结束读回。

新增分支在alternatives/closed-llm，10节点三层DAG、独立局部时钟。T1/T2奖励权重1，新T3权重0.25；跨分支只合并候选排序，不传播邻接参数、不共用年龄轮次。原图谱服务两个标准目标，但不因此把收益重复加倍。

## 一个稳定入口

```
pnp-research --help
pnp-research --version
pnp-research status                       # 原图谱，行为兼容
pnp-research alt status                   # 新分支
pnp-research alt check --json
pnp-research mission priorities --json    # raw_priority × weight
pnp-research mission status --json        # 三项停止状态与适用范围
pnp-research mission check --json         # 旧节点保护
pnp-research mission refresh --reason context-resume --json
```

alt拒绝--root及其缩写，避免误写旧状态。需要隔离验收时使用临时XDG_CONFIG_HOME配置，不改真实配置。旧入口的--root行为仍兼容；用户应明确知道这是对旧控制器的直接操作，不是新分支默认行为。

只有新分支任务活跃时，摘要恢复用mission refresh；它只改alternatives/closed-llm/research/{state,history}及新增research/mission-state.json，不触碰旧三文件。若将来主动恢复原数学研究，原refresh协议仍可使用，但那是旧任务的独立工作，不属于本次T3副作用。

## 停止与证书

research/termination.json存T1/T2/T3。新goal提交前T3必须pending_review，mission status.stop=false。独立goal pnp-t3的正式pass回执产生后，父任务核对goal_id、verdict、checks及SHA256，再只更新T3证书和proved_conditional_proxy状态。hub每次读取会验证回执SHA256、goal_id和verdict；不能拿系统测试或数学子任务回执替代完整T3回执。

仅T3达成时：stop_scope=qualified_closed_LLM_proxy，standard_targets_unresolved=true，human_equivalence_empirically_verified=false。适用条件始终随状态输出。原数学目标和旧前沿不被改标/关闭；行政父goal可能因保留旧子节点而继续active，不因此伪造完成。

原内核的mathematical_target字段保留原标准目标语义；T3正式状态以mission status为准，不能把alt中旧内核默认字段当T3证书。

## 状态快照与恢复

```
pnp-research alt snapshot --json
pnp-research alt restore <返回的文件名> --reason recovery --json
pnp-research alt check --json
```

恢复节点参数、证据引用，保留审计历史并增加恢复事件。只针对新分支，不改旧图谱。隔离验收实际执行snapshot→exhausted参数修改→restore，要求nodes恢复相等、events不被截断、旧SHA256与派生scores不变。正式旧状态基线副本在reports/extension-baseline/，本次不对它执行恢复覆盖。

## 冻结发布、回退、依赖

稳定入口~/.local/bin/pnp-research指向current版本。0.2.0包含新增hub.py和与0.1.0逐字节一致的research.py；发布SHA见releases/0.2.0/release.json。依赖系统Python>=3.10、Linux fcntl、标准库；无网络/凭据/GUI/服务，不改PATH或shell配置。

current原子切换至releases/0.1.0时launcher自动回退原内核；切回0.2.0恢复mission/alt。旧版本不认识新命令是版本能力边界，但旧check/status等始终可用。回退只换代码，不回退/删除数据。不可让两个writer并发激活版本。

实际0.2→0.1→0.2回退、每次版本读回及旧check验收见reports/extension-acceptance.json。测试失败也会finally切回0.2.0。卸载扩展可切回0.1.0，保留新分支证据和配置以便恢复；没有授权删除任何旧节点或数据。

## 验收入口与准确范围

```
cd /home/desk/projects/pnp-unprovability
python3 -m unittest discover -s tests -v
python3 tests/extension_acceptance.py
```

后者是独立审查前的pending状态验收；证书激活后不要不加说明地把它的pending断言当当前状态。正式回执后的证书验证另记reports/t3-certificate-check.json。旧reports/acceptance.json保留，未覆盖或把旧时序伪装成新验收。

软件测试包括原25项与新增隔离/选项保护/INDEX有限sanity checks。有限测试不是渐近证明；真实200B部署、人类接近度与墙钟性能未测。数学论证在alternatives/closed-llm/proof，独立回执见reviews/INDEX.md。

### 独立执行权限的区分

完整T3第1次只读审查因不能亲自执行带副作用的测试而未通过，该失败保留。使用单独明确允许测试副作用的pnp-t3-test-gate完成独立重跑；tests/run_gate.py在R运行两条指定命令，reports/independent-tests.json及带时间戳归档包含原始退出码与完整日志路径。这个角色只允许运行测试，不允许改证明、源代码、旧节点或证书；不绕过原只读校验器的权限闸，也不把历史报告伪称为本次独立执行。

### 当前已激活状态

完整pnp-t3第2次已pass，证书已激活；mission显示stop=true、met=[T3]、stop_scope=qualified_closed_LLM_proxy，同时standard_targets_unresolved=true且人类经验等价未验。回执持久副本在reviews/pnp-t3-submit-2.receipt.json，当前使用不依赖原Pi会话仍可读取；SHA和官方源路径保留在证书检查报告。原目标节点仍原状。
