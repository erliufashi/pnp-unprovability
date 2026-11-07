#!/usr/bin/env python3
"""Run the two exact acceptance commands and retain raw exit evidence.

Allowed effects: test tempdirs/logs/reports and this tool's current symlink
rollback drill. Source/proofs/old research/termination certificates are not edited.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R=Path(__file__).resolve().parents[1]

def main():
    now=lambda: dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    runs=[]
    commands=[['python3','-m','unittest','discover','-s','tests','-v'],
              ['python3','tests/extension_acceptance.py']]
    for number,command in enumerate(commands,1):
        started=now()
        result=subprocess.run(command,cwd=R,capture_output=True,text=True,timeout=120)
        stdout=R/f'reports/gate-{stamp}-{number}.stdout.log'
        stderr=R/f'reports/gate-{stamp}-{number}.stderr.log'
        stdout.write_text(result.stdout); stderr.write_text(result.stderr)
        runs.append({'argv':command,'cwd':str(R),'started':started,'ended':now(),
                     'returncode':result.returncode,'stdout_path':str(stdout),
                     'stderr_path':str(stderr)})
    version=subprocess.check_output([str(Path.home()/'.local/bin/pnp-research'),'--version'],text=True).strip()
    mission=json.loads(subprocess.check_output([str(Path.home()/'.local/bin/pnp-research'),'mission','status','--json'],text=True))
    extension=json.loads((R/'reports/extension-acceptance.json').read_text())
    preserved=json.loads((R/'reports/extension-preservation.json').read_text())
    passed=all(row['returncode']==0 for row in runs) and extension.get('passed') is True and preserved.get('passed') is True and version=='0.2.0' and mission['stop'] is False
    report={'schema':1,'run_id':stamp,'producer':'tests/run_gate.py; independent verifier must actually rerun',
            'runs':runs,'passed':passed,'final_version':version,'stop':mission['stop'],
            'legacy_preserved':preserved['readback'],'extension_passed':extension['passed'],
            'source_sha256':{name:hashlib.sha256((R/name).read_bytes()).hexdigest()
                             for name in ['src/hub.py','src/research.py','tests/test_extension.py','tests/extension_acceptance.py','tests/run_gate.py']}}
    text=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    (R/f'reports/independent-tests-{stamp}.json').write_text(text)
    (R/'reports/independent-tests.json').write_text(text)
    print(json.dumps({'passed':passed,'run_id':stamp,'exits':[row['returncode'] for row in runs],
                      'report':str(R/'reports/independent-tests.json')},ensure_ascii=False))
    return 0 if passed else 1

if __name__=='__main__':
    raise SystemExit(main())
