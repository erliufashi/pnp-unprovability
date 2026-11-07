#!/usr/bin/env python3
"""Persist actual compact neural retrieval experiment exit/logs."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

A=Path(__file__).resolve().parents[1]
script=A/'tools/neural_retrieval_probe.py'
command=[sys.executable,str(script),'--report',str(A/'reports/retrieval-tests-v1.json')]
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(command,cwd=A,capture_output=True,text=True,timeout=180)
stdout=A/'reports/retrieval-v1.stdout.log'; stderr=A/'reports/retrieval-v1.stderr.log'
stdout.write_text(result.stdout); stderr.write_text(result.stderr)
report={'passed':result.returncode==0,'argv':command,'cwd':str(A),'started':started,
        'ended':datetime.now(timezone.utc).isoformat(),'returncode':result.returncode,
        'stdout_path':str(stdout),'stderr_path':str(stderr),
        'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest()}
(A/'reports/retrieval-execution-v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(result.returncode)
