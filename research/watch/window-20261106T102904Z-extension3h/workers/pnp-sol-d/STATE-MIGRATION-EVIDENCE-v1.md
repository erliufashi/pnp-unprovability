# D-GVC-STATE-1 — 持久隐状态、反馈容量与迁移账本

分类：proved-candidate（局部信息论/接口定理，未独立验收）。不是现实覆盖、运行时性能或 P/NP 分离证明。

## 结论

设隐藏答案 X 有 N 个可能值；策略有 q-bit 持久状态，每次调用之间可保存并恢复该状态；在 K 轮中每轮至多提交 L 个完整候选并得到一个 batch-membership bit；此外，整个会话最多有 h 个**额外的、公开计费的 binary input-dependent observations**（可相关、自适应；其索引/时序选择不能另携未计信息）（例如显式读取服务状态或迁移日志中的一个 bit）。如果初始状态与 X 独立，且持久状态只能由这 K 个 batch bit 和 h 个显式 observations 更新，那么精确恢复最多覆盖

`min(N, 2^h * F(K,L))` 个候选，

其中 `F(K,L)=1+sum_{j=0}^{K-1} min(L,2^j)`。均匀先验成功概率至多该容量除以 N；任意先验则是该数量个最大先验质量之和。

理由：固定所有 h 个额外观察值后，剩余策略就是原批反馈树，最多 F 个正确答案；最多 2^h 个 observation transcripts，求和得到乘法界。持久 q-bit state 本身不增加这个因子，只是树节点的 q-bit工作记忆；若它被允许在每次调用中被外部读取并携带 X-dependent 信息，则那次读取必须算作 observation bit（或更宽的通信），不能把它称作免费内部状态。

## 跨调用隐状态反例

一个 q=1 的环境单元可以在每次调用被覆写为隐藏串 X 的下一个 bit；调用者每次读取该单元并推进索引，L=0 也能在 m 次读取后完整恢复 m-bit X。这里不是 q=1 状态突破容量，而是发生了 m 个额外 X-dependent read observations。若合同只写“每次调用工作空间 q=1”却不写跨调用读写/迁移次数和接口宽度，容量结论不成立。

同样，序列化一个候选批的 wire payload 不是免费的：固定宽度 m-bit 候选、L 个候选、K 次调用至少产生 K·L·m 个候选payload bits（还需计 framing/address/error metadata）；写入、读取、解析和恢复的时间/峰值buffer必须进入资源账本。若保留完整 remote request log，它也是可再次读取的状态信道，不应被工作空间 q 抹掉。

## 严格边界

- `q` 限制的是某一调用间持久**内部**状态，不限制外部服务暗中保留的无限日志；后者须纳入可见通信或禁止。
- batch bit 与显式 state-read bit 是不同接口；把后者重命名为“state”不会使信息免费。
- 如果状态写入/迁移只能由 batch bit 决定且外部不可读，q 不改变 GVC-BATCH-1 的 F 界；如果迁移消息可携带 w 个 X-dependent bits，h 应替换为累计通信宽度 w，容量因子至多 2^w。
- 这是隐藏对象接口定理。已知明文输入的算法计算、SAT verifier 的常规输入访问、外部工具的服务计算均不自动落入此模型。

## 可核验证据

`probe_state_migration_v1.py` 标准库实现：

1. 对 N=1..8、K=0..3、L=0..3、h=0..2，完整枚举 batch-membership 与额外 binary observation 的合法自适应树，共 384 个最优值，与 `min(N,2^h F)` 全部一致。
2. 对 m=1..10 的全部 2^m 隐藏串，q=1 环境单元逐次读取 m 个 bit，2046/2046 完整恢复，作为“q 不等于累计通信预算”的负控。
3. 固定宽度 wire ABI 的 m=1..8、K,L=1..4 共 128 个账本案例通过；写入/读取/日志长度均精确为 K·L·m。

