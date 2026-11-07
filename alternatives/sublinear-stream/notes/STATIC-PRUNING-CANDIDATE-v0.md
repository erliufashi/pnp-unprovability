# 下一候选：带证书的profile-specific参数剪枝（v0，未认证）

M17最坏检索族限制普遍小模型系数编译，但没有否定某个具体profile的特殊结构。下一步应找可证明的结构，而不是从下界宣布所有实际模型都差。

## 静态域，不是观测域

对固定head，证明所有实际query在Q_A、key在K_A。toy可枚举其有限hidden/position word输入的全部组合，得到保守φ像；这是code/domain分析，不是只收集有限prompt中出现的q。

若q只通过score σ(q,k)影响kernel，primitive/初值/参考树同一，则原始score word签名(σ(q,k))_{k∈K_A}相同的query可安全共用参数状态。这个条件充分，不宣称是最粗行为等价；不同签名可能归一化后仍等价，但未证就不合并。

## selected-parameter证书

nonempty历史且μ为无错误的普通max、初值低于所有score时，实际max m来自score像。对每个q/m，可只保留已证明覆盖实际最终den的Z_qm。

关键不是要求D[q,m]在所有counterfactual历史中都属于Z_qm，而是：如果查询实际选择了这个m，则最终z必须属于Z_qm。其他m下的D可取别的word，不会被当前查询读取。

一个保守构造：仅取σ(q,k)≤m的key，生成叶子(u, seen_equal)，其中seen_equal表示score=m。把seed(0,false)及这些叶子闭包到有限状态Ω×{false,true}，合并为(⊕,OR)。实际m为max时至少有一条real leaf相等，故root flag=true；取所有true状态的z即可安全覆盖。它对任意binary树过近似，不靠⊕结合律。

empty query需单独返回声明的init结果，不能凭非空max论证把seed-only状态删掉。

## 预计成本与必须承认的边界

K_pruned=|query classes| + Σ_q |M_q| + Σ_q,m |Z_qm|r，forest再乘log t。仍需计readonly证书/分类器、静态分析成本，不能把Ω^d枚举说成实际200B可用。

retrieval族的query签名应两两不同（取key=q即可区分），故不能借此消除M17的最坏指数。这是特殊结构优化，不与下界冲突。

## 下一批次MVP

1. 给完整的条件性剪枝正确性证明及toy静态证书生成/检查规则。
2. 固定toy2层2头上比较full-KV/full-table/pruned每步输出与RNG，记录actual K降低及仍未满足的预算，不强行说更省实际设备内存。
3. 给只按观测q/同号score等不安全规则的明确反例。raw score相近不等于word相同；若用近似合并须另有hour5质量证明。
4. 不改旧T3或任何原35节点；没有证书的模型变化不得自动沿用剪枝。
