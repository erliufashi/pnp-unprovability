# ASTRA-CHIEF-CONTRACT-MATRIX-1：同权限、同生命周期能力/分离合同矩阵

分类：campaign综合审计，待独立验收；不是新的现实覆盖证书、标准P/NP结论或T3-v2通过。目的不是把局部定理相加，而是阻止把不同输入通道、反馈字母表和生命周期账本的结论非法迁移。

## 1. 六个必须冻结的坐标

每个候选算法空间都必须在评测前冻结：

1. **输入可见性**：透明raw bit/word、opaque equality/CMP、可信summary、外部工具返回值；读取粒度和地址/时钟/错误泄漏。
2. **响应字母表**：每次反馈的bit数、候选批上限、是否能返回任意certificate；response alphabet本身是信息资源。
3. **persistent state**：data-dependent index/code/cache、PC/地址/RNG/log/版本/输出；静态代码与数据特化状态分开。
4. **生命周期**：Build/preprocess、cold query、warm query、update/rebuild、总query horizon H；不能用未声明的无限H摊销prep。
5. **组合/历史**：路由、重试、环境隐状态、候选保留和失败/超时；逐步kernel必须条件于可达历史。
6. **成功量词**：全输入/全历史、uniform average、声明promise、现实分布；不能把其中一个量词换成另一个。

缺任何一格时，比较标签是`INVALID_COMPARISON`，不是“分离”。

## 2. 当前证据的矩阵定位

| 证据 | 输入/接口 | 已支付的结论 | 能继承什么 | 明确不能继承 |
|---|---|---|---|---|
| OPAQUE-v2 / ASTRA-F | 私有键+CMP或二元equality | 比较树/反馈字母表局部下界；raw值/summary会逃逸 | 协议下的计数证明 | 透明raw BRAM、SUM/DOT、现实能力 |
| FNS/C62 | raw word、一般BP映射、fullscan；确定性/强错误条件 | 在明确BRAM账本与原始BP定理条件下的确定性候选 | 同一BP模型的条件推论 | BPP(1/3)直接迁移、物理可行性、human coverage |
| RAND-ED审计 | 同类fullscan目标，但BSSV误差门槛过强 | 证明强错误来源不能当常数错误来源；pair-sampling负控 | 特定算法族的失败/限定promise界 | 全类随机下界 |
| D-GVC-BATCH-1 | hidden答案反馈，每轮至多L候选，bit reply | 容量F(K,L)的决策树界 | 相同反馈接口/候选成本模型 | raw SAT验证器或opaque多bit certificate |
| B56/B57 | raw Build后dynamic SET/update/OR | persistent state容量及逐bit动态解码界 | 相同update、oldbit/raw信道、逐输入历史量词 | 静态一bit索引、短update窗口、D/ND分离 |
| ASTRA-E parity-index | raw database、query mask、可复用data-dependent index | `2^s Σ_{i≤q} C(N,i) ≥ 2^N`必要frontier | 相同Build/Query/raw probe、全query exact | 现实效率、随机/approx、免费代码/无限H |
| D-GVC-RETRY-1 | 反馈/环境可读状态 | answer-independent retry仅加预算，answer-dependent state增加transcript alphabet | 同生命周期/状态重置契约 | 把环境输出当免费独立CPU |

该表是类型检查和证据定位，不声称这些列的结论组成一个共同A。

## 3. 典型非法迁移规则

- **opaque→raw**：CMP的`Ω(n log n)`比较树不能用于raw values；direct addressing/hash/summary可能在线击穿。
- **raw→opaque**：raw fullscan collision候选不能当CMP黑盒分离；改变输入接口就是改变任务。
- **强错误→1/3**：BSSV的ε随T/n变化的定理不能直接给常数错误BPP。pair sampling反控制只否定该算法族。
- **bit feedback→candidate identity**：K个1-bit最多2^K叶；`log m`轮只够区分m个候选，不够恢复m-bit secret。批验证容量另按F(K,L)。
- **静态index→动态update**：B56/B57显示未来SET会给初始状态收费；只存OR/count不能自动保留未来能力。
- **Build可计算→无泄漏**：Build可暴力枚举有限答案或读标签；须非干涉性、允许视图、源码/数据独立性和cold/warm账本。
- **单模块误差→工作流误差**：自适应历史和环境状态必须有条件kernel界；模块benchmark平均误差不能覆盖选择后的边界查询。
- **有限/大常数→现实大部分**：形式`∀H∃B_H`、固定promise或toy穷举不能替代冻结reference、现实分层分布和执行轨迹。

## 4. 能力保全与分离的共同验收门

要把一项局部候选升级为T3-v2材料，至少需要同一份冻结contract同时给出：

- strong reference及统一路由，未按题目答案挑程序；
- 输入/工具/索引/反馈/环境/更新的权限完全对齐；
- 同一Γ的时间、代码、persistent state、峰值live和冷启动/摊销分母；
- 分离两侧的成功量词一致（全输入/历史或明确promise）；
- 形式模拟/严格D-ND分离/现实分布覆盖三种证书分别独立，未知μ/Γ/漂移不设为0。

当前矩阵仅暴露缺口，不关闭任何主目标。T1/T2/T3-v2仍`UNRESOLVED`。
