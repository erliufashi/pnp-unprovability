# 10小时研究窗口中的独立子线性空间分支

## 当前窗口：已暂停且完成行政验收

原定2026-11-05 09:17:58截止，实际09:19:24确认一次暂停；两个专用monitor均off，实际post-pause探针静默。九批局部复核完成，窗口本身已独立验收通过，不自动续期。标准P/NP/ZFC不可证性仍未解决，旧数学goal保持未解。

- 汇总：[window-final-v1.md](reports/window-final-v1.md)
- 时间窗口正式回执：[window-review.receipt.json](reports/window-review.receipt.json)
- 当前验收状态：[window-acceptance-v1.json](reports/window-acceptance-v1.json)

后面的hour条目及proof头部保留各自写作时状态；当前复核以对应receipt为准。

本目录不改变已认证T3或原35节点。它是新研究，不是自动追加到停止证书的条件。

## 当前局部结果

- log n≤f(n)=o(n)的单遍多项式模型，仍有INDEX∈NP_f而不在P_f，甚至不在BPP_f。
- 对明确纯行局部有限精度DAG，只改存储/合法拓扑调度、保留原primitive及归约树，可将attention中间矩阵峰值从C²值降到O(Cd)，正常数值输出逐位不变。
- 原型36组C/d/causal例子逐位相等；4个规模的Python辅助内存测量另见reports/hour1-tests.json。它不测GPU或实际LLM，也不由有限样本证明渐近界。
- 浮点重结合及资源OOM返回已给反例：数值实数公式相等或优化后正常输出相等，都不足以自动保证整个API协议不变。

## 稳定已有入口（无需新安装）

```
pnp-research --root /home/desk/projects/pnp-unprovability/alternatives/sublinear-stream status
pnp-research --root /home/desk/projects/pnp-unprovability/alternatives/sublinear-stream next --json
pnp-research --root /home/desk/projects/pnp-unprovability/alternatives/sublinear-stream refresh --reason context-resume --json
```

同一冻结控制器在独立root运行；本分支不接入原mission停止判断。概念收益倍率仍按较弱LLM代理方向0.25看待，不能因实验结果改写原两项目标权重。

证明及必要限定：proof/ENVELOPE-v1.md、proof/ATTENTION-v1.md、proof/QUALIFICATIONS-v1.md（DAG生成器空间、打包数组和标准TM步数口径不可省略）。数值原型：tools/attention_probe.py（标准库）；测试报告与完整日志在reports/。

## 最新候选与后续目标

notes/ALL-QUERY-CANDIDATE-v0.md提出为所有有限query/max/分母维护append-only历史摘要。它可能消除无界KV存储，但尚未认证；模型规模的指数常数、归约树、删除、位置相关score和随机性都必须审计。只把它作为下一小时高新鲜度研究候选，不冒称已覆盖任意真实LLM。

## hour2新增局部工具

proof/KERNEL-SUMMARY-v1.md给有限query/max/分母左折叠摘要的归纳论证；缓存999个玩具域数值单元的实现完成76680次逐前缀query对照（实际子进程exit0）。全部参数表对b/d指数巨大，非实际200B优化；有限试验不替代归纳证明。

原始ALL-QUERY-CANDIDATE-v0提案保留；当前下一候选为PREFIX-TREE-CANDIDATE-v0，尚未证明。最新结果/审查状态见reports/hour2-summary.json，下一步理由见notes/NEXT-v2.md。

## hour3新增局部工具

proof/PREFIX-FOREST-v1.md将摘要推进到一个明确、含seed真实叶子的前缀树族；不使用结合律。实际实验包含33333次通用前缀与76680次kernel query对照；512步流时999个参数森林分配9990个数值槽，实际活跃1998个，二者不能混同。左折叠/删seed重平衡/primitive padding均有负控制。

这不是任意GPU树或完整LLM覆盖。最新审查状态见reports/hour3-summary.json；下一候选是操作prefix-stability与完整因果组合，见notes/NEXT-v3.md。

## hour4新增条件性提升

