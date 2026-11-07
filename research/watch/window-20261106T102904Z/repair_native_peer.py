from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
W=Path(__file__).resolve().parent
prefix=Path('/home/desk/.local/share/pi-subagents-runtime-peers/releases/chord-1.3.0')
link=Path('/home/desk/.pi/agent/node_modules/@earendil-works/chord')
host=Path('/home/desk/.pi/agent/install/releases/1.3.0/node_modules/@earendil-works/pi-coding-agent')
expected='sha512-qqYhjALZ193atpBzmmS+M5pHQoiI4Aynetc1jXpv+5O2crXH3Y8wbFEy33orU2nmFrlw1U36rsdgUjaW4b3m/w=='
assert not prefix.exists() and not link.exists() and not link.is_symlink()
original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [host/'package.json',host/'dist/index.js']}
prefix.mkdir(parents=True)
argv=['npm','install','--prefix',str(prefix),'--save-exact','--omit=dev','--ignore-scripts','--no-audit','--no-fund','--registry=https://registry.npmjs.org','--fetch-timeout=30000','--fetch-retries=1','@earendil-works/chord@1.3.0']
r=subprocess.run(argv,capture_output=True,text=True,timeout=120)
(W/'native-peer-install.stdout.log').write_text(r.stdout); (W/'native-peer-install.stderr.log').write_text(r.stderr)
assert r.returncode==0,'actual npm install failed'
lock=json.loads((prefix/'package-lock.json').read_text()); installed=lock['packages']['node_modules/@earendil-works/chord']
assert installed['version']=='1.3.0' and installed['integrity']==expected
package=prefix/'node_modules/@earendil-works/chord'; manifest=json.loads((package/'package.json').read_text())
assert manifest['name']=='@earendil-works/chord' and './context' in manifest['exports']
link.parent.mkdir(parents=True,exist_ok=True); link.symlink_to(package,target_is_directory=True)
js="""import {resolveHostPeerAliases} from '/home/desk/.pi/agent/npm/node_modules/pi-subagents/src/runs/background/runner-aliases.js';
const r=resolveHostPeerAliases('/home/desk/.pi/agent/install/releases/1.3.0/node_modules/@earendil-works/pi-coding-agent');
if(r.missing.length) throw new Error(JSON.stringify(r.missing));
const a=await import(r.aliases['@earendil-works/chord']); const b=await import(r.aliases['@earendil-works/chord/context']);
console.log(JSON.stringify({missing:r.missing,chordExports:Object.keys(a).length,contextExports:Object.keys(b).length,paths:{root:r.aliases['@earendil-works/chord'],context:r.aliases['@earendil-works/chord/context']}}));"""
clean={'HOME':'/home/desk','PATH':'/run/current-system/sw/bin:/usr/bin:/bin','LC_ALL':'C.UTF-8'}
test=subprocess.run(['node','--input-type=module','-e',js],capture_output=True,text=True,env=clean,timeout=30)
(W/'native-peer-consumer.stdout.log').write_text(test.stdout); (W/'native-peer-consumer.stderr.log').write_text(test.stderr)
assert test.returncode==0,'actual peer import/consumer failed'
for p,sha in original.items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha
record={'installed':True,'version':'1.3.0','integrity':expected,'scripts_disabled':True,'prefix':str(prefix),'managed_link':str(link),'link_target':str(package),'host_snapshot_unchanged':original,'ordinary_clean_node_import':json.loads(test.stdout),'native_research_child_execution':'NOT YET RETRIED OR VERIFIED','rollback':'Only after owned children stop: remove this exact symlink if target still matches; retain immutable sidecar/lock/logs. No Pi host files or default routes were changed.','at':datetime.now(timezone.utc).isoformat()}
(W/'native-peer-repair.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(record,ensure_ascii=False))
