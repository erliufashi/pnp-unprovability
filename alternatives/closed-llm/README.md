# T3：受限单遍算法空间与封闭200B LLM代理

新分支独立于原25节点；收益倍率0.25，原T1/T2各1。原研究文件、参数、轮号和评分不变。

## 一次性输入协议

本分支的封闭profile按通常提示—生成协议解释：完整提示EOF到达后才生成答案，不把输入前缀先输出给外部解码器作为额外记忆。内部推理、输出反馈窗口与随机状态均已计入profile。任务编码和解码不得偷偷调用外部求解器。

## 数学内容

- 模型M：单遍输入、O(log n)工作空间、多项式时间。
- INDEX属于NP_M，不属于P_M，甚至不属于逐输入错误≤1/3的BPP_M。
- 任意符合固定有限精度/上下文/存储/运行预算profile的封闭≤200B LLM可统一模拟，保持输出分布及代理任务指标。

这是条件性的LLM代理结果，不是标准P≠NP，不是已验证人类能力覆盖，不涵盖无限上下文或无限可回读输出。

## 入口

```
pnp-research alt status
pnp-research alt next --json
pnp-research alt check --json
pnp-research mission priorities --json
pnp-research mission status --json
pnp-research mission refresh --reason context-resume --json
```

alt固定使用本分支root，拒绝--root覆盖，防误写旧节点。原status/next/check等命令仍使用原图谱。mission刷新只更新新分支局部时钟和新增mission记录，不改变旧状态。

证明：[proof/MAIN.md](proof/MAIN.md)、[proof/RANDOMIZED.md](proof/RANDOMIZED.md)、[proof/LLM-SIMULATION.md](proof/LLM-SIMULATION.md)。任务定义：[TASK-SPACE.md](TASK-SPACE.md)。完整边界：[proof/SCOPE.md](proof/SCOPE.md)。

当前T3已完成独立审查，正式pass回执已核对并绑定SHA256，状态为proved_conditional_proxy。mission status.stop=true仅表示上述封闭LLM代理条件下允许停止，standard_targets_unresolved=true；原未解目标不改标。

正式回执的逐字节持久副本在主目录reviews/pnp-t3-submit-2.receipt.json；原始工具路径和校验记录在reports/t3-certificate-check.json。此前只读执行权限受阻的FAIL回执仍保留，不覆盖历史。
