#!/usr/bin/env python3
"""Explicit append-only local graph admission from a versioned JSON plan.

No installation/global registry changes; original namespaces are never opened.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil

A=Path(__file__).resolve().parents[1]
R=A.parents[1]
spec=importlib.util.spec_from_file_location('core',R/'src/research.py')
core=importlib.util.module_from_spec(spec); spec.loader.exec_module(core)


def admit(root,plan):
    root=Path(root).resolve()
    assert root not in {R.resolve(),(R/'alternatives/closed-llm').resolve()}, '禁止修改原研究命名空间'
    output=(root/plan['report']).resolve()
    assert output.is_relative_to(root/'reports') and (root/'reports').resolve().is_relative_to(root)
    store=core.Store(root)
    with store.lock():
        old_graph=copy.deepcopy(store.graph); old_state=store.load()
        old_ids={node['id'] for node in old_graph['nodes']}
        additions=plan['nodes']; ids=[node['id'] for node in additions]
        assert len(ids)==len(set(ids)) and not old_ids.intersection(ids)
        assert int(plan['revision'])>int(old_graph.get('revision',1))
        name=plan['backup_name']; assert Path(name).name==name
        backup=store.directory/'migrations'/name
        assert not backup.exists(); backup.mkdir(parents=True)
        for file in ('graph.json','state.json','history.jsonl'):
            shutil.copy2(store.directory/file,backup/file)
        graph=copy.deepcopy(old_graph)
        graph['nodes'].extend(additions); graph['edges'].extend(plan['edges'])
        graph['revision']=plan['revision']; graph['planned_checkpoint']=plan['hour']
        core.validate_graph(graph)
        fresh=core.initial_state(graph); state=copy.deepcopy(old_state)
        for node_id in ids:
            state['nodes'][node_id]=fresh['nodes'][node_id]
            state['nodes'][node_id]['revision']=1
            # Freshness age starts at admission, not at the session's round 0.
            state['nodes'][node_id]['last_work_round']=old_state['round']
            state['nodes'][node_id]['freshness_origin']='admission, no work claimed'
            state['nodes'][node_id]['note']=f"新候选入网，等待hour{plan['hour']}；并非已证明"
        assert all(state['nodes'][key]==value for key,value in old_state['nodes'].items())
        state['graph_digest']=core.digest(graph)
        event=core.refresh_state(graph,state,plan['reason'],{
            'added':ids,'planned_next':plan['planned_next'],'scheduled_for_hour':plan['hour'],
            'backup':str(backup),'freshness_age_initialized_at_admission':True})
        try:
            core.atomic_json(store.graph_path,graph); store.graph=graph; store.save(state)
        except Exception:
            core.atomic_json(store.graph_path,old_graph); store.graph=old_graph; store.save(old_state); raise
        report={'passed':True,'before_nodes':len(old_graph['nodes']),'after_nodes':len(graph['nodes']),
                'old_node_parameters_preserved':all(state['nodes'][key]==value for key,value in old_state['nodes'].items()),
                'old_descriptors_preserved':graph['nodes'][:len(old_graph['nodes'])]==old_graph['nodes'],
                'old_history_preserved':state['events'][:-1]==old_state['events'],
                'event':event,'planned_next':plan['planned_next'],'hour':plan['hour']}
        core.atomic_json(output,report)
        return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path)
    parser.add_argument('--root',type=Path,default=A)
    args=parser.parse_args(); result=admit(args.root,json.loads(args.plan.read_text()))
    print(json.dumps({k:result[k] for k in ('passed','before_nodes','after_nodes','planned_next')},ensure_ascii=False))
