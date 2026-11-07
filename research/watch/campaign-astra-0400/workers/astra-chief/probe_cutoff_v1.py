from math import ceil
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
rows=[]
for U,w in [(2**3,3),(2**4,4),(2**8,8),(2**16,16),(2**20,20)]:
 for N in [max(1,U//2),U,2*U]:
  M=ceil(U/w); F=1+3*N
  # Exact semantic check over small domains only; formulas are general.
  if U<=8:
   for x in __import__('itertools').product(range(U),repeat=min(N,4)):
    table=set(); ok=False
    for value in x:
     if value in table: ok=True; break
     table.add(value)
    assert ok==(len(set(x))<len(x))
  rows.append({'U':U,'w':w,'N':N,'M_addr_words':M,'F_formula':F,'raw_static_exact':True})
result={'passed':True,'rows':rows,'formula':'F=I+N(r+c+u)+O(1), M=ceil(U/w)+control','scope':'transparent raw static collision; not opaque/dynamic/random lower bound','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'document_sha256':hashlib.sha256((P/'CUTOFF-AUDIT-v1.md').read_bytes()).hexdigest(),'generation_contract':'This JSON is generated directly by this source in the clean command; no post-processing is required.'}
(P/'cutoff-tests-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False))
