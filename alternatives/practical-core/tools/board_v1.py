#!/usr/bin/env python3
"""Shared research board v1: all authorized researchers may add/adjust nodes.

Authoritative graph+state+leases are one atomic snapshot. Legacy files are
recoverable projections. Every client operation is serialized by fcntl; node
artifact leases do NOT require commander approval for new nodes/parameters.
"""
import argparse,copy,fcntl,hashlib,importlib.util,json,os,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('legacy_core',PROJECT/'src/research.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
base_score=c.score_graph


def scored(graph,state):
    rows=base_score(graph,state); lookup={n['id']:n for n in graph['nodes']}
    parents={n:set() for n in lookup}
    for a,b in graph['edges']: parents[a].add(b)
    for row in rows:
        frontier={row['id']}; directions=set()
        while frontier:
            x=frontier.pop()
            if lookup[x]['layer']==1: directions.add(x)
            else: frontier.update(parents[x])
        weight=max((lookup[d].get('reward_multiplier',.25) for d in directions),default=.25)
        row['priority_raw']=row['priority']; row['reward_multiplier']=weight
        row['priority']=round(row['priority']*weight,10)
    return sorted(rows,key=lambda x:(-x['priority'],x['id']))
c.score_graph=scored


def store(graph):
    obj=object.__new__(c.Store); obj.root=ROOT; obj.directory=ROOT/'research'; obj.graph=graph
    obj.graph_path=obj.directory/'graph.json'; obj.state_path=obj.directory/'state.json'; obj.history_path=obj.directory/'history.jsonl'
    obj.save=lambda state: None
    return obj


def projection(board):
    c.validate_state(board['graph'],board['state'])
    c.atomic_json(ROOT/'research/graph.json',board['graph'])
    c.Store.save(store(board['graph']),board['state'])


def execute(a):
    path=ROOT/'research/shared-board.json'; config=json.loads((ROOT/'research/config.json').read_text())
    if a.actor not in config['actors']: raise ValueError('unknown actor')
    with (ROOT/'research/.writer.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)  # tiny transactions only, never held during research
        board=json.loads(path.read_text()); graph=board['graph']; state=board['state']; now=time.time()
        c.validate_state(graph,state)
        mutation=a.command not in ('status','next','show','check')
        if mutation:
            if a.actor not in config['research_writers']: raise ValueError('advisor proposes via mail; three researchers and chief have board rights')
            if not a.op: raise ValueError('mutations require a stable --op id for idempotency')
            request=vars(a).copy(); request.pop('op',None)
            if a.spec: request['spec_sha256']=hashlib.sha256(Path(a.spec).read_bytes()).hexdigest()
            if a.file: request['file_sha256']=hashlib.sha256(Path(a.file).read_bytes()).hexdigest()
            fingerprint=c.digest(request)
            if a.op in board['operations']:
                old=board['operations'][a.op]
                if old['fingerprint']!=fingerprint: raise ValueError('op id reused with different payload')
                return {**old['result'],'reused':True}
            window=json.loads(Path(config['window_state']).read_text())
            if a.command!='release' and (window['phase']!='running' or now>=window['deadline_epoch']):
                raise ValueError('window ended: no new research mutation')
        leases=board['leases']
        rows=scored(graph,state)
        available=[r for r in rows if r['eligible'] and (r['id'] not in leases or leases[r['id']]['expires']<=now or leases[r['id']]['actor']==a.actor)]
        if a.command=='status': return {'ok':True,'round':state['round'],'nodes':len(graph['nodes']),'edges':len(graph['edges']),'ranking':rows,'leases':leases,'mathematical_target':state['mathematical_target']}
        if a.command=='next': return {'ok':True,'selected':available[0] if available else None,'alternatives':available[1:6],'leases':leases}
        if a.command=='show':
            return {'ok':True,'definition':next(n for n in graph['nodes'] if n['id']==a.node),'state':state['nodes'][a.node],'lease':leases.get(a.node)}
        if a.command=='check':
            for item in state['nodes'].values():
                for e in item['evidence']:
                    if hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()!=e['sha256']: raise ValueError('evidence hash mismatch')
            projection(board)
            return {'ok':True,'nodes':len(graph['nodes']),'edges':len(graph['edges']),'round':state['round'],'authoritative':'shared-board.json'}
        if not a.note.strip(): raise ValueError('mutation needs a factual --note')
        event=None
        if a.command=='claim':
            node=a.node or (available[0]['id'] if available else None)
            if not node: raise ValueError('no available node; add a concrete new node or report blocker')
            if node not in state['nodes']: raise ValueError('unknown node')
            old=leases.get(node)
            if old and old['expires']>now and old['actor']!=a.actor: raise ValueError('node owned; choose another or coordinate by mail')
            leases[node]={'actor':a.actor,'expires':min(now+a.ttl,config['deadline_epoch']),'token':str(uuid.uuid4())}
            result={'ok':True,'node':node,'lease':leases[node]}
        elif a.command=='release':
            old=leases.get(a.node)
            if old and old['actor']!=a.actor and a.actor!='pnp-chief': raise ValueError('cannot release another owner without chief arbitration')
            leases.pop(a.node,None); result={'ok':True,'released':a.node}
        elif a.command=='add':
            payload=json.loads(Path(a.spec).read_text()); additions=payload['nodes']; edges=payload['edges']
            existing=set(state['nodes'])
            if existing.intersection(n['id'] for n in additions): raise ValueError('node id exists; use actor-qualified new ids')
            graph['nodes'].extend(additions); graph['edges'].extend(edges); c.validate_graph(graph)
            fresh=c.initial_state(graph)
            for n in additions:
                item=fresh['nodes'][n['id']]; item['last_work_round']=state['round']; item['note']=a.note
                state['nodes'][n['id']]=item
            state['graph_digest']=c.digest(graph)
            event=c.refresh_state(graph,state,'add:'+a.actor,{'actor':a.actor,'nodes':[n['id'] for n in additions],'note':a.note,'op':a.op})
            result={'ok':True,'added':[n['id'] for n in additions],'round':event['round'],'selected':event['selected']}
        elif a.command in ('update','publish'):
            item=state['nodes'][a.node]
            if a.expect_revision is not None and item['revision']!=a.expect_revision: raise ValueError('stale revision: show node and reconsider')
            changes={f:getattr(a,f) for f in c.FIELDS if getattr(a,f) is not None}
            if a.status: changes['status']=a.status
            evidence=None
            if a.command=='publish':
                lease=leases.get(a.node)
                if not lease or lease['actor']!=a.actor or lease['expires']<=now: raise ValueError('valid own node lease required to publish')
                source=Path(a.file).resolve(); workspace=Path(config['actors'][a.actor]['cwd']).resolve()
                if not source.is_relative_to(workspace) or not source.is_file(): raise ValueError('publish only own workspace artifact')
                data=source.read_bytes()
                if not data: raise ValueError('empty artifact')
                sha=hashlib.sha256(data).hexdigest(); dest=ROOT/'evidence'/a.node/(sha+source.suffix)
                dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():
                    if dest.read_bytes()!=data: raise ValueError('immutable artifact collision')
                else:
                    with dest.open('xb') as out: out.write(data); out.flush(); os.fsync(out.fileno())
                evidence=str(dest.relative_to(ROOT))
                item['result_classification']=a.classification
            elif a.evidence:
                evidence=a.evidence
            if changes.get('status') in c.TERMINAL: changes['remaining']=0
            event=c.Store.update(store(graph),state,a.node,changes,a.note,evidence,a.worked,a.gain)
            event['details']['actor']=a.actor; event['details']['op']=a.op
            if changes.get('status') in c.TERMINAL: leases.pop(a.node,None)
            result={'ok':True,'node':a.node,'revision':item['revision'],'round':event['round'],'selected':event['selected'],'evidence':evidence}
        elif a.command=='refresh':
            event=c.refresh_state(graph,state,'refresh:'+a.actor,{'actor':a.actor,'note':a.note,'op':a.op})
            result={'ok':True,'round':event['round'],'selected':event['selected']}
        else: raise ValueError('unknown command')
        board['operations'][a.op]={'fingerprint':fingerprint,'result':result}
        board['coordination_log'].append({'at':now,'actor':a.actor,'command':a.command,'op':a.op,'note':a.note})
        c.validate_state(graph,state)
        c.atomic_json(path,board)  # commit first; projections are recoverable
        projection(board)
        return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['status','next','show','check','claim','release','add','update','publish','refresh'])
    p.add_argument('--actor',default='pnp-chief'); p.add_argument('--node'); p.add_argument('--op'); p.add_argument('--note',default='')
    p.add_argument('--spec'); p.add_argument('--file'); p.add_argument('--evidence'); p.add_argument('--ttl',type=int,default=5400)
    p.add_argument('--expect-revision',type=int); p.add_argument('--status',choices=sorted(c.STATUSES))
    for name in c.FIELDS: p.add_argument('--'+name,type=float)
    p.add_argument('--worked',action='store_true'); p.add_argument('--gain',action='store_true')
    p.add_argument('--classification',choices=['hypothesis','conditional','proved-candidate','counterexample','blocked'],default='conditional')
    try: result=execute(p.parse_args()); print(json.dumps(result,ensure_ascii=False)); return 0
    except Exception as error: print(json.dumps({'ok':False,'error':str(error)},ensure_ascii=False)); return 2
if __name__=='__main__': raise SystemExit(main())
