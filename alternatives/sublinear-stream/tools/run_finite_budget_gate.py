#!/usr/bin/env python3
"""Persist one real finite-state run; never overwrite prior execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
A=Path(__file__).resolve().parents[1]; execution=A/'reports/finite-budget-execution-v1.json'
assert not execution.exists(),'existing execution must be preserved'
script=A/'tools/finite_budget_probe.py'; argv=[sys.executable,str(script),'--report',str(A/'reports/finite-budget-tests-v1.json')]
started=datetime.now(timezone.utc).isoformat(); result=subprocess.run(argv,cwd=A,capture_output=True,text=True,timeout=60)
out=A/'reports/finite-budget-v1.stdout.log'; err=A/'reports/finite-budget-v1.stderr.log'; out.write_text(result.stdout); err.write_text(result.stderr)
record={'passed':result.returncode==0,'returncode':result.returncode,'argv':argv,'cwd':str(A),'started':started,'ended':datetime.now(timezone.utc).isoformat(),'stdout_path':str(out),'stderr_path':str(err),'source_sha256':hashlib.sha256(script.read_bytes()).hexdigest()}
execution.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(record,ensure_ascii=False)); raise SystemExit(result.returncode)
