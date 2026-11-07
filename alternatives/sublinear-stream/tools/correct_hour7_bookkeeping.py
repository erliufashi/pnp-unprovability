#!/usr/bin/env python3
"""One-shot audited evidence-version/timestamp repair; never deletes events."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil

A=Path(__file__).resolve().parents[1]; R=A.parents[1]
spec=importlib.util.spec_from_file_location('core',R/'src/research.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
store=c.Store(A)
with store.lock():
    state=store.load(); assert state['round']==73
    events={event['round']:event for event in state['events']}
    for first,second in zip(range(64,69),range(69,74)):
        assert events[first]['details']['node']==events[second]['details']['node']
        assert events[first]['details']['changes']==events[second]['details']['changes']
    backup=A/'research/corrections/hour7-bookkeeping-before'; assert not backup.exists(); backup.mkdir(parents=True)
    for path in [store.state_path,store.history_path,store.graph_path,A/'proof/PRUNING-COST-v1.md']:
        shutil.copy2(path,backup/path.name)
    before_state_sha=hashlib.sha256(store.state_path.read_bytes()).hexdigest()
    v1=A/'proof/PRUNING-COST-v1.md'; v2=A/'proof/PRUNING-COST-v2.md'; assert not v2.exists()
    new=v1.read_text()
    old=new.replace('两个profile证书的各自JSON序列化大小约25146/25503 bytes（以本次实际report为准），包含闭包证明及分类信息；它们合存于报告引用的证书artifact。这不是Python对象驻留，也不是最小runtime metadata。',
                    '两个证书JSON artifact分别约25146/25503 bytes（以本次实际report为准），包含闭包证明及分类信息；这是序列化artifact大小，不是Python对象驻留，也不是最小runtime metadata。')
    old_sha=hashlib.sha256(old.encode()).hexdigest(); new_sha=hashlib.sha256(new.encode()).hexdigest()
    assert old_sha=='676d011c56b76545baf8c531241896949c3f0f34a2d9e6bf35faed3d7cb0f8b7'
    assert new_sha=='e2233caa66365bfb37188d968ef6f405fd722352ee68382a7e93ff001d5d97de'
    v2.write_text(new); v1.write_text(old)
    redirected=0
    for item in state['nodes']['E40']['evidence']:
        if item['path']=='proof/PRUNING-COST-v1.md' and item['sha256']==new_sha:
            item['path']='proof/PRUNING-COST-v2.md'; redirected+=1
    assert redirected==1
    restored={}
    for node,first in [('E39',64),('M18',66),('D6',67)]:
        item=state['nodes'][node]; restored[node]={'before':item['last_work_round'],'after':first-1}
        item['last_work_round']=first-1; item['revision']+=1
    # Round70 was an actual editorial clarification, not another theorem gain.
    state['nodes']['E40']['stagnation']=1; state['nodes']['E40']['revision']+=1
    corrections={'administrative_only_rounds':[69,71,72],
                 'editorial_not_new_theorem_round':70,
                 'genuine_new_candidate_round':73,
                 'raw_events_retained':True,'last_work_round_restored':restored,
                 'versioned_alias':{'original_event':70,'old_recorded_path':'proof/PRUNING-COST-v1.md',
                                    'sha256':new_sha,'current_path':'proof/PRUNING-COST-v2.md'},
                 'reason':'重复管理记录不算新科学进展；已被引用的v1恢复原字节，澄清版另存v2；没有删除原始事件或实验。'}
    event=c.refresh_state(store.graph,state,'correction:hour7-bookkeeping',corrections)
    assert event['selected'] is None
    store.save(state)
    for item in state['nodes'].values():
        for evidence in item['evidence']:
            assert hashlib.sha256((A/evidence['path']).read_bytes()).hexdigest()==evidence['sha256']
    result={'passed':True,'scope':'new local branch only, not original35/T3',**corrections,
            'backup':str(backup),'before_state_sha256':before_state_sha,
            'after_state_sha256':hashlib.sha256(store.state_path.read_bytes()).hexdigest(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'rollback':'备份用于审计/人工恢复；不得直接覆盖以抹掉后续历史。逆向调整须新建correction事件并保留两份证据。'}
    c.atomic_json(A/'reports/hour7-bookkeeping-correction.json',result)
    p=A/'reports/hour7-summary.json'; summary=json.loads(p.read_text()); summary['proofs'][1]='proof/PRUNING-COST-v2.md'
    summary['bookkeeping_correction']='reports/hour7-bookkeeping-correction.json'; c.atomic_json(p,summary)
    print(json.dumps({'passed':True,'round':event['round'],'versioned_v1_restored':True,'v2_preserved':True,'administrative_rounds_not_scientific_gain':[69,71,72]},ensure_ascii=False))
