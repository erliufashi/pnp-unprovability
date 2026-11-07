from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
text=(P/'CONTRACT-MATRIX-v1.md').read_text()
required=['输入可见性','响应字母表','persistent state','生命周期','组合/历史','成功量词','OPAQUE-v2','FNS/C62','RAND-ED审计','D-GVC-BATCH-1','B56/B57','ASTRA-E parity-index','D-GVC-RETRY-1','opaque→raw','强错误→1/3','静态index→动态update','Build可计算→无泄漏','T1/T2/T3-v2仍`UNRESOLVED`']
missing=[x for x in required if x not in text]
assert not missing,missing
result={'passed':True,'required_terms':len(required),'missing':missing,'invalid_comparison_rules':text.count('INVALID_COMPARISON'),'source_sha256':hashlib.sha256((P/'CONTRACT-MATRIX-v1.md').read_bytes()).hexdigest(),'scope':'contract type-check, not mathematical proof or reality coverage'}
(P/'contract-matrix-tests-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False))
