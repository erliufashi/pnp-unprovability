#!/usr/bin/env python3
"""一次性、可审计图谱演进：把新反例增长桥E12接入M7；不移动目录。"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("research_controller", PROJECT/"src/research.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def migrate(root):
    store = r.Store(root)
    with store.lock():
        old = store.load()
        old_graph = copy.deepcopy(store.graph)
        if ["E12", "M7"] in old_graph["edges"]:
            raise ValueError("v2边已存在，拒绝重复迁移")
        backup = store.directory/"migrations/001-before-v2"
        if backup.exists():
            raise ValueError("备份已存在，拒绝覆盖；先查阅上次迁移结果")
        backup.mkdir(parents=True)
        for name in ("graph.json", "state.json", "history.jsonl"):
            shutil.copy2(store.directory/name, backup/name)
        graph = copy.deepcopy(old_graph)
        graph["edges"].append(["E12", "M7"])
        graph["graph_revision"] = 2
        r.validate_graph(graph)
        state = copy.deepcopy(old)
        state["graph_digest"] = r.digest(graph)
        assert state["nodes"] == old["nodes"]
        event = r.refresh_state(graph, state, "graph-migration:v2-growth-bridge", {
            "added_edge": ["E12", "M7"], "old_digest": r.digest(old_graph),
            "new_digest": r.digest(graph), "backup": str(backup)})
        try:
            r.atomic_json(store.graph_path, graph)
            store.graph = graph
            store.save(state)
        except Exception:
            r.atomic_json(store.graph_path, old_graph)
            store.graph = old_graph
            store.save(old)
            raise
        report = {"passed": True, "kind": "graph-schema-preserving-evolution-not-path-migration",
                  "reason": "E12新增长桥实际支持M7；显式加入相邻依赖而非反向逻辑环",
                  "before_nodes": len(old["nodes"]), "after_nodes": len(state["nodes"]),
                  "before_edges": len(old_graph["edges"]), "after_edges": len(graph["edges"]),
                  "node_parameters_preserved": state["nodes"] == old["nodes"],
                  "audit_events_preserved": state["events"][:-1] == old["events"],
                  "math_target_preserved": state["mathematical_target"] == old["mathematical_target"],
                  "event": event, "backup": str(backup),
                  "recovery": "停止writer；保留故障三文件；从backup复制graph/state/history整套恢复，再check及refresh记录恢复。旧snapshot只兼容旧graph。"}
        r.atomic_json(store.root/"reports/graph-migration-v2.json", report)
        return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT)
    args = parser.parse_args()
    result = migrate(args.root)
    print(json.dumps({key: result[key] for key in ("passed", "before_edges", "after_edges", "node_parameters_preserved", "audit_events_preserved")}, ensure_ascii=False))
