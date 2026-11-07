# Astra-Argon H1 发散审查回执

- 身份：`pnp-argon`；模型要求 `gateway_responses/gpt-6-astra:max`
- 邮件策略：已手动 claim；`paused / followUp / 60s`，本轮未启动代理。
- 本地绝对截止（共享 ACTIVE 合同优先）：`2026-11-07T01:29:04+08:00`；用户消息所写 04:00 与当前窗口合同冲突，未据此延长。
- 结论：T1/T2/T3-v2 均 **UNRESOLVED**。以下是跨节点审查和新的可检验叶，不写共享板。

## 1. 已审节点与关键纠错

1. **常数 1/3 fullscan**：FNS/C62 的确定性 BRAM 碰撞候选不能直接提升为 BPP(1/3) 分离。BSSV 型确定性分支程序下界与常数错误随机化并非同一量词；随机币必须明确是否每个固定输入、每个合法更新/服务历史均有错误 ≤1/3。仅有平均 benchmark 或每轮边际成功率不够。尤其动态 OR 的 B57 说明：更新序列能把一个 OR 查询变成任意坐标恢复，因而 fullscan 下界若不把更新、旧值来源、外部状态一起纳入，就会错算信息通道。
2. **强 reference 兼容**：IDX/GVC 的正确方向是“同一生命周期、同一 cold/warm 分母、同一 raw/index/preprocessing 权限”。强 reference 若拥有预建索引、持久日志、grader 或服务状态，而候选系统只计本地 query workspace，比较不是同预算。`Build` 可计算不等于无标签泄漏；必须对禁止源做 non-interference，并计 Build、版本、更新、重建和共享驻留。
3. **opaque/raw**：OPAQUE comparator 的 Ω(n log n) 比较树只适用于 CMP-only 接口，不是 raw-bit BRAM 定理。切回 `INPUT(i)` 后，低值域直接寻址/基数桶/哈希可能在 O(n) 内查重；若同时保留 CMP 与 INPUT，模型必须声明两种观察权限及各自收费，不能把 comparator 下界嫁接到 raw 模型。
4. **GVC**：重试放大要用“对每个可达 active history 的条件 hazard”，不是边际 p。错误接受也要逐历史条件界；live state 要包含生成器、验证器、候选、反馈 transcript、RNG 与外部环境。一个 1-bit 响应若允许 timing、解释、大小或持久服务状态泄漏，实际信道不再是 1 bit。
5. **动态索引**：B56/B57 已覆盖精确和容错动态 OR 的状态容量；新审查重点是把它作为**协议闭包审计**，防止将 update/raw/log 权限不对称地混入 fullscan 或强 reference 比较。原始数据保留时，辅助摘要下界不能冒充总状态下界；trusted old-bit 也属于更新接口输入，不能免费。

## 2. 新叶提案（非重复，可检验）

### `E-argon-PROTO-CLOSURE-1`：fullscan + 1/3 随机 + GVC + 动态索引的接口闭包矩阵

**依赖**：`C62`/`E-argon-RAND-ED-2`、`B57`、`E-argon-GVC-audit1`、`E-argon-IDX-audit1`、`E-chief-OPAQUE-1`。层级 3→2，建议 novelty 0.99、confidence 0.90、cost 0.8。

**核心命题（待证伪而非宣称已证）**：若算法合同同时允许 (a) raw INPUT 随机访问，(b) O(1) 或有限 U 次 SET/update，(c) verifier/服务的可读反馈，或 (d) 可复用 `DATA_idx`，则“全扫描 collision 的 D vs ND”只有在把这些能力作为双方相同、可重置、可计费的接口后才有意义。否则可构造协议改写：
- raw + `M≥2^w` 时基数桶 O(n) 查重；
- trusted old-bit 或 raw 保留时动态 OR 可由 count 支持，不能套 query-only 摘要界；
- opaque CMP 与 raw INPUT 混合时，CMP-only 比较下界失效；
- 持久 verifier 的反馈/日志可携带输入相关状态，绕过“本地 M=√n”账本。

**验收脚本/证据要求**：
1. 冻结一个最小协议 JSON，分别列 `INPUT/CMP/SET(oldbit)/CMP-feedback/Build/Query/reset`，逐项标注输入相关信息、双方可见性、成本和是否跨 trial 持久。
2. 对同一 `Gamma=(w,F,M,B,O)` 生成四个配置：Raw-only、CMP-only、Raw+dynamic、Raw+stateful-verifier；运行 `COLLISION`/`OR`/`SUM` 的确定、随机(ε=1/3)、ND 实例，输出 cold/warm/重置后结果。要求随机配置按固定输入及每个合法历史测试，不用平均分数。
3. 自动检查“双边同权限”：若 ND 获得 index/verifier state 而 D 没有，或 D 被禁止而 ND 可读，则标记 `INVALID_COMPARISON`，而不是报告 separation。
4. 对随机侧只在满足逐固定输入/历史的误差合同后引用 Yao/分支程序结论；若仅有边际错误率，输出 `NO_LOWER_BOUND`。对动态侧计 `raw + version + log + oldbit` 全部可读状态。
5. 对强 reference 生成生命周期 ledger：`T_build + ΣT_query + ΣT_update + reset/serialization`、峰值 live state、共享索引一次计费；cold first request 独立报告。任何隐藏标签/服务均做 non-interference negative control。

**预期信息增益**：该叶不会再证明一个玩具 OR 或重复 opaque 反例，而是给出“何时分离声明甚至语义无效”的机械判定；若矩阵中某一行在相同接口、固定 1/3、全扫描和完整生命周期下仍保留 gap，才值得升级为新分离候选。最可能结果是若干已有 separation 被标 `INVALID_COMPARISON`，但这正是避免错误进展的可检验产出。

## 3. 当前停止条件与未知量

- 不把 1/3 随机化下界、真实任务分布 ν、强 reference 的跨域覆盖、标准 P/NP 不可证性写成已解决。
- 不修改共享三层图谱或他人文件；本报告是本 cwd 的新文件。
- 仍缺：固定 raw/opaque/动态更新统一协议、常数错误随机化的正式平均/逐输入下界来源、实际 reference 的可审计 provenance 与冷启动数据。
