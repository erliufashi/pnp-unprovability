import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "src/research.py"
spec = importlib.util.spec_from_file_location("research", SOURCE)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def graph():
    nodes = []
    for layer, prefix in ((1, "D"), (2, "M"), (3, "E")):
        for number in (1, 2):
            nodes.append({"id": f"{prefix}{number}", "layer": layer,
                          "title": "独立用例", "role": "测试职责", "acceptance": "断言通过",
                          "artifact": "evidence.txt", "seed": {"current": .5, "remaining": .5,
                          "novelty": .5, "confidence": 1, "cost": 1}})
    return {"schema": 1, "nodes": nodes,
            "edges": [["E1", "M1"], ["E2", "M2"], ["M1", "D1"], ["M2", "D2"]]}


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.g = graph()
        self.s = r.initial_state(self.g)

    def choose(self):
        return r.refresh_state(self.g, self.s, "test")["selected"]

    def rows(self):
        return {row["id"]: row for row in r.score_graph(self.g, self.s)}

    def test_current_value_changes_choice(self):
        self.assertEqual(self.choose(), "E1")
        self.s["nodes"]["E2"]["current"] = .9
        self.assertEqual(self.choose(), "E2")

    def test_remaining_value_changes_choice(self):
        self.assertEqual(self.choose(), "E1")
        self.s["nodes"]["E2"]["remaining"] = .9
        self.assertEqual(self.choose(), "E2")

    def test_freshness_changes_choice(self):
        self.assertEqual(self.choose(), "E1")
        self.s["nodes"]["E2"]["novelty"] = 1
        self.assertEqual(self.choose(), "E2")

    def test_neighbor_parameters_propagate(self):
        before = self.rows()["E2"]
        self.s["nodes"]["M2"].update(current=1, remaining=1, revision=1)
        after = self.rows()["E2"]
        self.assertGreater(after["effective_current"], before["effective_current"])
        self.assertGreater(after["effective_remaining"], before["effective_remaining"])
        self.assertGreater(after["freshness"], before["freshness"])
        self.assertEqual(after["changed_neighbors"], ["M2"])
        self.assertEqual(self.choose(), "E2")

    def test_no_gain_decays_freshness(self):
        before = self.rows()["E1"]["freshness"]
        self.s["nodes"]["E1"]["stagnation"] = 6
        self.assertLess(self.rows()["E1"]["freshness"], before)

    def test_age_capped(self):
        self.s["round"] = 100
        a = self.rows()["E1"]["freshness"]
        self.s["round"] = 100000
        self.assertEqual(a, self.rows()["E1"]["freshness"])

    def test_exhausted_not_resurrected_by_neighbor(self):
        self.s["nodes"]["E1"].update(status="exhausted", remaining=0)
        self.s["nodes"]["M1"].update(current=1, remaining=1, revision=100)
        self.s["round"] = 100000
        self.assertFalse(self.rows()["E1"]["eligible"])
        self.assertEqual(self.choose(), "E2")

    def test_blocked_excluded(self):
        self.s["nodes"]["E1"]["status"] = "blocked"
        self.assertEqual(self.choose(), "E2")

    def test_context_resume_records_new_round(self):
        before = self.s["round"]
        event = r.refresh_state(self.g, self.s, "context-resume")
        self.assertEqual(self.s["round"], before + 1)
        self.assertEqual(event["reason"], "context-resume")
        self.assertTrue(event["ranking"][0]["reason"])

    def test_reject_reverse_dependency(self):
        self.g["edges"].append(["D1", "E1"])
        with self.assertRaises(ValueError):
            r.validate_graph(self.g)

    def test_reject_same_layer_and_cycle(self):
        self.g["edges"].append(["M1", "M2"])
        with self.assertRaises(ValueError):
            r.validate_graph(self.g)

    def test_reject_nan(self):
        self.s["nodes"]["E1"]["current"] = float("nan")
        with self.assertRaises(ValueError):
            r.score_graph(self.g, self.s)

    def test_done_parent_prevents_orphan_work(self):
        self.s["nodes"]["M1"]["status"] = "done"
        self.assertFalse(self.rows()["E1"]["eligible"])


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pnp test ")
        self.root = Path(self.tmp.name)
        (self.root / "research").mkdir()
        r.atomic_json(self.root / "research/graph.json", graph())
        (self.root / "evidence.txt").write_text("局部推导证据\n")
        self.store = r.Store(self.root)
        self.s = r.initial_state(self.store.graph)
        r.refresh_state(self.store.graph, self.s, "initialization")
        self.store.save(self.s)

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SOURCE), "--root", str(self.root), *args, "--json"],
                              capture_output=True, text=True, timeout=10)

    def test_exhaustion_update_immediately_reselects(self):
        event = self.store.update(self.s, "E1", {"status": "exhausted"}, "模板无剩余价值",
                                  "evidence.txt", worked=True)
        self.assertEqual(event["reason"], "exhausted:E1")
        self.assertEqual(self.store.load()["selected"], "E2")
        self.assertEqual(self.s["nodes"]["E1"]["remaining"], 0)

    def test_done_requires_evidence(self):
        with self.assertRaises(ValueError):
            self.store.update(self.s, "E1", {"status": "done"}, "没有证据")

    def test_evidence_cannot_escape_root(self):
        with self.assertRaises(ValueError):
            self.store.evidence("../outside.txt")

    def test_reject_tampered_evidence(self):
        self.store.update(self.s, "E1", {"status": "done"}, "完成", "evidence.txt")
        (self.root / "evidence.txt").write_text("偷偷改写")
        result = self.cli("check")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_history_projection_matches_authority(self):
        self.store.update(self.s, "E1", {"current": .7}, "有新证据", "evidence.txt")
        events = [json.loads(line) for line in self.store.history_path.read_text().splitlines()]
        self.assertEqual(events, self.store.load()["events"])

    def test_restore_preserves_audit_history(self):
        snap = json.loads(self.cli("snapshot").stdout)["snapshot"]
        result = self.cli("update", "E1", "--current", "0.99", "--note", "恢复演练")
        self.assertEqual(result.returncode, 0)
        prior_events = len(self.store.load()["events"])
        result = self.cli("restore", snap, "--reason", "recovery-drill")
        self.assertEqual(result.returncode, 0)
        restored = self.store.load()
        self.assertEqual(restored["nodes"]["E1"]["current"], .5)
        self.assertEqual(len(restored["events"]), prior_events + 1)
        self.assertEqual(restored["events"][-1]["reason"], "restore:recovery-drill")

    def test_cli_context_resume(self):
        before = self.store.load()["round"]
        result = self.cli("refresh", "--reason", "context-resume")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["round"], before + 1)

    def test_json_failure_exit_nonzero(self):
        result = self.cli("update", "unknown", "--note", "错误ID")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_no_silent_reinitialization(self):
        result = self.cli("init")
        self.assertEqual(result.returncode, 2)
        self.assertIn("禁止覆盖", result.stdout)

    def test_snapshot_path_traversal_rejected(self):
        result = self.cli("restore", "../state.json", "--reason", "bad")
        self.assertEqual(result.returncode, 2)

    def test_graph_change_rejected(self):
        changed = copy.deepcopy(self.store.graph)
        changed["nodes"][0]["title"] = "图谱修改"
        r.atomic_json(self.store.graph_path, changed)
        result = self.cli("status")
        self.assertEqual(result.returncode, 2)

    def test_missing_history_repaired_by_explicit_refresh(self):
        self.store.history_path.write_text("")
        self.assertEqual(self.cli("check").returncode, 2)
        self.assertEqual(self.cli("refresh", "--reason", "repair-projection").returncode, 0)
        self.assertEqual(self.cli("check").returncode, 0)


if __name__ == "__main__":
    unittest.main()
