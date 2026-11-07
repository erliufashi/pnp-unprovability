# 操作与交付边界

> 下文保留0.1.0原内核操作说明。当前入口hub为0.3.0（兼容0.1.0/0.2.0全部旧命令）；`pnp-research mission status --json` 现明确区分早期 `T3-v1` 历史有限单遍代理与 `T1/T2/T3-v2` 当前 `UNRESOLVED`（阶段性收官）状态，并新增只读 `pnp-research practical status|check [--json]` 入口（`practical` 写入仅走 `alternatives/practical-core/tools/board_v1.py`）。`0.3.0 → 0.2.0 → 0.3.0` 原子回退及清洁普通 shell 验收见 `reports/wrapup-cli-acceptance.json`；早期 T3-v1 扩展说明见 [EXTENSION-T3.md](EXTENSION-T3.md)。旧研究状态与证据不因升级而变化。

## 消费者与稳定入口

人类：普通shell执行pnp-research；机器：同一CLI加--json，stdout为一个UTF-8 JSON对象。失败退出2，成功0；--help和参数解析遵循argparse（参数解析错误写stderr）。没有GUI、服务、网络、认证、后台模型调用；这些验收不适用。

固定入口：/home/desk/.local/bin/pnp-research
配置：~/.config/pnp-research/config.json，只保存root一次；支持XDG_CONFIG_HOME。
代码：~/.local/share/pnp-research/releases/0.1.0/research.py
激活：~/.local/share/pnp-research/current，指向冻结版本。
源码：/home/desk/projects/pnp-unprovability/src/research.py
运行数据：研究目录research/{graph.json,state.json,history.jsonl,snapshots/}

依赖：系统Python>=3.10（已用3.13.15验收）、Linux fcntl；launcher使用/run/current-system/sw/bin/python3，不依赖agent PATH、venv或当前cwd。版本与SHA256见发布目录release.json。唯一writer为当前主研究代理或用户发起的CLI；并发写操作会失败，不自动换owner。

## 常用命令

```
pnp-research status
pnp-research next --json
pnp-research check --json
pnp-research paths --json
pnp-research history --json
pnp-research refresh --reason context-resume --json
```

update需记录可审计依据。完成或耗尽必须附研究目录内的非空证据文件。--worked表示确实研究过，--gain表示获得新信息（不是必须证明成功）；无增益的worked会衰减新鲜度。证据被SHA256固定，修订另建版本。

```
pnp-research update E1 --status done --remaining 0 --note '证书和归约已逐项核验' --evidence notes/01-gate-v1.md --worked --gain --json
```

状态：open是上层未结；ready可研究；blocked确有缺失输入；done完成局部验收；exhausted表示此具体模板已无剩余信息价值。done不证明上层结论。重新启用exhausted必须有新的证据、R>0和不同于旧模板的操作；不得仅因时间经过复活。

## 快照与状态恢复

```
pnp-research snapshot --json
pnp-research restore <上一步返回的快照文件名> --reason recovery --json
pnp-research check --json
```

恢复对象是节点参数、局部状态、证据引用；不删历史，不回退已发生的轮号，不删除研究文稿。restore后按恢复参数重新评分；新事件记录来源快照。图谱digest不一致时拒绝恢复，以防把新图谱覆盖成旧状态。

state.json及其中events是权威；history.jsonl是投影。单文件原子写入、非阻塞writer锁；不声称两个文件跨文件原子事务或断电零损失。若投影缺失/不一致，先备份，再refresh --reason repair-projection即可从state.events重建。state.json损坏时从最近合法snapshot恢复文件（先保留损坏文件并停止其他writer），随后check/refresh；不要伪造丢失事件。

## 图谱演进

0.1不支持在线静默增删图谱。要加入新的第3层研究节点：停止writer，保存完整research快照及旧graph/state/history，生成仍符合3→2→1的新graph，显式迁移保留全部旧节点参数及事件、为新节点初始化参数、重算graph_digest，再check和refresh --reason graph-migration；迁移脚本与前后digest须留档。未完成此协议前不要直接编辑graph.json。本限制不妨碍现有节点的动态调度与摘要恢复。

首轮实际进行过一次显式演进：tools/migrate_graph_v2.py在单writer锁下增加E12→M7，保持三层和全部节点参数/审计历史；先在带空格的隔离目录演练并确认重复迁移拒绝，再应用正式图谱。报告reports/graph-migration-v2.json；旧三文件完整保留于research/migrations/001-before-v2/。这是小型图谱内容演进，不移动用户目录。回退需在停writer后保留当前三文件，再整套恢复该备份，随后check和refresh记录恢复；不同图谱digest的snapshot不能混用。

## 控制器更新、回退与卸载

代码更新须先跑测试，在新的版本目录冻结源码并记录SHA256，再用临时symlink+os.replace原子切换current；不能直接改0.1.0快照。回退只切回已验收的旧版本，不改研究状态；若新版本改了状态schema，则先做兼容性审查并按状态快照恢复，不盲目切换。

本次是初次安装，**没有旧控制器版本可回退**；已实测的是研究状态快照恢复，而不是虚称做过新旧版本切换。初次安装撤销：删除本工具的bin入口、current和0.1.0发布目录以及本工具配置；保留项目研究数据和证据，除非用户另行授权删除。全局local-resources登记同时标记撤销，不改用户shell/桌面/模型配置。

## 验收

```
cd /home/desk/projects/pnp-unprovability
python3 -m unittest discover -s tests -v
python3 tests/acceptance.py
```

acceptance在env -i、普通POSIX shell、任意cwd、只保留系统与用户bin PATH的环境启动真实固定入口，验证帮助、版本、check/status/JSON消费、无PI变量依赖、隔离状态的冷/暖多进程调用、摘要恢复刷新、耗尽重选和快照恢复。测试路径含空格。报告reports/acceptance.json逐项记录，失败会返回非0，不靠runner退出0掩盖。权限/秘密/认证/GUI/整机重启不在此纯本地CLI的适用范围；不宣称主数学结论已验证。
