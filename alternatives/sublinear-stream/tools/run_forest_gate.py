#!/usr/bin/env python3
"""Persist actual prefix-forest experiment exit and raw logs."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

A=Path(__file__).resolve().parents[1]
script=A/'tools/prefix_query_forest.py'
command=[sys.executable,str(script),'--report',str(A/'reports/prefix-forest-tests-v1.json')]
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(command,cwd=A,capture_output=True,text=True,timeout=180)
stdout=A/'reports/prefix-forest-v1.stdout.log'; stderr=A/'reports/prefix-forest-v1.stderr.log'
stdout.write_text(result.stdout); stderr.write_text(result.stderr)
report={'passed':result.returncode==0,'argv':command,'cwd':str(A),'started':started,
        'ended':datetime.now(timezone.utc).isoformat(),'returncode':result.returncode,
        'stdout_path':str(stdout),'stderr_path':str(stderr),
        'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
        'toy_primitives_sha256':hashlib.sha256((A/'tools/tiny_query_summary.py').read_bytes()).hexdigest()}
(A/'reports/prefix-forest-execution-v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(result.returncode)
