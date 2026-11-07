# selected参数证书下的精确特化

状态：本批条件性编译工具，待独立复核；不自动涵盖任意model，不改T3。参考为既有纯word/同一树的参数森林，query仅通过score进入attention，value不依未来query。

## 1. 证书而非观察清单

对有效工作域证明query∈Q_A、key∈K_A。证书与reference/profile/primitive/初值/树的版本绑定，不从有限prompt出现过的q推断未来域。

若q1/q2对每个k∈K_A有完全相同的score word，且其余primitive、初值及树不依query，则二者在任意同一历史上的score叶相同，继而M/D/A对应所有叶与根相同，可用同一代表c。

这只是安全充分条件，不声称是最粗行为等价。不同raw score签名也许归一化后等价，但未经额外证明不能合并；同号/数值接近不等于word相同。

## 2. selected参数条件

为每个代表c给有限M_c及每个m∈M_c的Z_cm，要求对所有有效非空历史H：

M_ref(H,c)∈M_c；若m=M_ref(H,c)，则D_ref(H,c,m)∈Z_cm。

这是条件于m真正被Read选择的范围，不要求每个counterfactual D(H,c,m)在所有历史都落在Z_cm。值存储仍用整个word域Ω，不把其编码截成Z的枚举索引。

empty Read另按reference初值语义处理；本核返回0，不用非空max结论误删其必要状态。query超出Q_A/keys超出K_A不属于证书承诺，不能悄悄默认0并称仍有覆盖。

## 3. 投影算法及正确性

只保留：每个代表的M森林；每个(c,m)的D森林；每个(c,m,z,通道)的A森林，m/z在证书集合内。Push仍为所有保留参数追加字面叶子，使用相同primitive/seed/参考树，不用running max/den替代固定m/z。

按历史长度归纳，每个保留森林等于完整参数算法的同名森林：初值相同，单元更新只依自身、当前record及固定参数，不读被删单元；forest块组合也相同。counterfactual计算采用totalized error，不全局抛异常。

Read时，将实际query映到score签名代表。签名证明使参考输出不变。非空时实际m与最终z由证书保证在保留索引中，对应根与完整算法相同，所以所有输出word相同。empty则用同一显式空语义。

特别地，某个未被选m的D根跑出Z不是不变量违反，不能据此删其更新或报全局错误。

## 4. toy静态证书的一个充分构造

冻结toy profile的φ仅读h∈F9和position word∈{−2,0,2}。枚举全部27组合取q/k/v像，是代码的保守像而非样本域。embedding/post/正常kernel闭包使有效路径hidden仍在F9，position程序对所有位置都在该三值集。

这里σ=toy乘法，score无ERR；μ是普通max，初值LOW≤全部score。对非空历史，实际m属于S_c={σ(c,k):k∈K_A}，且至少有一条real key的score=m、其余score≤m。因此可取M_c=S_c。

对每个c/m，仅用score≤m的key生成有限leaf状态(u,score=m)，u=E(score⊖m)。加seed(0,false)，在如下操作下取有限最小闭包：

(z1,b1) ⊙ (z2,b2) = (z1⊕z2, b1 OR b2)。

参考树的每个子树状态在闭包中；实际m被选择时root flag=true。故Z_cm可取闭包中所有true状态的z。这对任意binary树是安全过近似，不依赖数值加法结合律，也不声称最小集合。

max有NaN/不同seed、输入可能ERROR或primitive不同，不能直接套这个构造；须另给证书。普通max与LOW下界也不可省略，否则seed可能主导而没有real max leaf。

## 5. 典型易错情形

toy q=3、m=−4，单key=−2使score=−3，counterfactual exp(score−m)=3，D(H,q,m)=3；该m的selected Z可能只有{2,4}。实际max是−3，Read选择它的有效den，仍正确。这说明证书不是所有counterfactual状态的范围。

若只保存观测q或按score sign合并，没有上述全域证据就不保证正确。对应负控制属于本批实验。

## 6. 成本和能力边界

若代表集为C，则保留森林数：

K'=|C|+Σ_c|M_c|+Σ_c,m|Z_cm|r。

在B森林中数值工作位可界O(K' b log(t+2))，另计当前record、控制。分类器/证书/域描述为只读模型元数据，也需要物理存储；不能因为不在工作带复杂性中就当设备免费。

静态枚举Q/K或完整hidden字母表可能对精度/宽度指数大。本工具未证明模型规模高效，也未测真实200B。runtime ctor应只分配特化表，不能先分配完整表再替换后只报告最终峰值。

M17的equality检索族对q1≠q2取key=q1就有不同score，所以此签名规则不会合并全部指数query。这是特殊结构优化，不反驳最坏族下界，不否定某个实际baseline。

若把本精确kernel放入M15条件性控制器且域证书对全部实际q/k成立，原word/输出RNG耦合保持；完整API硬件预算仍不是自动推论。
