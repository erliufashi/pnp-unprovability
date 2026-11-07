#!/usr/bin/env python3
"""Real installed CLI acceptance, isolated mutation/recovery; no new dependencies."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
ENTRY = Path.home() / ".local/bin/pnp-research"
CLEAN = {"HOME": str(Path.home()), "PATH": f"{Path.home()}/.local/bin:/run/current-system/sw/bin:/usr/bin:/bin",
         "LANG": "C.UTF-8"}
REPORT = {"schema": 1, "checks": [], "states": {"mathematical_target": "UNRESOLVED"},
          "not_applicable": {"GUI": "纯CLI，无桌面配置变化", "authentication": "不使用网络或凭据",
                             "system_reboot": "不安装服务或会话配置", "old_release_rollback": "首次安装，无旧发布版本；另验状态恢复"}}


def command(argv, cwd="/tmp", clean=True, expected=0):
    start = time.monotonic()
    result = subprocess.run([str(x) for x in argv], cwd=cwd, env=CLEAN if clean else None,
                            text=True, capture_output=True, timeout=30)
    record = {"command": [str(x) for x in argv], "cwd": str(cwd), "clean_environment": clean,
              "returncode": result.returncode, "seconds": round(time.monotonic()-start, 4),
              "stdout": result.stdout[:8000], "stderr": result.stderr[:8000]}
    REPORT["checks"].append(record)
    assert result.returncode == expected, record
    record["passed"] = True
    return result.stdout


def cli(*args, root=None, expected=0):
    argv = [ENTRY]
    if root is not None:
        argv += ["--root", root]
    argv += list(args) + ["--json"]
    output = command(argv, expected=expected)
    value = json.loads(output)
    assert value["ok"] == (expected == 0), value
    return value


def main():
    try:
        command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
        command(["/bin/sh", "-c", "command -v pnp-research && pnp-research --help"], cwd="/")
        command(["/bin/sh", "-c", "pnp-research --version && pnp-research --version"])
        shell = shutil.which("zsh")
        if shell:
            command([shell, "-ic", "command -v pnp-research && pnp-research --version"], clean=False)
        else:
            raise AssertionError("用户zsh未发现，不能冒充普通交互shell入口通过")
        assert cli("check")["valid"]
        assert len(cli("status")["nodes"]) == 25
        assert cli("paths")["root"] == str(ROOT)
        installed = Path(cli("paths")["controller"])
        assert hashlib.sha256(installed.read_bytes()).digest() == hashlib.sha256((ROOT/"src/research.py").read_bytes()).digest()
        with tempfile.TemporaryDirectory(prefix="pnp acceptance 带空格 ") as temporary:
            test_root = Path(temporary)
            (test_root/"research").mkdir()
            shutil.copy2(ROOT/"research/graph.json", test_root/"research/graph.json")
            (test_root/"evidence.txt").write_text("恢复演练证据；不是P/NP证明\n")
            first = cli("init", root=test_root)
            selected = first["selected"]
            snapshot = cli("snapshot", root=test_root)["snapshot"]
            before = json.loads((test_root/"research/state.json").read_text())
            exhausted = cli("update", selected, "--status", "exhausted", "--current", "0.01",
                            "--note", "隔离耗尽重选实测", "--evidence", "evidence.txt", "--worked", root=test_root)
            assert exhausted["selected"] != selected
            assert exhausted["reason"] == "exhausted:" + selected
            resumed = cli("refresh", "--reason", "context-resume", root=test_root)
            assert resumed["round"] > before["round"]
            assert resumed["reason"] == "context-resume"
            restored = cli("restore", snapshot, "--reason", "recovery-drill", root=test_root)
            after = json.loads((test_root/"research/state.json").read_text())
            assert after["nodes"] == before["nodes"]
            assert len(after["events"]) > len(before["events"])
            assert restored["selected"] == selected
            assert cli("check", root=test_root)["valid"]
            cli("update", "DOES-NOT-EXIST", "--note", "故障验收", root=test_root, expected=2)
            cli("restore", "../state.json", "--reason", "refuse-path-traversal", root=test_root, expected=2)
        REPORT["states"].update(installed=True, configured=True, clean_shell_end_to_end=True,
                                 interactive_shell_discovery=True, machine_json_consumption=True,
                                 context_resume_protocol_tested=True, exhausted_reselection_tested=True,
                                 state_recovery_drill=True, version_rollback_drill=False,
                                 automatic_pi_compaction_hook=False)
        REPORT["passed"] = True
    except Exception as exc:
        REPORT["passed"] = False
        REPORT["failure"] = str(exc)
    (ROOT/"reports/acceptance.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"passed": REPORT["passed"], "checks": len(REPORT["checks"]),
                      "report": str(ROOT/"reports/acceptance.json"), "failure": REPORT.get("failure")}, ensure_ascii=False))
    return 0 if REPORT["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