proof/CAUSAL-CONTRACT-v1.md区分mask、增量reference与跨shape逐位prefix-stability；给generic masked reducer反例，不冒称真实GPU。proof/CAUSAL-COMPOSITION-v1.md在精确kernel接口前提下作位置/层/头归纳，计费采样/输出/位置/各head临时计数。

247个有限toy实例（240普通、2guard、1EOS、4长例）完成2539步trace/10156头计数/1551随机状态检查。实际toy长例编译31968槽对原KV1072更大；这不是实际内存优化。最新独立审查状态见reports/hour4-summary.json。下一方向是质量-资源分层充分性，见notes/NEXT-v4.md，不自动改变原T3。

当前因果组合证明必须同时读proof/CAUSAL-RESOURCE-QUALIFICATIONS-v1.md：S(t)取前缀峰值包络，采样/控制另有log空间要求，有限时间不自动推空间；输入输出功能指标不等于硬件预算。

## hour5新增充分性工具

D7/M16将功能law、渐近计算、明确预算可用性、人类代理假设分开。proof/APPROX-TRANSFER-v1.md给吸收EOS的逐步TV/有界风险界、task slack与margin/理想softmax条件；不从小数值误差猜实际准确率。proof/RESOURCE-LEDGER-v1.md区分当前live、peak live、allocated与RSS。

指定toy槽模型的allocated永久交叉6494、peak-live5994；instant-live首次511但512又失败、永久5119，均有分析/有限域覆盖依据。2048词槽预算只是合成observer反例，未强制OS故障，也非用户接受值或200B实测。具体构造差不证明所有编译器差，旧T3未改。最新状态见reports/hour5-summary.json，后续目标见notes/NEXT-v5.md。

## hour6新增参数化下界

proof/NEURAL-RETRIEVAL-v1.md给稀疏ReLU equality-score/指定binary32 one-hot检索族，非stock bilinear或实际训练模型。proof/MODEL-STATE-LOWER-v1.md由INDEX另证固定d/horizon下包括控制的状态需Ω(2^d)，区分无界模型族与固定200B/单π/任意常数。没有从既有坏上界倒推，也不证明现有上界全部因子最优。

有限实验实际exit0：5460 equality pairs、4240小d全值/query双layout比较、384随机双layout，exp32(-120)=0。源码最后的expected x_j断言仅为输出已经计算完后的测试observer，可删去而不改变神经数据流；未给reference/未知编译器外部答案。

最新审查见reports/hour6-summary.json；后续建设性特殊结构优化见notes/NEXT-v6.md，而非否定全部实际baseline。

## hour7证书特化

SELECTED-PARAMETER-PRUNING-v1.md给静态域/精确签名和selected m/z证书；COST-v2只澄清v1表述，旧哈希及重复管理更正历史保留。实际K3996→752/776，p134仍比原KV大，metadata不免费。54212 kernel比较与2539三路feed/1551 RNG检查通过，详见reports/hour7-summary.json。未扩大T3或声称200B性能；新候选见notes/NEXT-v7.md。

## hour8固定H混合

proof/HORIZON-HYBRID-v1.md给稳定边界内部KV重建/保控制RNG；proof/NONVACUITY-v1.md审计有限范围和巨常数量词。480cases实际通过，但普通H16长例仍比native大，2×仅为条件性cache子界。第1次非法JSON未计通过、第二次合法回执已独立通过。详见reports/hour8-summary.json和notes/NEXT-v8.md；不改T3/标准P/NP。

## hour9有限state预算

数值D_s/ND_s及随机INDEX阈值见proof/FINITE-BUDGET-SEPARATION-v2.md、FINITE-BUDGET-RANDOM-v2.md；v1原件保留，v2只澄清payload/wire单位。948协议cases/7368 ND分支和131344小prefix映射实际通过；非Python RAM、实际200B/human或标准P/NP结论。详见reports/hour9-summary.json，首个坏JSON未计pass、第二合法回执通过。本窗口研究批次已收束，仍等待原09:17:58截止闹钟，不提前声称已暂停。
