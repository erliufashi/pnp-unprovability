# 摘要恢复卡

## 新增T3的当前恢复入口

处理T3时执行`pnp-research mission refresh --reason context-resume --json`，然后读`mission status`、`mission priorities`与docs/EXTENSION-T3.md。不要借本次新增任务刷新/修改旧节点。以下旧流程仅在主动恢复原标准数学研究时使用。T3是有限封闭LLM代理条件，不是原P/NP或人类等价证明。

## 必做第一步

```
pnp-research refresh --reason context-resume --json
pnp-research next --json
pnp-research check --json
```

若PATH暂未包含用户bin，用/home/desk/.local/bin/pnp-research。读取proof/MAIN.md、proof/obligations.json与推荐节点产物，然后依据research/state.json和history.jsonl恢复，不只相信摘要文字。

## 当前真实状态

- 主目标：ZFC中标准E或¬E的明确一侧不可证；未解决。
- 系统：三层依赖3→2→1，4方向/7工具/14初始证据节点；优先级是启发式。
- 首轮已执行：11个叶节点局部完成、E4/E13两个模板耗尽、E12阻塞。图谱已显式演进为25节点32边，新增E12→M7，备份及演进验收见reports/graph-migration-v2.json。
- 最新局部结果：S在T内精确等价于E的局部反思；真正可独立的怪oracle仍欠标准表示转移；SAT反例搜索h有真实上界判据，尚无所需的SAT特定增长引理。
- 当前前沿D2/M7/E12：先读notes/07-frontier-v1.md。next返回null是因为没有可执行ready叶节点，不是数学目标完成；没有后台任务在生成缺失定理。只有新证据/具体新机制时显式解冻E12。
- 重要陷阱：Con(T)已足以说明E和¬E不能同时可证，但不点名一侧的析取不能算研究成功。
- 没有Pi自动压缩hook；本卡与AGENTS.md规定看到摘要后的手动/代理恢复操作。

## 记录实际研究

```
pnp-research update E1 --status done --remaining 0 --note '具体依据' --evidence notes/01-gate-v1.md --worked --gain --json
```

证据文件一旦引用，保留不可变。修订使用v2。耗尽使用--status exhausted并附证据；会立即重选。不要只为了让网络继续转动而提高评分或复活节点。研究不是有限测试可判定的问题。

## 行政goal状态

根goal pnp-research仍未完成。pnp-system、pnp-round-1已分别独立验收；pnp-frontier为unready，不伪装成外部任务等待。看到摘要仍先执行刷新；只有核验到新机制/新证据才用task_edit将pnp-frontier恢复ready，并以新证据将E12改回ready。没有新信息就维持前沿状态，不为让系统运转而空转。
