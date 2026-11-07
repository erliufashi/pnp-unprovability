#!/usr/bin/env python3
"""Explicit local graph evolution, preserving prior nodes and original namespaces."""
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
        assert not any(node['id']=='M13' for node in old_graph['nodes']), '已演进，不重复覆盖'
        backup=A/'research/migrations/hour1-to-hour2'
        assert not backup.exists()
        backup.mkdir(parents=True)
        for name in ('graph.json','state.json','history.jsonl'):
            shutil.copy2(A/'research'/name,backup/name)
        graph=copy.deepcopy(old_graph)
        additions=[
            {'id':'M13','layer':2,'title':'有限query/归一化历史摘要','role':'新的append-only状态压缩工具，非行缓冲调度',
             'acceptance':'给出左折叠摘要归纳证明或反例，明确模型规模成本及未覆盖情况',
             'artifact':'notes/ALL-QUERY-CANDIDATE-v0.md',
             'seed':{'current':.95,'remaining':.95,'novelty':1,'confidence':.7,'cost':1.4}},
            {'id':'E25','layer':3,'title':'小有限域逐前缀摘要核验','role':'先找反例与检查counterfactual错误处理',
             'acceptance':'字面完整历史与摘要在每个小前缀/每个query匹配或给最小反例；不是float32全域穷举',
             'artifact':'reports/tiny-domain-tests-v1.json',
             'seed':{'status':'blocked','current':.95,'remaining':.9,'novelty':1,'confidence':.85,'cost':.9}},
            {'id':'E26','layer':3,'title':'左折叠有限摘要的形式归纳','role':'分析证明与模型规模成本，独立于有限实验',
             'acceptance':'给明确有限域/纯映射/append-only前提、精确等式及边界；未证部分明确',
             'artifact':'proof/KERNEL-SUMMARY-v1.md',
             'seed':{'status':'blocked','current':.9,'remaining':.95,'novelty':1,'confidence':.75,'cost':1.4}},
        ]
        graph['nodes'].extend(additions)
        graph['edges'].extend([['M13','D6'],['E25','M13'],['E26','M13']])
        graph['revision']=2
        graph['planned_checkpoint']=2
        core.validate_graph(graph)
        fresh=core.initial_state(graph)
        state=copy.deepcopy(old_state)
        for item in additions:
            node_id=item['id']; state['nodes'][node_id]=fresh['nodes'][node_id]
            state['nodes'][node_id]['revision']=1
            state['nodes'][node_id]['note']='hour1新候选入网；步骤等待用户指定第2小时唤醒，不视为已证明'
        assert all(state['nodes'][key]==value for key,value in old_state['nodes'].items())
        state['graph_digest']=core.digest(graph)
        event=core.refresh_state(graph,state,'new-frontier:finite-query-summary',
                                 {'added':['M13','E25','E26'],'planned_next':'E25',
                                  'scheduled_for_hour':2,'backup':str(backup)})
        try:
            core.atomic_json(store.graph_path,graph); store.graph=graph; store.save(state)
        except Exception:
            core.atomic_json(store.graph_path,old_graph); store.graph=old_graph; store.save(old_state)
            raise
        report={'passed':True,'old_nodes_parameters_preserved':all(state['nodes'][key]==value for key,value in old_state['nodes'].items()),
                'old_history_preserved':state['events'][:-1]==old_state['events'],
                'before_nodes':len(old_graph['nodes']),'after_nodes':len(graph['nodes']),
                'before_digest':core.digest(old_graph),'after_digest':core.digest(graph),
                'event':event,'scheduled_target':'E25','note':'只演进新研究命名空间，不修改旧35节点或T3证书；新候选未认证。'}
        core.atomic_json(A/'reports/hour2-frontier-migration.json',report)
        print(json.dumps({k:report[k] for k in ('passed','before_nodes','after_nodes','scheduled_target')},ensure_ascii=False))


if __name__=='__main__':
    main()
