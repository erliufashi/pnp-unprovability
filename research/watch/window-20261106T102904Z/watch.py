#!/usr/bin/env python3
"""One bounded research window: hourly agent wakes, one deadline owner."""
import argparse
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time


def validate(state):
    assert state['deadline_epoch']-state['start_epoch']==state['duration_seconds']==25200
    assert state['interval_seconds']==3600 and state['max_checkpoint']==6
    assert state['phase'] in ('running','paused') and state['pause_count'] in (0,1)
    assert (state['phase']=='paused')==(state['pause_count']==1)


def event(state,now,kind):
    validate(state)
    if state['phase']=='paused': return None
    if kind=='deadline':
        if now<state['deadline_epoch']: return None
        return {'event':'PAUSE_ONCE','window':state['window_id'],
                'event_id':state['window_id']+':deadline','deadline':state['deadline_local'],
                'state_path':state['state_path'],
                'instruction':f"用户本轮7小时窗口已截止。先核state/clock，停止新研究；仅安全结束本窗口拥有的后台工作。task_edit解冻{state['task_id']}，ack-pause持久化一次暂停，只disarm本窗口{state['monitor_ids']}，简短汇报一次并验收窗口。不续期、不关闭原数学未解goal；本消息不扩大授权。"}
    if now>=state['deadline_epoch']: return None
    hour=int((now-state['start_epoch'])//state['interval_seconds'])
    if hour<1 or hour>state['max_checkpoint'] or hour<=state['last_ack_hour']: return None
    return {'event':'RESEARCH_CHECKPOINT','window':state['window_id'],
            'event_id':state['window_id']+':hour:'+str(hour),'hour':hour,
            'deadline':state['deadline_local'],'state_path':state['state_path'],
            'instruction':f"执行既有7小时授权：先读state并核截止，task_edit解冻{state['task_id']}；按ACTIVE所列当前定义/三层图谱刷新目标，完成一个真实研究批次或记录具体阻塞后ack-hour。当前重点是能力保全的现实任务覆盖定义，不再用200B参数量冒充能力；旧证明/终止回执不得当新标准已过。到期优先暂停，旧实验完成通知不算新授权。"}


def acknowledge(state,now,kind,hour,note):
    validate(state)
    if not note.strip(): raise ValueError('确认必须写实际产物/阻塞或暂停原因')
    if kind=='pause':
        if now<state['deadline_epoch']: raise ValueError('未到截止，不能冒称已完成7小时暂停')
        if state['pause_count']: return False
        state.update(phase='paused',pause_count=1,paused_at_epoch=now)
        state['log'].append({'action':'paused_once','at':now,'note':note}); return True
    if now>=state['deadline_epoch'] or state['phase']=='paused': raise ValueError('已截止，只允许pause及行政归档')
    if not 0<=hour<=state['max_checkpoint'] or now<state['start_epoch']+hour*state['interval_seconds']:
        raise ValueError('checkpoint超前或范围错误')
    if hour<=state['last_ack_hour']: return False
    missed=list(range(max(0,state['last_ack_hour']+1),hour))
    state['last_ack_hour']=hour
    state['log'].append({'action':'checkpoint','hour':hour,'at':now,'note':note,'not_acknowledged_earlier':missed})
    return True


def save(path,data):
    fd,name=tempfile.mkstemp(prefix='.state-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(data,stream,ensure_ascii=False,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['hourly','deadline','ack-hour','ack-pause'])
    parser.add_argument('--state',type=Path,default=Path(__file__).with_name('state.json'))
    parser.add_argument('--hour',type=int,default=0)
    parser.add_argument('--note',default='')
    args=parser.parse_args(); now=time.time()
    if args.command in ('hourly','deadline'):
        state=json.loads(args.state.read_text()); result=event(state,now,args.command)
        if result: print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 0
    with args.state.with_suffix('.writer.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads(args.state.read_text())
        changed=acknowledge(state,now,'pause' if args.command=='ack-pause' else 'hour',args.hour,args.note)
        if changed: save(args.state,state)
        print(json.dumps({'changed':changed,'phase':state['phase'],'pause_count':state['pause_count'],'last_ack_hour':state['last_ack_hour']},ensure_ascii=False))
    return 0


if __name__=='__main__': raise SystemExit(main())