Generate-and-Verify资源闭包要求：在相同计费原语下串行模拟本地生成器、验证器及远端状态转移；总时间计各方实际步骤、wire读写/解析、路由和恢复，不仅是调用次数；峰值空间计同时存活的本地状态、远端持久状态、活动scratch、候选buffer和可读日志。冷启动/Build不得移出预算后再称同预算。纯内部store的dense q-bit无损固定长迁移若覆盖全部2^q状态，线长至少q；按单bit读写原语还需至少q次写和q次读。若采用地址引用、共享buffer或压缩，应以真实对象可达性/可恢复状态数重新计费，不能把复制公式无条件套用。固定Lm候选payload结论只针对本实验固定宽度显式传输ABI；流式生成不必同时保留Lm bits，却仍要支付完整传输，若API支持句柄/压缩则须另计解析或解引用成本。

脚本输出由清洁 `/run/current-system/sw/bin/python3` 运行；不使用网络、凭据、额外包或子代理。所有实验仅核验有限接口模型，不提供现实任务成功率。

全局 T1/T2/T3-v2 仍 UNRESOLVED。

## 冻结源码与实测输出
```python
#!/usr/bin/env python3
from functools import lru_cache
from itertools import combinations
import json

def f(k,l): return 1+sum(min(l,2**j) for j in range(k))
# Full exact optimization permits arbitrary extra binary observations
# interleaved with restricted batch-membership replies.
def opt(n,k,l,h):
 @lru_cache(None)
 def solve(mask,k,h):
  ids=[i for i in range(n) if mask>>i&1]
  if not ids: return 0
  best=1
  for z in range(1,len(ids)):
   for subset in combinations(ids,z):
    a=sum(1<<i for i in subset); b=mask^a
    if h: best=max(best,solve(a,k,h-1)+solve(b,k,h-1))
    if k and z<=l: best=max(best,solve(a,k-1,h)+solve(b,k-1,h))
  return best
 return solve((1<<n)-1,k,h)
checks=0
for n in range(1,9):
 for k in range(4):
  for l in range(4):
   for h in range(3):
    assert opt(n,k,l,h)==min(n,(2**h)*f(k,l)),(n,k,l,h)
    checks+=1
# 1 writable environment bit, repeatedly overwritten and explicitly read.
# Raw hidden input is not counted as that 1-bit work cell.
negative=0
for m in range(1,11):
 for x in range(1<<m):
  recovered=0
  for i in range(m):
   env_bit=(x>>i)&1
   # API read is an additional input-dependent bit transfer, NOT membership.
   recovered |= env_bit<<i
  assert recovered==x
  negative+=1
# A concrete fixed-width wire ABI and retained remote request log.
ledger_cases=0
for m in range(1,9):
 for k in range(1,5):
  for l in range(1,5):
   log=[]; writes=reads=0
   for turn in range(k):
    batch=[(turn+j)%(1<<m) for j in range(l)]
    wire=''.join(format(x,'0%db'%m) for x in batch)
    writes+=len(wire)
    parsed=[int(wire[j:j+m],2) for j in range(0,len(wire),m)]
    reads+=len(wire)
    assert parsed==batch
    log.append(wire)
   assert writes==reads==k*l*m
   assert sum(map(len,log))==k*l*m
   ledger_cases+=1
print(json.dumps({'ok':True,'interleaved_optimal_tree_cases':checks,'fixed_width_ledger_cases':ledger_cases,
 'one_bit_environment_full_recoveries':negative,
 'negative_control':'q=1 work cell, m additional reads, L=0: full recovery; q alone is not cumulative leakage',
 'limits':'finite hidden-object interface, no computational or empirical coverage claim'},sort_keys=True))
```
```json
{"fixed_width_ledger_cases": 128, "interleaved_optimal_tree_cases": 384, "limits": "finite hidden-object interface, no computational or empirical coverage claim", "negative_control": "q=1 work cell, m additional reads, L=0: full recovery; q alone is not cumulative leakage", "ok": true, "one_bit_environment_full_recoveries": 2046}
```
