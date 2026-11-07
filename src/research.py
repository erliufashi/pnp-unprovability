#!/usr/bin/env python3
"""PNP Research 0.1.0: stdlib-only, single-writer milestone scheduler.

The controller checks research bookkeeping, NOT mathematical correctness.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import uuid

VERSION = "0.1.0"
TERMINAL = {"done", "exhausted"}
STATUSES = {"open", "ready", "blocked", "done", "exhausted"}
FIELDS = ("current", "remaining", "novelty", "confidence", "cost")


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pnp-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(value):
    body = json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(body).hexdigest()


def validate_graph(graph):
    if graph.get("schema") != 1:
        raise ValueError("不支持的图谱schema")
    nodes = graph.get("nodes", [])
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("节点ID重复")
    lookup = {node["id"]: node for node in nodes}
    if {node.get("layer") for node in nodes} != {1, 2, 3}:
        raise ValueError("必须恰好有第1、2、3层")
    for node in nodes:
        for field in ("title", "role", "acceptance", "artifact"):
            if not node.get(field):
                raise ValueError(f"{node['id']} 缺少 {field}")
    edges = graph.get("edges", [])
    if len({tuple(edge) for edge in edges}) != len(edges):
        raise ValueError("依赖边重复")
    incident = {node_id: 0 for node_id in ids}
    for edge in edges:
        if len(edge) != 2 or any(item not in lookup for item in edge):
            raise ValueError("依赖边指向未知节点")
        source, target = edge
        if lookup[source]["layer"] - lookup[target]["layer"] != 1:
            raise ValueError("依赖只允许3→2或2→1；禁止同层、跨层和反向边")
        incident[source] += 1
        incident[target] += 1
    if any(count == 0 for count in incident.values()):
        raise ValueError("存在孤立节点")
    return lookup


def validate_state(graph, state):
    lookup = validate_graph(graph)
    if state.get("graph_digest") != digest(graph):
        raise ValueError("图谱版本变更，不能静默套用旧状态；请显式迁移")
    if set(state.get("nodes", {})) != set(lookup):
        raise ValueError("图谱与状态节点不一致")
    for node_id, item in state["nodes"].items():
        if item.get("status") not in STATUSES:
            raise ValueError(f"{node_id} 状态无效")
        for field in FIELDS:
            value = item.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{node_id}.{field} 必须为有限数字")
            if (field == "cost" and value <= 0) or (field != "cost" and not 0 <= value <= 1):
                raise ValueError(f"{node_id}.{field} 超出范围")
        if item["status"] == "exhausted" and item["remaining"] != 0:
            raise ValueError(f"{node_id} 耗尽时remaining必须为0")
        if item.get("stagnation", 0) < 0 or item.get("revision", 0) < 0:
            raise ValueError("停滞次数和revision不能为负")
    return lookup


def initial_state(graph):
    validate_graph(graph)
    nodes = {}
    for item in graph["nodes"]:
        seed = item.get("seed", {})
        nodes[item["id"]] = {
            "status": seed.get("status", "ready" if item["layer"] == 3 else "open"),
            "current": seed.get("current", 0.5),
            "remaining": seed.get("remaining", 0.7),
            "novelty": seed.get("novelty", 0.8),
            "confidence": seed.get("confidence", 0.7),
            "cost": seed.get("cost", 1.0),
            "last_work_round": 0, "stagnation": 0, "revision": 0,
            "seen_neighbors": {}, "evidence": [], "note": "尚未执行",
        }
    state = {"schema": 1, "controller_version": VERSION, "graph_digest": digest(graph),
             "round": 0, "selected": None, "nodes": nodes, "events": [],
             "mathematical_target": "UNRESOLVED", "created": stamp()}
    validate_state(graph, state)
    return state


def score_graph(graph, state):
    lookup = validate_state(graph, state)
    neighbors = {node_id: set() for node_id in lookup}
    parents = {node_id: set() for node_id in lookup}
    for source, target in graph["edges"]:
        neighbors[source].add(target)
        neighbors[target].add(source)
        parents[source].add(target)
    output = []
    for node_id, definition in lookup.items():
        item = state["nodes"][node_id]
        adjacent = sorted(neighbors[node_id])
        def raw(other, field):
            value = state["nodes"][other]
            return 0.0 if value["status"] in TERMINAL else value[field]
        local_current = raw(node_id, "current")
        local_remaining = raw(node_id, "remaining")
        neighbor_current = sum(raw(other, "current") for other in adjacent) / len(adjacent)
        neighbor_remaining = sum(raw(other, "remaining") for other in adjacent) / len(adjacent)
        effective_current = 0.8 * local_current + 0.2 * neighbor_current
        effective_remaining = 0.8 * local_remaining + 0.2 * neighbor_remaining
        changed = [other for other in adjacent if state["nodes"][other]["revision"] >
                   item["seen_neighbors"].get(other, 0)]
        signal = len(changed) / len(adjacent)
        age = min(max(state["round"] - item["last_work_round"], 0) / 6, 1)
        freshness = (0.65 * item["novelty"] * 2 ** (-item["stagnation"] / 3)
                     + 0.20 * age + 0.15 * signal)
        priority = item["confidence"] * (0.45 * effective_current +
                   0.35 * effective_remaining + 0.20 * freshness) / item["cost"]
        if item["status"] in TERMINAL:
            priority = 0.0
        live_parent = any(state["nodes"][other]["status"] not in TERMINAL for other in parents[node_id])
        eligible = (definition["layer"] == 3 and item["status"] == "ready" and
                    item["remaining"] > 0 and live_parent)
        output.append({"id": node_id, "title": definition["title"], "layer": definition["layer"],
                       "status": item["status"], "eligible": eligible,
                       "priority": round(priority, 8), "current": item["current"],
                       "remaining": item["remaining"], "freshness": round(freshness, 8),
                       "effective_current": round(effective_current, 8),
                       "effective_remaining": round(effective_remaining, 8),
                       "confidence": item["confidence"], "cost": item["cost"],
                       "changed_neighbors": changed, "neighbors": adjacent,
                       "artifact": definition["artifact"],
                       "reason": f"价值={effective_current:.3f} 余值={effective_remaining:.3f} "
                                 f"新鲜度={freshness:.3f} 可信度={item['confidence']:.3f} "
                                 f"成本={item['cost']:.2f} 邻接新信号={','.join(changed) or '无'}"})
    return sorted(output, key=lambda row: (-row["priority"], row["id"]))


def refresh_state(graph, state, reason, event=None):
    if not reason.strip():
        raise ValueError("刷新必须记录原因")
    previous = state["selected"]
    state["round"] += 1
    scores = score_graph(graph, state)
    candidates = [row for row in scores if row["eligible"]]
    state["selected"] = candidates[0]["id"] if candidates else None
    record = {"seq": len(state["events"]) + 1, "at": stamp(), "round": state["round"],
              "reason": reason, "previous": previous, "selected": state["selected"],
              "ranking": [{key: row[key] for key in ("id", "priority", "reason")}
                          for row in candidates], "details": event or {}}
    state["events"].append(record)
    return record


class Store:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.directory = self.root / "research"
        self.graph_path = self.directory / "graph.json"
        self.state_path = self.directory / "state.json"
        self.history_path = self.directory / "history.jsonl"
        self.graph = json.loads(self.graph_path.read_text(encoding="utf-8"))
        validate_graph(self.graph)

    def load(self):
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        validate_state(self.graph, state)
        return state

    def save(self, state):
        validate_state(self.graph, state)
        atomic_json(self.state_path, state)
        # state.events is authoritative. JSONL is an atomically replaced projection.
        lines = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in state["events"])
        fd, temporary = tempfile.mkstemp(prefix=".history-", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(lines)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.history_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def lock(self):
        stream = (self.directory / ".writer.lock").open("a", encoding="utf-8")
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return stream

    def evidence(self, name):
        path = (self.root / name).resolve()
        if not path.is_relative_to(self.root) or not path.is_file() or path.stat().st_size == 0:
            raise ValueError("证据必须是研究目录内非空文件")
        return {"path": str(path.relative_to(self.root)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def update(self, state, node_id, changes, note, evidence=None, worked=False, gain=False):
        if node_id not in state["nodes"]:
            raise ValueError(f"未知节点 {node_id}")
        if not note.strip():
            raise ValueError("参数调整必须写明依据")
        item = state["nodes"][node_id]
        if changes.get("status") in TERMINAL and not evidence:
            raise ValueError("完成/耗尽必须提供证据文件，不能只改状态")
        item.update(changes)
        if item["status"] == "exhausted":
            item["remaining"] = 0.0
        if evidence:
            item["evidence"].append(self.evidence(evidence))
        item["revision"] += 1
        item["note"] = note
        if worked:
            item["last_work_round"] = state["round"]
            item["stagnation"] = 0 if gain else item["stagnation"] + 1
            neighbors = next(row["neighbors"] for row in score_graph(self.graph, state) if row["id"] == node_id)
            item["seen_neighbors"] = {other: state["nodes"][other]["revision"] for other in neighbors}
        reason = ("exhausted:" if item["status"] == "exhausted" else "update:") + node_id
        record = refresh_state(self.graph, state, reason,
                               {"node": node_id, "changes": changes, "note": note,
                                "evidence": evidence, "worked": worked, "gain": gain})
        self.save(state)
        return record


def resolve_root(value):
    if value:
        return Path(value)
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config = config_home / "pnp-research" / "config.json"
    if not config.is_file():
        raise ValueError(f"缺少配置 {config}；用 --root 指定研究目录")
    return Path(json.loads(config.read_text(encoding="utf-8"))["root"])


def make_parser():
    parser = argparse.ArgumentParser(description="P/NP不可证性三层研究网络；调度通过不等于数学证明通过")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--root", help="研究目录（默认读取XDG配置）")
    parser.add_argument("--json", action="store_true", help="仅输出机器JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    for command, help_text in [("init", "初始化一次"), ("check", "校验图谱、状态、证据及日志"),
                               ("status", "查看三层节点"), ("next", "查看当前推荐目标"),
                               ("refresh", "重算并记录一轮"), ("update", "根据证据调整节点"),
                               ("history", "读取选择历史"), ("snapshot", "保存研究状态快照"),
                               ("restore", "恢复快照中的节点参数，保留审计历史"),
                               ("paths", "发现入口与数据位置")]:
        child = sub.add_parser(command, help=help_text)
        child.add_argument("--root", default=argparse.SUPPRESS)
        child.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
        if command in {"refresh", "restore"}:
            child.add_argument("--reason", required=True)
        if command == "update":
            child.add_argument("id")
            for field in FIELDS:
                child.add_argument("--" + field, type=float)
            child.add_argument("--status", choices=sorted(STATUSES))
            child.add_argument("--note", required=True)
            child.add_argument("--evidence")
            child.add_argument("--worked", action="store_true")
            child.add_argument("--gain", action="store_true")
        if command == "restore":
            child.add_argument("snapshot", help="snapshot返回的文件名，不接受任意路径")
    return parser


def run(args):
    root = resolve_root(args.root)
    if args.command == "paths":
        return {"root": str(root.resolve()), "controller": str(Path(__file__).resolve()),
                "graph": str(root / "research/graph.json"),
                "state": str(root / "research/state.json"),
                "resume": str(root / "docs/RESUME.md"), "version": VERSION}
    store = Store(root)
    if args.command == "init":
        with store.lock():
            if store.state_path.exists():
                raise ValueError("状态已存在；禁止覆盖初始化")
            state = initial_state(store.graph)
            record = refresh_state(store.graph, state, "initialization")
            store.save(state)
            return record
    mutating = args.command in {"refresh", "update", "snapshot", "restore"}
    lock = store.lock() if mutating else None
    try:
        state = store.load()
        if args.command == "check":
            exported = [json.loads(line) for line in store.history_path.read_text().splitlines() if line]
            if exported != state["events"]:
                raise ValueError("日志投影与权威状态不一致；refresh可从state.events修复")
            for node in state["nodes"].values():
                for evidence in node["evidence"]:
                    actual = store.evidence(evidence["path"])
                    if actual["sha256"] != evidence["sha256"]:
                        raise ValueError(f"证据已改写：{evidence['path']}；保留旧版证据后显式更新")
            return {"valid": True, "layers": 3, "nodes": len(state["nodes"]),
                    "edges": len(store.graph["edges"]), "round": state["round"],
                    "mathematical_target": state["mathematical_target"],
                    "warning": "只校验调度与证据完整性，不校验数学定理"}
        if args.command == "status":
            return {"round": state["round"], "selected": state["selected"],
                    "mathematical_target": state["mathematical_target"],
                    "nodes": score_graph(store.graph, state)}
        if args.command == "next":
            rows = score_graph(store.graph, state)
            return {"round": state["round"], "selected": state["selected"],
                    "node": next((row for row in rows if row["id"] == state["selected"]), None),
                    "mathematical_target": state["mathematical_target"]}
        if args.command == "history":
            return {"events": state["events"]}
        if args.command == "refresh":
            record = refresh_state(store.graph, state, args.reason)
            store.save(state)
            return record
        if args.command == "update":
            if args.gain and not args.worked:
                raise ValueError("--gain需要--worked")
            changes = {field: getattr(args, field) for field in FIELDS + ("status",)
                       if getattr(args, field) is not None}
            return store.update(state, args.id, changes, args.note,
                                args.evidence, args.worked, args.gain)
        if args.command == "snapshot":
            name = f"round-{state['round']:05d}-{uuid.uuid4().hex[:8]}.json"
            atomic_json(store.directory / "snapshots" / name, state)
            return {"snapshot": name, "round": state["round"], "sha256": digest(state)}
        if args.command == "restore":
            if Path(args.snapshot).name != args.snapshot:
                raise ValueError("只接受快照文件名")
            saved = json.loads((store.directory / "snapshots" / args.snapshot).read_text())
            validate_state(store.graph, saved)
            state["nodes"] = copy.deepcopy(saved["nodes"])
            record = refresh_state(store.graph, state, "restore:" + args.reason,
                                   {"snapshot": args.snapshot, "restored_from_round": saved["round"]})
            store.save(state)
            return record
    finally:
        if lock:
            lock.close()
    raise ValueError("未知操作")


def main():
    parser = make_parser()
    args = parser.parse_args()
    try:
        result = run(args)
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"错误：{exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    elif args.command == "status":
        print(f"第 {result['round']} 轮；数学目标：{result['mathematical_target']}；当前：{result['selected']}")
        for layer in (1, 2, 3):
            print(f"\n第{layer}层")
            for row in result["nodes"]:
                if row["layer"] == layer:
                    print(f"  {row['id']:5} {row['status']:9} {row['priority']:.4f} {row['title']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
