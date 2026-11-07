# 每小时唤醒、10小时后暂停一次

时区Asia/Shanghai（UTC+8）。墙钟窗口：2026-11-04 23:17:58 → 2026-11-05 09:17:58。主会话每小时获得一次研究唤醒；另有60秒无输出的截止保护。没有启动外部LLM或持续占用算力的子代理，也不把两次唤醒之间的空闲算成实际计算。

两个当前会话监控器：pnp-hourly-10h（3600秒、steer），pnp-deadline-10h（60秒、steer）。前者到截止时间静默，后者是唯一暂停事件owner。shell输出按事件ID稳定去重；到期ack-pause将pause_count置为1，之后两个探针都静默。

## 每次唤醒

1. 读state.json，先核deadline及phase；到期就优先暂停，不能先继续研究。
2. 用task_edit把pnp-10h-window设ready且unblock=true。
3. 未到期时做有产出的研究批次（初选见RESEARCH-00.md），不改写认证T3或旧节点。
4. 实际产出写新文件，再执行：
   `/run/current-system/sw/bin/python3 /home/desk/projects/pnp-unprovability/research/watch/window-20261104T151758Z/watch.py ack-hour --hour <1..9> --note '<实际产物/阻塞>'`
5. 需要等下一小时唤醒时，task_edit设unready，然后task_block，注明两个监控器作为唤醒源。不能因收到旧测试完成通知就自动恢复本窗口。

## 到截止点

1. 停止本窗口的新研究操作，检查ACTIVE.json所列归属本窗口的后台工作。没有启动长期外部LLM研究代理，但各批可能有普通数值实验进程；已完成的只归档，仍运行的按确切任务ID结束或安全收尾，不误杀其他owner进程，也不再启动新批次。
2. task_edit解冻窗口任务，执行watch.py ack-pause --note '<暂停原因/最后产物>'。
3. 仅disarm pnp-hourly-10h和pnp-deadline-10h；不关其他消息接收或有明确观察目标的监控。
4. 简短向用户汇报一次，不自动续期。随后提交本窗口task验收（不要关闭旧数学goal）。

这些监控器仅在当前Pi会话存活，关闭会话会失去唤醒；状态文件持久不等于跨会话agent已在场。没有承诺整机重启/关会话后自动恢复研究。tests.json是隔离时间门控/一次性确认逻辑测试，未冒称真实10小时触发已验收。
