#!/usr/bin/env python3
"""PNP Research hub 0.3.0. Legacy engine and legacy state remain unchanged."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

VERSION = "0.3.0"
spec = importlib.util.spec_from_file_location("pnp_legacy", Path(__file__).with_name("research.py"))
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def legacy_fingerprint(root):
    return {name: sha(Path(root)/"research"/name) for name in ("graph.json", "state.json", "history.jsonl")}


def registry(root):
    value = json.loads((Path(root)/"research/termination.json").read_text())
    terms = value["terminals"]
    if terms["T1"]["weight"] != 1 or terms["T2"]["weight"] != 1 or not 0 < terms["T3"]["weight"] < 1:
        raise ValueError("T1/T2权重必须为1，T3必须严格介于0和1")
    if value["branches"]["main"]["weight"] != 1 or value["branches"]["closed-llm"]["weight"] != terms["T3"]["weight"]:
        raise ValueError("分支和终止项权重不一致")
    return value


def registry_v2(root):
    path = Path(root)/"research/termination-v2.json"
    if not path.is_file():
        return None
    value = json.loads(path.read_text())
    terms = value["terminals"]
    if terms["T1"]["weight"] != 1 or terms["T2"]["weight"] != 1:
        raise ValueError("v2中T1/T2权重必须为1")
    if not (0 < terms["T3_v2"]["weight"] < 1 and 0 < value["branches"]["practical-core"]["weight"] < 1):
        raise ValueError("v2中T3_v2与practical-core权重必须严格介于0和1")
    return value


def branch_root(root, name, reg=None):
    root = Path(root).resolve()
    data = (reg or registry(root))["branches"][name]
    destination = (root/data["path"]).resolve()
    if name == "main":
        if destination != root:
            raise ValueError("旧分支root不能改写")
    elif not destination.is_relative_to(root/"alternatives") or destination == root:
        raise ValueError("新分支必须在独立alternatives目录")
    return destination


def priorities(root):
    reg = registry(root)
    rows = []
    for name, definition in reg["branches"].items():
        store = core.Store(branch_root(root, name, reg))
        state = store.load()
        for row in core.score_graph(store.graph, state):
            rows.append({**row, "branch": name, "raw_priority": row["priority"],
                         "weight": definition["weight"],
                         "weighted_priority": row["priority"] * definition["weight"],
                         "local_round": state["round"]})
    v2 = registry_v2(root)
    if v2 and "practical-core" in v2["branches"]:
        p_def = v2["branches"]["practical-core"]
        p_root = branch_root(root, "practical-core", v2)
        if (p_root/"research/graph.json").is_file() and (p_root/"research/state.json").is_file():
            store = core.Store(p_root)
            state = store.load()
            for row in core.score_graph(store.graph, state):
                rows.append({**row, "branch": "practical-core", "raw_priority": row["priority"],
                             "weight": p_def["weight"],
                             "weighted_priority": row["priority"] * p_def["weight"],
                             "local_round": state["round"]})
    rows.sort(key=lambda row: (-row["weighted_priority"], row["branch"], row["id"]))
    candidates = [row for row in rows if row["eligible"]]
    weights = {key: value["weight"] for key, value in reg["terminals"].items()}
    if v2:
        weights["T3_v2"] = v2["terminals"]["T3_v2"]["weight"]
    return {"nodes": rows, "selected": ({"branch": candidates[0]["branch"], "id": candidates[0]["id"]}
                                          if candidates else None),
            "weights": weights,
            "note": "T1/T2共享旧研究图谱，不重复叠加收益；新分支不传播参数给旧节点"}


def certificate_valid(terminal):
    cert = terminal.get("certificate")
    if terminal["status"] not in {"proved", "proved_conditional_proxy"} or not cert:
        return False
    path = Path(cert["path"])
    if not path.name.endswith(".receipt.json") or sha(path) != cert["sha256"]:
        raise ValueError("正式回执路径或SHA256不一致")
    receipt = json.loads(path.read_text())
    if receipt.get("goal_id") != terminal["required_goal"] or receipt.get("verdict") != "pass":
        raise ValueError("回执goal或verdict不匹配")
    if not terminal.get("conditions"):
        raise ValueError("停止条件缺少适用范围")
    return True


def mission_status(root):
    reg = registry(root)
    verified = {name: certificate_valid(item) for name, item in reg["terminals"].items()}
    met = [name for name, passed in verified.items() if passed]
    out = {"stop": bool(met), "met": met, "terminals": reg["terminals"],
           "verified": verified, "standard_targets_unresolved": not (verified["T1"] or verified["T2"]),
           "stop_scope": ("qualified_closed_LLM_proxy" if met == ["T3"] else "standard_target" if met else None),
           "human_equivalence_empirically_verified": False,
           "no_background_proof_job": True}
    v2 = registry_v2(root)
    if v2:
        t3_v2 = v2["terminals"]["T3_v2"]
        current_met = [k for k in ("T1", "T2") if verified.get(k)]
        if t3_v2.get("status") == "proved":
            current_met.append("T3_v2")
        branches_v2 = {}
        for bname, bdef in v2.get("branches", {}).items():
            broot = branch_root(root, bname, v2)
            entry = dict(bdef)
            if (broot/"research/graph.json").is_file() and (broot/"research/state.json").is_file():
                bstore = core.Store(broot)
                bstate = bstore.load()
                entry.update({"nodes": len(bstore.graph["nodes"]), "edges": len(bstore.graph["edges"]), "round": bstate["round"]})
            branches_v2[bname] = entry
        out.update({
            "current_contract_version": 2,
            "phase": v2.get("phase", "active"),
            "current_goal_stop": bool(current_met),
            "current_goal_met": current_met,
            "t3_v1_historical_only": True,
            "t3_v2": t3_v2,
            "branches_v2": branches_v2,
            "weights_v2": {k: val["weight"] for k, val in v2["terminals"].items()},
            "status_summary_zh": "T1/T2与T3-v2当前均未解决（UNRESOLVED）；早期T3-v1仅保留封闭单遍有限代理历史效力，不构成现实能力覆盖。"
        })
    return out


def preservation(root, save=False):
    root = Path(root)
    path = root/"reports/extension-preservation.json"
    baseline = json.loads(path.read_text())
    current = {name: sha(root/name) for name in baseline["baseline"]}
    store = core.Store(root)
    scores = core.score_graph(store.graph, store.load())
    result = {"files_unchanged": current == baseline["baseline"],
              "scores_unchanged": scores == baseline["baseline_scores"],
              "changed": [key for key, value in current.items() if value != baseline["baseline"][key]]}
    result["passed"] = result["files_unchanged"] and result["scores_unchanged"]
    if save:
        baseline["readback"] = result
        baseline["passed"] = result["passed"]
        core.atomic_json(path, baseline)
    return result


def refresh_mission(root, reason):
    root = Path(root)
    before = legacy_fingerprint(root)
    reg = registry(root)
    lock = (root/"research/.mission.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        store = core.Store(branch_root(root, "closed-llm", reg))
        with store.lock():
            state = store.load()
            event = core.refresh_state(store.graph, state, reason)
            store.save(state)
        choice = priorities(root)["selected"]
        path = root/"research/mission-state.json"
        mission = json.loads(path.read_text()) if path.exists() else {"schema": 1, "events": []}
        record = {"seq": len(mission["events"])+1, "at": core.stamp(), "reason": reason,
                  "selected": choice, "alt_local_round": event["round"],
                  "legacy_unchanged": before == legacy_fingerprint(root)}
        if not record["legacy_unchanged"]:
            raise ValueError("旧分支在扩展刷新中发生变更；停止并检查writer")
        mission["events"].append(record)
        core.atomic_json(path, mission)
        return record
    finally:
        lock.close()


def validate_alt_args(args):
    for arg in args:
        option = arg.split("=", 1)[0]
        if option.startswith("--") and len(option) >= 3 and "--root".startswith(option):
            raise ValueError("隔离分支命令拒绝--root及其缩写，避免误写旧节点")


def mission_main(argv):
    parser = argparse.ArgumentParser(description="终止条件状态（区分T3-v1历史代理与T3-v2当前未解状态）与低权重隔离调度；旧节点只读")
    parser.add_argument("action", choices=("status", "priorities", "refresh", "check"))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--reason")
    args = parser.parse_args(argv)
    root = core.resolve_root(None)
    if args.action == "status":
        result = mission_status(root)
    elif args.action == "priorities":
        result = priorities(root)
    elif args.action == "refresh":
        if not args.reason:
            raise ValueError("刷新必须有--reason")
        result = refresh_mission(root, args.reason)
    else:
        checked = preservation(root)
        if not checked["passed"]:
            raise ValueError("旧节点保护校验失败：" + str(checked))
        result = {"valid": True, "legacy_preservation": checked, "status": mission_status(root)}
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=None if args.json else 2))
    return 0


def main():
    argv = sys.argv[1:]
    if argv == ["--version"]:
        print(VERSION)
        return 0
    if argv in (["--help"], ["-h"], []):
        print("PNP Research hub 0.3.0\n新增与分支入口：\n"
              "  pnp-research alt <旧控制器命令> [--json]         # T3-v1 历史封闭单遍代理分支\n"
              "  pnp-research practical <旧控制器命令> [--json]   # T3-v2 现实能力保全核心分支（只读兼容投影）\n"
              "  pnp-research mission status|priorities|check [--json]\n"
              "  pnp-research mission refresh --reason context-resume [--json]\n"
              "说明：mission status 明确区分 T3-v1 历史条件代理与 T1/T2/T3-v2 当前 UNRESOLVED 状态；原命令保持兼容。\n\n"
              + core.make_parser().format_help())
        return 0
    try:
        if argv[0] == "mission":
            return mission_main(argv[1:])
        if argv[0] in {"alt", "practical"}:
            args = argv[1:]
            validate_alt_args(args)
            if argv[0] == "practical" and any(a in {"init", "refresh", "update", "restore"} for a in args):
                raise ValueError("practical分支写入须经alternatives/practical-core/tools/board_v1.py带锁事务，禁止直接覆盖投影")
            root = core.resolve_root(None)
            before = legacy_fingerprint(root)
            target = (branch_root(root, "closed-llm") if argv[0] == "alt"
                      else branch_root(root, "practical-core", registry_v2(root) or {"branches": {"practical-core": {"path": "alternatives/practical-core"}}}))
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("research.py")),
                                     "--root", str(target), *args],
                                    capture_output=True, text=True)
            if before != legacy_fingerprint(root):
                raise ValueError("旧分支在分支操作中变更；停止并检查writer")
            sys.stdout.write(result.stdout)
            sys.stderr.write(result.stderr)
            return result.returncode
    except (ValueError, KeyError, OSError) as exc:
        if "--json" in argv:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"错误：{exc}", file=sys.stderr)
        return 2
    os.execv(sys.executable, [sys.executable, str(Path(__file__).with_name("research.py")), *argv])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
