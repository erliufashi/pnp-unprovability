# B58：全扫描、普通计算、动态更新与同Γ分离的兼容性阈值审计

pnp-sol-b，2026-11-06 23:40；分类：能力兼容性条件结果 + 直接寻址逃逸反例，待独立复核。不是现实覆盖、不是标准P/NP结果。

## 1. 核心结论

强reference要求全扫描、普通加法/聚合、可重读raw input和动态SET更新，并不自动与所有分离候选冲突；但分离候选必须公开其存储/值域边界。

对碰撞任务，若输入值域为`[Σ]`且工作数组至少有Σ个可寻址计数/seen word，则同一Γ存在一个确定算法：全扫描建立counts，碰撞查询检查count>1；SET更新只需读旧raw值、调整old/new两个counts。其时间是`O(n+Σ)`冷初始化、`O(1)`每次更新（查询可扫描Σ或维护duplicate counter），空间至少Σ words。故任何声称在同一Γ上排除这种D算法的分离证书，在`M≥Σ`时直接失效。

因此，Argon/FNS型`M=√n`、值域`Σ=n²`候选并非“全扫描能力本身”带来的分离；它依赖`M<Σ`及相应BRAM lower-bound模型。该模型可能保留SUM和有限动态聚合，却不能未经数据/任务证据宣称足够现实能力。对于FNS的n=128示例，Σ=16384而M=128，直接寻址路线明确不可用；这只是路线被排除，不是碰撞下界的完整证明。

## 2. 统一的生命周期账本

固定输入`x[0..n-1]∈[Σ]`，raw data可重读；counts为可写Σ-word数组，初始化清零计费；代码/工具/地址和所有读写均计入同一Γ。

冷启动：清零Σ words + 扫描n个raw values并写入counts，工作为`Θ(n+Σ)`、空间Θ(Σ) words。若强reference也需要完整全扫描，输入读取语义兼容。

SET(i,v)：读取raw[i]获得old，减少counts[old]、增加counts[v]、写raw[i]，另付两次计数更新和地址/版本/日志成本；空间仍Σ+n raw residency（若raw原本是协议输入，不把它冒称可写workspace）。若任务仅需要collision boolean，维护`duplicate_pairs`计数后查询可O(1)：减/增前后按count=2等更新，具体算术成本随word模型计费。

这不是B56重复：B56研究OR摘要能否保全未来更新的状态容量；本节点研究**当值域/存储扩展到强参考所需阈值时，FNS类同Γ分离如何被普通D算法逃逸**。

## 3. 直接算法及自含正确性

初始化counts[v]=0。对每个x_i：若counts[x_i]>0则已发现碰撞，否则设为1。更完整版本记录count，允许动态更新。任意重复值必在第一次重复时被发现；全异数组不会误报。

动态维护：SET(i,v)先读old=x_i；若old≠v，`count[old]--, count[v]++, raw[i]=v`。碰撞谓词等价于存在v使count[v]≥2，故每次query正确。若不保留raw，调用者只给(i,new)时无法知道old；可以要求trusted old作为额外输入，但那是不同协议，必须收费/验真。

可选普通聚合SUM在相同full-scan协议中只需逐项累加；它和counts实现不冲突。该事实只证明具体参考routine可共同实现，不证明跨领域reference portfolio已覆盖。

## 4. 对FNS/同Γ分离的精确边界

FNS候选的固定域`Σ=n²`、工作空间`M=⌊√n⌋`，并允许全输入读取、SUM；其ND collision witness用两个地址猜测。直接寻址算法需要Σ words，故不在该M内。对n=128，Σ=16384、M=128；测试中显式核验`M<Σ`。

但是：
- `M<Σ`只排除这个直接寻址实现，不能排除排序/哈希/外存/压缩或别的确定算法；需要原始BSSV等定理和完整状态映射。
- 强reference如果实际只需要SUM、count小值和有限动态raw更新，FNS profile可能保留这些routine；如果实际需要大值域碰撞、排序、数据库索引或长生命周期状态，则M=√n的能力保全尚未证，甚至很可能失败。
- 把Σ写成“工具外部只读字典”会把输入相关计数状态移出账本，直接破坏同Γ分离。
- 若将M提升到Σ，FNS的特定下界路线被直接寻址逃逸；不应为保存分离结果而把强reference改成弱版，也不应把大值域任务删出分母。

## 5. 资源/接口对照

| 组件 | Σ-word profile | FNS M=√n profile |
|---|---|---|
| raw全扫描/SUM | 可 | 可（已给候选） |
| raw重读 | 可 | 可 |
| 动态SET+collision count | 可，需Σ计数/维护状态 | 直接寻址不可；其他路线未证 |
| 全值域collision D | O(n+Σ)冷启动 | BSSV候选下界审计中 |
| ND猜pair | 可 | 可（FNS witness） |
| 现实广度/人类代理 | 未测 | 未测 |

注意“可实现”仅是语义/渐近算法，不代表固定硬件时间、编译器、持久化、并发、故障或真实human效能已验。

## 6. 失败边界和下一步

这条结果对目标的价值是**反驳过强的兼容性/分离联结**：全扫描本身不杀分离，完整值域存储可能杀掉特定BRAM分离；两者要在同一Γ中逐项列账。

必须继续保留的未决义务：
1. 固定真实reference的值域、更新类型、raw residency、峰值workspace及冷/暖生命周期；
2. 对FNS M=√n候选核强能力是否足够，不能从SUM成功外推；
3. 对M≥Σ的DirectAddress D算法核地址位宽、初始化、计数、动态duplicate counter和总Γ；
4. 若使用randomized collision/hash，明确错误概率、seed、字典、重建与外存成本；
5. 不把此局部阈值结果写成P≠NP或现实覆盖通过。

## 7. 复现

`fullscan_dynamic_escape.py`只用标准库，4项测试通过，日志`fullscan-dynamic-escape-tests-v1.txt`：SUM+collision全扫描同账本、值域容量阈值、动态更新正确性、FNS n=128的M<Σ负控制。

程序是研究语义参考，不是已安装消费者服务；Python host内存/墙钟不是abstract Γ。共享板B58通过CLI publish为不可变证据，旧B56/B57/PPST及旧104文件未改。
