#!/usr/bin/env python3
"""Local phase evolution only: preserve states/history; schedule tree research."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil

A=Path(__file__).resolve().parents[1]
R=A.parents[1]
spec=importlib.util.spec_from_file_location('core',R/'src/research.py')
core=importlib.util.module_from_spec(spec); spec.loader.exec_module(core)


def main():
    store=core.Store(A)
    with store.lock():
        old_graph=copy.deepcopy(store.graph); old_state=store.load()
        assert not any(n['id']=='M14' for n in old_graph['nodes'])
        backup=A/'research/migrations/hour2-to-hour3'; assert not backup.exists(); backup.mkdir(parents=True)
        for name in ('graph.json','state.json','history.jsonl'):
            shutil.copy2(A/'research'/name,backup/name)
        graph=copy.deepcopy(old_graph)
        for item in graph['nodes']:
            if item['id']=='M13': item['artifact']='proof/KERNEL-SUMMARY-v1.md'
        additions=[
            {'id':'M14','layer':2,'title':'前缀兼容树的参数森林','role':'只处理明确树形/初值，不把左折叠当任意归约',
             'acceptance':'块不变量与右嵌套查询证明及限定的有限核验，模型成本显式',
             'artifact':'proof/PREFIX-FOREST-v1.md',
             'seed':{'current':.9,'remaining':.95,'novelty':1,'confidence':.75,'cost':1.2}},
            {'id':'E27','layer':3,'title':'森林块不变量与精确树证明','role':'形式结构证明，含初值真实叶子',
             'acceptance':'不假定结合律，明确B树及O(K log t)存储/时间界',
             'artifact':'proof/PREFIX-FOREST-v1.md',
             'seed':{'status':'blocked','current':.9,'remaining':.9,'novelty':1,'confidence':.8,'cost':1.1}},
            {'id':'E28','layer':3,'title':'树森林逐前缀反例/匹配实验','role':'实现与负控制，区分reference树/左折叠/padding',
             'acceptance':'字面B与forest逐前缀匹配、非结合负控制、峰值levels，实际退出日志',
             'artifact':'reports/prefix-forest-tests-v1.json',
             'seed':{'status':'blocked','current':.95,'remaining':.9,'novelty':1,'confidence':.9,'cost':.9}},
        ]
        graph['nodes'].extend(additions); graph['edges'].extend([['M14','D6'],['E27','M14'],['E28','M14']])
        graph['revision']=3; graph['planned_checkpoint']=3; core.validate_graph(graph)
        fresh=core.initial_state(graph); state=copy.deepcopy(old_state)
        for item in additions:
            key=item['id']; state['nodes'][key]=fresh['nodes'][key]; state['nodes'][key]['revision']=1
            state['nodes'][key]['note']='等待用户指定hour3唤醒；M14为新待证工具，不改T3证书'
        assert all(state['nodes'][key]==value for key,value in old_state['nodes'].items())
        state['graph_digest']=core.digest(graph)
        event=core.refresh_state(graph,state,'new-frontier:prefix-compatible-tree',
            {'added':['M14','E27','E28'],'descriptor_update':{'M13.artifact':'proposal-v0 → proved-v1'},
             'planned_next':'E28','scheduled_for_hour':3,'backup':str(backup)})
        try:
            core.atomic_json(store.graph_path,graph); store.graph=graph; store.save(state)
        except Exception:
            core.atomic_json(store.graph_path,old_graph); store.graph=old_graph; store.save(old_state); raise
        report={'passed':True,'before_nodes':len(old_graph['nodes']),'after_nodes':len(graph['nodes']),
                'old_node_parameters_preserved':all(state['nodes'][key]==value for key,value in old_state['nodes'].items()),
                'old_history_preserved':state['events'][:-1]==old_state['events'],
                'descriptor_only_change':['M13.artifact'],'event':event,'planned_next':'E28',
                'note':'原35节点与已认证T3不属于本次迁移；未证明的新树工具等待第3小时。'}
        core.atomic_json(A/'reports/hour3-frontier-migration.json',report)
        print(json.dumps({k:report[k] for k in ('passed','before_nodes','after_nodes','planned_next')},ensure_ascii=False))


if __name__=='__main__': main()
