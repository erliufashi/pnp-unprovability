#!/usr/bin/env python3
"""Real extension CLI, isolated recovery, old→new rollback, legacy immutability."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
ENTRY=Path.home()/".local/bin/pnp-research"
RELEASES=Path.home()/".local/share/pnp-research/releases"
CURRENT=RELEASES.parent/"current"
BASE={"HOME":str(Path.home()),"PATH":f"{Path.home()}/.local/bin:/run/current-system/sw/bin:/usr/bin:/bin","LANG":"C.UTF-8"}
REPORT={"schema":1,"checks":[],"assertions":{},"not_applicable":{"GUI":"纯CLI，不改桌面或shell配置","authentication":"无网络/凭据","real_200B":"未下载部署；交付为量化profile的形式定理","human_equivalence":"未实证验证"}}
spec=importlib.util.spec_from_file_location("extension_hub",ROOT/"src/hub.py")
hub=importlib.util.module_from_spec(spec); spec.loader.exec_module(hub)


def command(argv,env=None,expected=0):
    started=time.monotonic()
    result=subprocess.run([str(x) for x in argv],cwd="/tmp",env=env or BASE,capture_output=True,text=True,timeout=30)
    row={"command":[str(x) for x in argv],"cwd":"/tmp","clean_environment":True,
         "returncode":result.returncode,"seconds":round(time.monotonic()-started,4),
         "stdout":result.stdout[:6000],"stderr":result.stderr[:6000]}
    REPORT["checks"].append(row)
    assert result.returncode==expected,row
    row["passed"]=True
    return result.stdout


def cli(*args,env=None,expected=0):
    value=json.loads(command([ENTRY,*args,"--json"],env,expected))
    assert value["ok"]==(expected==0),value
    return value


def switch_release(version):
    destination=RELEASES/version
    assert destination.is_dir()
    temporary=CURRENT.with_name('.acceptance-current')
    if temporary.is_symlink(): temporary.unlink()
    temporary.symlink_to(destination)
    os.replace(temporary,CURRENT)


def main():
    try:
        command([sys.executable,"-m","unittest","discover","-s",str(ROOT/"tests"),"-v"])
        command(["/bin/sh","-c","command -v pnp-research && pnp-research --help"])
        assert command([ENTRY,"--version"]).strip()=="0.2.0"
        assert cli("check")["valid"]
        assert cli("alt","check")["valid"]
        assert cli("mission","status")["stop"] is False  # before independent parent review
        rows=cli("mission","priorities")
        assert rows["weights"]=={"T1":1,"T2":1,"T3":.25}
        for row in rows["nodes"]:
            assert row["weighted_priority"]==row["raw_priority"]*row["weight"]
        assert hub.preservation(ROOT)["passed"]
        # Mutations use a copied workspace/config. The installed launcher/code are real.
        with tempfile.TemporaryDirectory(prefix="pnp extension 验收 带空格 ") as temporary:
            temp=Path(temporary); data=temp/"research root"; config=temp/"xdg config"
            baseline=json.loads((ROOT/"reports/extension-preservation.json").read_text())
            for name in baseline["baseline"]:
                out=data/name; out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/name,out)
            (data/"reports").mkdir(exist_ok=True)
            shutil.copy2(ROOT/"reports/extension-preservation.json",data/"reports/extension-preservation.json")
            shutil.copy2(ROOT/"research/termination.json",data/"research/termination.json")
            alt=data/"alternatives/closed-llm"; (alt/"research").mkdir(parents=True)
            shutil.copy2(ROOT/"alternatives/closed-llm/research/graph.json",alt/"research/graph.json")
            (alt/"notes").mkdir(); (alt/"notes/evidence.txt").write_text("隔离恢复/耗尽证据；不是数学证明\n")
            cfg=config/"pnp-research"; cfg.mkdir(parents=True)
            (cfg/"config.json").write_text(json.dumps({"root":str(data)}))
            env={**BASE,"XDG_CONFIG_HOME":str(config)}
            before=hub.legacy_fingerprint(data)
            old_scores=cli("status",env=env)["nodes"]
            first=cli("alt","init",env=env); chosen=first["selected"]
            snap=cli("alt","snapshot",env=env)["snapshot"]
            original=json.loads((alt/"research/state.json").read_text())
            changed=cli("alt","update",chosen,"--status","exhausted","--current","0.01",
                        "--note","隔离模板耗尽实测","--evidence","notes/evidence.txt","--worked",env=env)
            assert changed["selected"]!=chosen
            resumed=cli("mission","refresh","--reason","context-resume",env=env)
            assert resumed["reason"]=="context-resume" and resumed["legacy_unchanged"]
            assert before==hub.legacy_fingerprint(data)
            assert old_scores==cli("status",env=env)["nodes"]
            restored=cli("alt","restore",snap,"--reason","isolated-recovery",env=env)
            after=json.loads((alt/"research/state.json").read_text())
            assert after["nodes"]==original["nodes"]
            assert len(after["events"])>len(original["events"])
            assert restored["selected"]==chosen
            assert cli("alt","check",env=env)["valid"]
            assert hub.preservation(data)["passed"]
            cli("alt","refresh","--roo",str(ROOT),"--reason","block-root-override",env=env,expected=2)
            assert before==hub.legacy_fingerprint(data)
            REPORT["assertions"].update(state_snapshot_modify_restore=True,audit_retained=True,
                context_resume_local_clock_only=True,exhaustion_local_reselection=True,
                original_bytes_unchanged=True,original_scores_unchanged=True,root_override_abbreviation_refused=True)
        # Deliberate code rollback, always reactivate 0.2.0 even if a check fails.
        before=hub.legacy_fingerprint(ROOT)
        versions=[]
        try:
            for version in ("0.2.0","0.1.0","0.2.0"):
                switch_release(version)
                actual=command([ENTRY,"--version"]).strip()
                assert actual==version
                assert cli("check")["valid"]
                versions.append(actual)
        finally:
            switch_release("0.2.0")
        assert before==hub.legacy_fingerprint(ROOT)
        assert cli("alt","check")["valid"]
        preservation=hub.preservation(ROOT,save=True)
        assert preservation["passed"]
        REPORT["assertions"].update(code_rollback_versions=versions,legacy_check_each_release=True,
            final_release="0.2.0",real_root_unchanged=True,weights_strictly_weaker=True,
            legacy_preservation=preservation,qualified_certificate_not_yet_activated=True)
        REPORT["passed"]=True
    except Exception as exc:
        REPORT["passed"]=False; REPORT["failure"]=str(exc)
    (ROOT/"reports/extension-acceptance.json").write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"passed":REPORT["passed"],"checks":len(REPORT["checks"]),
                      "failure":REPORT.get("failure"),"report":str(ROOT/"reports/extension-acceptance.json")},ensure_ascii=False))
    return 0 if REPORT["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
