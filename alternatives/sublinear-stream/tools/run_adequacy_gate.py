#!/usr/bin/env python3
"""Persist actual adequacy/resource probe exit and raw logs."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

A=Path(__file__).resolve().parents[1]
script=A/'tools/adequacy_probe.py'
command=[sys.executable,str(script),'--report',str(A/'reports/adequacy-probe-tests-v1.json')]
started=datetime.now(timezone.utc).isoformat()
result=subprocess.run(command,cwd=A,capture_output=True,text=True,timeout=180)
stdout=A/'reports/adequacy-probe-v1.stdout.log'; stderr=A/'reports/adequacy-probe-v1.stderr.log'
stdout.write_text(result.stdout); stderr.write_text(result.stderr)
report={'passed':result.returncode==0,'argv':command,'cwd':str(A),'started':started,
        'ended':datetime.now(timezone.utc).isoformat(),'returncode':result.returncode,
        'stdout_path':str(stdout),'stderr_path':str(stderr),
        'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
        'frozen_dependencies':{name:hashlib.sha256((A/'tools'/name).read_bytes()).hexdigest()
          for name in ['causal_model_probe.py','prefix_query_forest.py','tiny_query_summary.py']},
        'frozen_hour4_report_sha256':hashlib.sha256((A/'reports/causal-model-tests-v1.json').read_bytes()).hexdigest()}
(A/'reports/adequacy-probe-execution-v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(result.returncode)
