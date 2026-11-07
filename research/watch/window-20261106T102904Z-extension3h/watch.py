#!/usr/bin/env python3
"""Three-hour authorized extension window; starts exactly at prior deadline."""
import argparse,fcntl,json,os,tempfile,time
from pathlib import Path

def validate(s):
    assert s['deadline_epoch']-s['start_epoch']==s['duration_seconds']==10800
    assert s['interval_seconds']==3600 and s['max_checkpoint']==2
    assert s['phase'] in ('running','paused') and s['pause_count'] in (0,1)
    assert (s['phase']=='paused')==(s['pause_count']==1)

def event(s,now,kind):
    validate(s)
    if s['phase']=='paused': return None
    if kind=='deadline':
        if now<s['deadline_epoch']: return None
        return {'event':'PAUSE_ONCE','window':s['window_id'],'event_id':s['window_id']+':deadline','deadline':s['deadline_local'],'state_path':s['state_path'],'instruction':'追加3小时窗口已截止：先核state/clock，停止新研究，ack-pause一次，随后只停扩展自有monitor并行政验收，不自动续期。'}
    if now<s['start_epoch'] or now>=s['deadline_epoch']: return None
    hour=int((now-s['start_epoch'])//s['interval_seconds'])
    if hour<1 or hour>s['max_checkpoint'] or hour<=s['last_ack_hour']: return None
    return {'event':'RESEARCH_CHECKPOINT','window':s['window_id'],'event_id':s['window_id']+':hour:'+str(hour),'hour':hour,'deadline':s['deadline_local'],'state_path':s['state_path'],'instruction':'追加3小时研究检查：先核state/clock，推进一个真实节点批次或记录具体阻塞后ack-hour；五位研究员同权，旧证明/历史不改标。'}

def ack(s,now,kind,hour,note):
    validate(s)
    if not note.strip(): raise ValueError('note required')
    if kind=='pause':
        if now<s['deadline_epoch']: raise ValueError('before extension deadline')
        if s['pause_count']: return False
        s.update(phase='paused',pause_count=1,paused_at_epoch=now); s['log'].append({'action':'paused_once','at':now,'note':note}); return True
    if now<s['start_epoch'] or now>=s['deadline_epoch'] or s['phase']=='paused': raise ValueError('checkpoint outside extension')
    if hour<0 or hour>s['max_checkpoint'] or now<s['start_epoch']+hour*s['interval_seconds']: raise ValueError('invalid hour')
    if hour<=s['last_ack_hour']: return False
    s['last_ack_hour']=hour; s['log'].append({'action':'checkpoint','hour':hour,'at':now,'note':note}); return True

def save(path,s):
    fd,tmp=tempfile.mkstemp(prefix='.state-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(s,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
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
