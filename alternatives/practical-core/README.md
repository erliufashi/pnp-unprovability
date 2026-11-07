# `practical-core`：能力保全算法空间与多研究员共享板（T3-v2 分支）

本分支对应用户对 T3 目标的优化指令：摒弃早期不准确的“200B 参数量封闭单遍代理”，转向研究**如何在严格收缩算法空间以暴露确定性/非确定性分离的同时，保全解决绝大多数现实任务所需的基础计算、重读、索引、更新与验证闭环能力**。

- **当前结论状态**：`T3-v2` 总体目标保持 **`UNRESOLVED`**。本分支完成了 54 个节点、88 条依赖边、95 轮带锁事务推进，产出了系统的能力—分离边界定理、精确反例、文献漏洞修补与六维可比性合同。

## 核心入口文档

- [CONTRACT-v2.md](CONTRACT-v2.md)：有界算法空间 $A_\Gamma$ 的资源账本、公平 $ND_\Gamma$ 准则与六维 `INVALID_COMPARISON` 判定表
- [TASK-SPACE-v2.md](TASK-SPACE-v2.md)：统一可执行路由量词、双轴现实覆盖指标与含未知质量/选择罚项的统计下界
- [coverage-spec.json](coverage-spec.json)：机器可读的合同坐标与未决外部输入清单
- `research/shared-board.json`：权威单文件三层图谱、节点状态与不可变证据 SHA256 账本（`graph.json` 与 `state.json` 为兼容投影）
- `evidence/<NODE_ID>/<SHA256>.md`：47 个已完成/耗尽节点的自包含不可变证据（内嵌完整推导、探针源码与核验结果）

## 常用只读核验命令

```sh
# 校验 54 节点三层 DAG 结构（仅允许 3→2→1）及全部已发布证据 SHA256 完整性
python3 alternatives/practical-core/tools/board_v1.py check

# 查看全部节点按价值/余值/新鲜度/邻接传播计算的排名快照
python3 alternatives/practical-core/tools/board_v1.py status
```

## 代表性节点索引

| 类别 | 节点 ID | 核心结论摘要 |
| :--- | :--- | :--- |
| **旧路线证伪与逃逸阈值** | `E49`, `A57`, `C56`, `ASTRA-CHIEF-CUTOFF-AUDIT-1` | 一次重读即可用 $O(\log m)$ 空间解全部 `INDEX`；亚线性探针 `OR` 分离无法容纳全输入 `SUM`（$7n+9$ 步）；明文值域允许 $M \ge \lceil 2^w/w\rceil$ 时基数查重 $O(n)$ 步击穿碰撞下界 |
| **证明带与黑盒协议边界** | `E-chief-cert-1`, `C57`, `E-chief-OPAQUE-1`, `ASTRA-F-OPAQUE-ALPHABET-1` | 双单调只读头配 $O(\log n)$ 空间即可恢复整个 $\mathrm{NP}$（禁止免费长证书）；`CMP` 的 $\lceil\log_2(n!)\rceil$ 下界与隐藏 oracle 下界均依赖输入可见性/响应位宽限制 |
| **全扫描 BRAM 候选与瓶颈** | `E-chief-dom-1`, `E-argon-FNS-audit1`, `C62`, `E-argon-RAND-ED-2`, `E-chief-RAND-BRAM-1` | $M=\lfloor\sqrt{n}\rfloor, F=32n+512$ 同时容纳 `SUM`/`DOT` 与 `ND_COLLISION` 并由 BSSV 排除渐近确定性 BRAM；但显式交叉点达 $n=2^{3315164}$，且常数 $1/3$ 错误率随机化下界尚未闭合 |
| **文献修补与访问鸿沟** | `E-chief-PPST-1`, `C59`, `C60`, `C61` | 核实 PPST 顺序多带同线性预算分离；发现并自包含修补 Cook–Moshkovitz (CCC 2024) Lemma 52 计数漏洞，确立 $h S_{\mathrm{aug}} T > \delta N^2 / 18432$ |
| **索引、动态更新与验证闭环** | `ASTRA-E-PARITY-INDEX-1`, `B56`, `B57`, `D-GVC-BATCH-1`, `D-GVC-STATE-1`, `D-GVC-RETRY-1` | 非线性可复用索引紧界 $2^s\sum_{i\le q}\binom{N}{i} \ge 2^N$；支持 $U$ 次 `SET` 更新的初始状态紧界 $1+\sum_{k\le U}\binom{N}{k}$；批量 1-bit 验证紧容量 $F(K,L)=1+\sum_{j<K}\min(L,2^j)$ |
| **组合工作流与统计防过拟合** | `E47`, `E48`, `B54`, `C55`, `A56`, `E-CLOSURE-ADVICE-1`, `E-chief-compose-1`, `ASTRA-CHIEF-CONTRACT-MATRIX-1` | 自适应调用逐步条件 TV 耦合与边界路由放大反例；前缀码先验抗评测集过拟合；六维 `INVALID_COMPARISON` 合同矩阵 |
