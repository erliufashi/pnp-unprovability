#!/usr/bin/env python3
"""Persist actual multilayer toy experiment exit and raw logs."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

A=Path(__file__).resolve().parents[1]
script=A/'tools/causal_model_probe.py'
command=[sys.executable,str(script),'--report',str(A/'reports/causal-model-tests-v1.json')]
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(command,cwd=A,capture_output=True,text=True,timeout=180)
stdout=A/'reports/causal-model-v1.stdout.log'; stderr=A/'reports/causal-model-v1.stderr.log'
stdout.write_text(result.stdout); stderr.write_text(result.stderr)
report={'passed':result.returncode==0,'argv':command,'cwd':str(A),'started':started,
        'ended':datetime.now(timezone.utc).isoformat(),'returncode':result.returncode,
        'stdout_path':str(stdout),'stderr_path':str(stderr),
        'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
        'frozen_kernel_sha256':hashlib.sha256((A/'tools/prefix_query_forest.py').read_bytes()).hexdigest(),
        'frozen_word_sha256':hashlib.sha256((A/'tools/tiny_query_summary.py').read_bytes()).hexdigest()}
(A/'reports/causal-model-execution-v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(result.returncode)
