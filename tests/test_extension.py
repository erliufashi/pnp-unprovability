import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest

from test_research import graph

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hub", ROOT/"src/hub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)
core = hub.core
spec2 = importlib.util.spec_from_file_location("index_sanity", ROOT/"alternatives/closed-llm/tools/index_sanity.py")
index = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(index)


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pnp extension test ")
        self.root = Path(self.tmp.name)
        self.alt = self.root/"alternatives/closed-llm"
        for path in (self.root, self.alt):
            (path/"research").mkdir(parents=True)
            core.atomic_json(path/"research/graph.json", graph())
            store = core.Store(path)
            state = core.initial_state(store.graph)
            core.refresh_state(store.graph, state, "init")
            store.save(state)
        self.registry = {
            "branches": {"main":{"path":".","weight":1}, "closed-llm":{"path":"alternatives/closed-llm","weight":.25}},
            "terminals": {key: {"weight": weight,"status":"pending_review","certificate":None,
                                 "required_goal":"test-proof","conditions":["finite closed profile"]}
                          for key, weight in (("T1",1),("T2",1),("T3",.25))}}
        core.atomic_json(self.root/"research/termination.json", self.registry)
        (self.root/"reports").mkdir()
        before = hub.legacy_fingerprint(self.root)
        store = core.Store(self.root)
        scores = core.score_graph(store.graph, store.load())
        core.atomic_json(self.root/"reports/extension-preservation.json", {
            "baseline": {"research/"+name: value for name,value in before.items()},
            "baseline_scores": scores})

    def tearDown(self):
        self.tmp.cleanup()

    def test_weights_are_weaker_and_product_exact(self):
        result = hub.priorities(self.root)
        self.assertEqual(result["weights"], {"T1":1,"T2":1,"T3":.25})
        for row in result["nodes"]:
            self.assertEqual(row["weighted_priority"], row["raw_priority"]*row["weight"])
        self.assertEqual(result["selected"]["branch"], "main")

    def test_reject_stronger_new_weight(self):
        self.registry["terminals"]["T3"]["weight"] = 1
        core.atomic_json(self.root/"research/termination.json", self.registry)
        with self.assertRaises(ValueError):
            hub.priorities(self.root)

    def test_neighbor_parameters_do_not_cross_branches(self):
        before = [r for r in hub.priorities(self.root)["nodes"] if r["branch"]=="main"]
        store = core.Store(self.alt)
        state = store.load()
        store.update(state,"M1",{"current":1,"remaining":1},"new neighbor evidence")
        after = [r for r in hub.priorities(self.root)["nodes"] if r["branch"]=="main"]
        self.assertEqual(before, after)

    def test_context_resume_does_not_age_old_nodes(self):
        before = hub.legacy_fingerprint(self.root)
        event = hub.refresh_mission(self.root,"context-resume")
        self.assertEqual(event["reason"],"context-resume")
        self.assertEqual(before,hub.legacy_fingerprint(self.root))
        self.assertTrue(hub.preservation(self.root)["passed"])

    def test_exhaustion_reselects_only_alt(self):
        before = hub.legacy_fingerprint(self.root)
        (self.alt/"evidence.txt").write_text("local evidence")
        store=core.Store(self.alt); state=store.load()
        event=store.update(state,"E1",{"status":"exhausted"},"local exhausted","evidence.txt")
        self.assertEqual(event["selected"],"E2")
        self.assertEqual(before,hub.legacy_fingerprint(self.root))
        self.assertTrue(hub.preservation(self.root)["scores_unchanged"])

    def test_pending_does_not_stop(self):
        self.assertFalse(hub.mission_status(self.root)["stop"])

    def test_matching_receipt_required(self):
        receipt=self.root/"proof.receipt.json"
        core.atomic_json(receipt,{"goal_id":"test-proof","verdict":"pass"})
        term=self.registry["terminals"]["T3"]
        term["status"]="proved_conditional_proxy"
        term["certificate"]={"path":str(receipt),"sha256":hub.sha(receipt)}
        core.atomic_json(self.root/"research/termination.json",self.registry)
        result=hub.mission_status(self.root)
        self.assertTrue(result["stop"])
        self.assertTrue(result["standard_targets_unresolved"])
        self.assertEqual(result["stop_scope"],"qualified_closed_LLM_proxy")
        receipt.write_text('{"goal_id":"wrong","verdict":"pass"}')
        with self.assertRaises(ValueError):
            hub.mission_status(self.root)

    def test_root_override_abbreviations_blocked(self):
        for option in ("--root", "--root=/tmp", "--roo", "--ro=/tmp", "--r"):
            with self.assertRaises(ValueError):
                hub.validate_alt_args(["refresh", option, "/tmp"])
        hub.validate_alt_args(["refresh", "--reason", "context-resume"])

    def test_no_alias_to_old_root(self):
        self.registry["branches"]["closed-llm"]["path"]="."
        with self.assertRaises(ValueError):
            hub.branch_root(self.root,"closed-llm",self.registry)

    def test_v2_status_distinguishes_historical_t3_v1_from_unresolved_t3_v2(self):
        receipt = self.root/"proof.receipt.json"
        core.atomic_json(receipt, {"goal_id": "test-proof", "verdict": "pass"})
        self.registry["terminals"]["T3"]["status"] = "proved_conditional_proxy"
        self.registry["terminals"]["T3"]["certificate"] = {"path": str(receipt), "sha256": hub.sha(receipt)}
        core.atomic_json(self.root/"research/termination.json", self.registry)
        prac = self.root/"alternatives/practical-core"
        (prac/"research").mkdir(parents=True)
        core.atomic_json(prac/"research/graph.json", graph())
        store = core.Store(prac)
        state = core.initial_state(store.graph)
        core.refresh_state(store.graph, state, "init")
        store.save(state)
        core.atomic_json(self.root/"research/termination-v2.json", {
            "schema": 2,
            "phase": "stage_wrapup_archived",
            "branches": {
                "main": {"path": ".", "weight": 1.0},
                "practical-core": {"path": "alternatives/practical-core", "weight": 0.25},
            },
            "terminals": {
                "T1": {"weight": 1.0, "status": "unresolved"},
                "T2": {"weight": 1.0, "status": "unresolved"},
                "T3_v1": {"weight": 0.25, "status": "historical_conditional_proxy"},
                "T3_v2": {"weight": 0.25, "status": "unresolved"},
            },
        })
        st = hub.mission_status(self.root)
        self.assertTrue(st["stop"])
        self.assertEqual(st["stop_scope"], "qualified_closed_LLM_proxy")
        self.assertEqual(st["current_contract_version"], 2)
        self.assertFalse(st["current_goal_stop"])
        self.assertTrue(st["t3_v1_historical_only"])
        self.assertEqual(st["t3_v2"]["status"], "unresolved")
        pri = hub.priorities(self.root)
        self.assertEqual(pri["weights"]["T3_v2"], 0.25)
        self.assertTrue(any(r["branch"] == "practical-core" and r["weight"] == 0.25 for r in pri["nodes"]))


class IndexSanityTests(unittest.TestCase):
    """Finite sanity checks, NOT substitutes for asymptotic proofs."""
    def test_exhaustive_small_inputs(self):
        for m in range(1,8):
            for values in itertools.product("01",repeat=m):
                word="".join(values)
                for pos in range(1,m+1):
                    self.assertEqual(index.harness_accepts(index.encode_index(word,pos)),word[pos-1]=="1")

    def test_invalid_encodings_rejected(self):
        for text in ("", "#1", "01", "1#0", "1#11", "1##1", "01#11", "01#001", "01#a"):
            self.assertFalse(index.harness_accepts(text),text)

    def test_distinguishing_prefix_suffixes(self):
        for m in range(1,7):
            words=["".join(bits) for bits in itertools.product("01",repeat=m)]
            for a,b in itertools.combinations(words,2):
                pos=next(i+1 for i in range(m) if a[i]!=b[i])
                self.assertNotEqual(index.harness_accepts(index.encode_index(a,pos)),
                                    index.harness_accepts(index.encode_index(b,pos)))


if __name__=="__main__":
    unittest.main()
