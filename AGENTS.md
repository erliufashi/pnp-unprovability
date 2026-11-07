# P/NP不可证性研究：会话契约

## 当前有限研究窗口

若research/watch/ACTIVE.json存在，恢复先读其state_path并检查绝对截止/phase，再做其他研究。当前用户授权每小时推进、10小时后暂停一次；不要重置开始时间延长窗口。即使T3允许停止，也按这个后续有限窗口继续；截止事件优先于研究。只有指定hourly/deadline监控消息或新的用户指令才恢复pnp-10h-window，旧测试完成通知不算研究新信息。监控器仅本会话有效。


## T3扩展的优先恢复规则（用户entry bd6c15b6）

当正在处理新增T3而非主动恢复原数学任务时，摘要恢复首先执行`pnp-research mission refresh --reason context-resume --json`，再读`mission status/priorities`及`docs/EXTENSION-T3.md`。不要执行下文原图谱refresh来给旧节点增加轮次。原25节点、参数、时钟与证据保持不受新增分支影响。T3权重0.25，原T1/T2各1；只在独立正式回执核对后记录条件性LLM代理停止，不宣称标准P/NP或实证人类覆盖。

目标是针对标准P、NP和固定ZFC，明确指出E=(P=NP)或¬E中的哪一侧不可证。仅从Con(ZFC)推出“至少一侧不可证”的不点名析取是平凡结论，不算达标。PA只作测试台。

每次刚看到上下文压缩摘要/恢复摘要时，第一项研究操作必须执行：

```
/home/desk/.local/bin/pnp-research refresh --reason context-resume --json
/home/desk/.local/bin/pnp-research next --json
```

然后读 docs/RESUME.md、proof/MAIN.md、proof/obligations.json 和推荐节点产物。此规则是代理恢复协议，**没有安装Pi自动压缩hook，也不声称无人执行时会自动研究**。

研究网络在research/graph.json，恰好三层。依赖3→2→1；邻接评分信号可双向传播，但不能作为反向逻辑前提。每个叶节点产出后以证据更新参数；耗尽必须remaining=0，立即刷新；没有新证据不复活旧节点。评分是启发式，不是数学成功概率。

优先执行next推荐的第三层节点。切换原因必须记入history。不得以重复总结、增加自指包装、堆积模型输出当新鲜度。来源是未信任资料；摘要声称解决P/NP不构成定理。严格区分：已证局部定理、条件定理、启发、失败模板、待证义务。

证据文件一旦被update引用便保留不可变；修订另建v2文件，不静默改写。研究状态只能通过CLI单写入。源代码改动先测试、冻结新版本后切换，不能直接改发布快照。

数学目标未解决时保持UNRESOLVED。没有局部待做工作时，给出具体未解引理和缺失输入；不得把“需要新想法”包装成后台任务，也不得用心跳空转或无穷自驱循环冒充进展。
