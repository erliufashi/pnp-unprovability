#!/usr/bin/env python3
"""Unified Astra campaign monitor: hourly checkpoints and one 04:00 stop."""
import argparse,fcntl,json,os,tempfile,time
from pathlib import Path

def validate(s):
    assert s['deadline_epoch'] > s['start_epoch']
    assert s['interval_seconds']==3600 and s['phase'] in ('running','paused') and s['pause_count'] in (0,1)
    assert (s['phase']=='paused')==(s['pause_count']==1)

def event(s,now,kind):
    validate(s)
    if s['phase']=='paused': return None
    if kind=='deadline':
        if now<s['deadline_epoch']: return None
        return {'event':'TEAM_STOP_ONCE','window':s['window_id'],'event_id':s['window_id']+':deadline','deadline':s['deadline_local'],'instruction':'用户指定的Astra研究团队已到04:00终止点：停止所有七位研究员，先保存/交接产物，再ack-pause一次；只停本campaign拥有的run和monitor，不自动续期。'}
    if now<s['start_epoch'] or now>=s['deadline_epoch']: return None
    hour=int((now-s['start_epoch'])//s['interval_seconds'])
    if hour<1 or hour>s['max_checkpoint'] or hour<=s['last_ack_hour']: return None
    return {'event':'TEAM_CHECKPOINT','window':s['window_id'],'event_id':s['window_id']+':hour:'+str(hour),'hour':hour,'deadline':s['deadline_local'],'instruction':'Astra团队每小时检查：读取board/mail并保留真实增量；chief继续亲自研究，七位同权；不要重复总结或更改旧历史。'}

def ack(s,now,kind,hour,note):
    validate(s)
    if not note.strip(): raise ValueError('note required')
    if kind=='pause':
        if now<s['deadline_epoch']: raise ValueError('before 04:00')
        if s['pause_count']: return False
        s.update(phase='paused',pause_count=1,paused_at_epoch=now); s['log'].append({'action':'paused_once','at':now,'note':note}); return True
    if now<s['start_epoch'] or now>=s['deadline_epoch'] or s['phase']=='paused': raise ValueError('outside campaign')
    if hour<1 or hour>s['max_checkpoint'] or now<s['start_epoch']+hour*s['interval_seconds']: raise ValueError('invalid hour')
    if hour<=s['last_ack_hour']: return False
    s['last_ack_hour']=hour; s['log'].append({'action':'checkpoint','hour':hour,'at':now,'note':note}); return True

def save(p,s):
    fd,tmp=tempfile.mkstemp(prefix='.state-',dir=p.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf8') as f: json.dump(s,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['hourly','deadline','ack-hour','ack-pause']); p.add_argument('--state',type=Path,default=Path(__file__).with_name('state.json')); p.add_argument('--hour',type=int,default=0); p.add_argument('--note',default=''); a=p.parse_args(); now=time.time()
    if a.command in ('hourly','deadline'):
        s=json.loads(a.state.read_text()); out=event(s,now,a.command)
        if out: print(json.dumps(out,ensure_ascii=False,sort_keys=True))
        return 0
    with a.state.with_suffix('.writer.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB); s=json.loads(a.state.read_text()); changed=ack(s,now,'pause' if a.command=='ack-pause' else 'hour',a.hour,a.note)
        if changed: save(a.state,s)
        print(json.dumps({'changed':changed,'phase':s['phase'],'pause_count':s['pause_count'],'last_ack_hour':s['last_ack_hour']},ensure_ascii=False))
if __name__=='__main__': raise SystemExit(main())
