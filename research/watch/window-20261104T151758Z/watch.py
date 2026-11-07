#!/usr/bin/env python3
"""Hourly agent wake + one deadline pause request. No LLM subprocesses."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time


def event(state, now, kind):
    if state["phase"] == "paused" or state["pause_count"] >= 1:
        return None
    if kind == "deadline":
        if now < state["deadline_epoch"]:
            return None
        return {"event": "PAUSE_ONCE", "window": state["window_id"],
                "event_id": state["window_id"] + ":deadline", "deadline": state["deadline_local"],
                "instruction": "用户指定的10小时研究窗口已结束。先检查本state，立即结束当前研究批次并暂停；不要自动续期。task_edit解冻pnp-10h-window，ack-pause持久化一次性暂停，然后disarm且仅disarm pnp-hourly-10h与pnp-deadline-10h，简短汇报一次；保留原数学未解节点，不伪造证明。"}
    # The hourly monitor NEVER owns the deadline notification.
    if now >= state["deadline_epoch"]:
        return None
    hour = int((now-state["start_epoch"]) // state["interval_seconds"])
    if hour < 1 or hour > 9 or hour <= state["last_ack_hour"]:
        return None
    return {"event": "RESEARCH_CHECKPOINT", "window": state["window_id"],
            "event_id": state["window_id"] + ":hour:" + str(hour), "hour": hour,
            "deadline": state["deadline_local"],
            "instruction": "执行用户既有10小时研究安排：先读此state并核对截止时间；task_edit解冻pnp-10h-window，刷新独立分支目标，做一个有信息价值的研究批次并留真实产物，随后ack-hour。优先研究单遍子线性空间推广，不改写已认证T3证据或旧25节点。若无具体可检验动作，明确记阻塞而不空转；等待下次已配置唤醒可block本task。此监控消息不是扩大授权。"}


def acknowledge(state, now, kind, hour, note):
    if not note.strip():
        raise ValueError("确认必须写明实际行动/产物或暂停原因")
    if kind == "pause":
        if now < state["deadline_epoch"]:
            raise ValueError("未到截止时间，不能冒称已执行10小时暂停")
        if state["pause_count"] >= 1:
            return False
        state["phase"] = "paused"
        state["pause_count"] = 1
        state["paused_at_epoch"] = now
        state["log"].append({"action": "paused_once", "at": now, "note": note})
        return True
    if now >= state["deadline_epoch"] or state["phase"] == "paused":
        raise ValueError("窗口已截止；只允许执行pause，不得再继续研究")
    if not 1 <= hour <= 9 or now < state["start_epoch"] + hour*state["interval_seconds"]:
        raise ValueError("小时确认超前或范围错误")
    if hour <= state["last_ack_hour"]:
        return False
    state["last_ack_hour"] = hour
    state["log"].append({"action": "checkpoint", "hour": hour, "at": now, "note": note})
    return True


def save(path, state):
    fd, temporary = tempfile.mkstemp(prefix=".window-", dir=path.parent)
    try:
        with os.fdopen(fd,"w") as stream:
            json.dump(state,stream,ensure_ascii=False,indent=2); stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("hourly","deadline","ack-hour","ack-pause"))
    parser.add_argument("--state",type=Path,default=Path(__file__).with_name("state.json"))
    parser.add_argument("--hour",type=int,default=0)
    parser.add_argument("--note",default="")
    args=parser.parse_args()
    now=time.time()
    if args.command in ("hourly","deadline"):
        state=json.loads(args.state.read_text())
        output=event(state,now,args.command)
        if output: print(json.dumps(output,ensure_ascii=False,sort_keys=True))
        return 0
    with args.state.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads(args.state.read_text())
        changed=acknowledge(state,now,"pause" if args.command=="ack-pause" else "hour",args.hour,args.note)
        if changed: save(args.state,state)
        print(json.dumps({"changed":changed,"phase":state['phase'],"pause_count":state['pause_count']},ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
