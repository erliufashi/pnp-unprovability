#!/usr/bin/env python3
"""Capture one real hybrid run; preserve prior attempt artifacts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import subprocess
import sys

A=Path(__file__).resolve().parents[1]
execution=A/'reports/hybrid-execution-v1.json'
assert not execution.exists(),'prior execution exists: do not overwrite it'
script=A/'tools/horizon_hybrid_probe.py'
argv=[sys.executable,str(script),'--report',str(A/'reports/hybrid-tests-v1.json')]
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(argv,cwd=A,capture_output=True,text=True,timeout=180)
out=A/'reports/hybrid-v1.stdout.log'; err=A/'reports/hybrid-v1.stderr.log'
out.write_text(result.stdout); err.write_text(result.stderr)
record={'passed':result.returncode==0,'returncode':result.returncode,'argv':argv,'cwd':str(A),
        'started':started,'ended':datetime.now(timezone.utc).isoformat(),
        'stdout_path':str(out),'stderr_path':str(err),
        'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
        'frozen_dependencies':{n:hashlib.sha256((A/'tools'/n).read_bytes()).hexdigest() for n in
           ['causal_model_probe.py','prefix_query_forest.py','tiny_query_summary.py','pruned_query_probe.py']}}
execution.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False)); raise SystemExit(result.returncode)
