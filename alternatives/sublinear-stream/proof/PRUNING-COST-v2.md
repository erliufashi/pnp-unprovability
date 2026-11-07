# 特化的成本、域依据与不安全规则审计

状态：本批具体构造审计，待独立复核；不声称最优、实际200B或全设备内存优势。

## 1. 这个静态域为什么不是样本域

冻结toy的qkv程序只读h、position word与固定6系数。position_word(p)的周期为3，像恰为{−2,0,2}，程序枚举全部h∈F9和p=1,2,3共27组合，而不是观察prompt输出。

正常有效路径的hidden在F9：输入/反馈token在有限F9；φ的乘加对F9输入总返回F9；每头max为真实最大score、exp(0)>0，normalizer树只加非负word且保留正项，所以所选den非0。后续除/乘/加在这些有限正常输入下不抛异常，head输出仍F9，post乘加也在F9。逐层/位置归纳得到整个域闭包。空/非法输入走固定有限guard而不是生成未声明query。

这给toy的保守域证书；不声称精确可达性或任意profile都能如此高效分析。版本/权重/primitive改变必须重编证书。

## 2. 实际数值状态结果

完整表每模型3996参数森林。静态特化后toy-A为752、toy-B为776。每个retained森林按参考B树保留同样level shape，故状态系数按实际保留数改变。

在同一t=134长例：

| 模型 | 完整表allocated | 特化allocated | 特化当前live | 原KV word |
|---|---:|---:|---:|---:|
| toy-A | 31968 | 6016 | 3008 | 1072 |
| toy-B | 31968 | 6208 | 3104 | 1072 |

这确实降低了完整表系数，但特化组件在该范围仍大于原KV。当前live不是peak；按同shape账本推导的post-feed peak为752×7=5264、776×7=5432，而非3008/3104。这里是数值槽/word口径，不是RSS或整个pipeline峰值。

constructor直接分配特化表，未先分配3996完整表再替换后只报末态。test harness另有完整表对照实例，其内存不能归入特化solver。

## 3. metadata和编译成本不能隐藏

两个profile证书的各自JSON序列化大小约25146/25503 bytes（以本次实际report为准），包含闭包证明及分类信息；它们合存于报告引用的证书artifact。这不是Python对象驻留，也不是最小runtime metadata。

query到代表、m/z offsets、源码/配置绑定均为只读模型资料，物理部署需计费。静态枚举可能对b/d指数大；toy .007秒量级不外推200B。若实际cold start把编译也算在任务预算里，不能只报warm kernel状态。

## 4. 必要负控制

- 同号query不保证score word相同：history[(-2,-4),(2,4)]中q=1与q=2的参考输出为0与4。若按sign合并会出错。
- 只保留观察到的q=0后对新q=2默认0，没有覆盖证据；单record[(-2,2)]的参考输出是2。这个例是kernel product-domain控制，不声称真实训练模型已出现该激活。
- 不能把selected Z误当所有D状态范围：q=3、inactive m=−4时某前缀D=3，而该m的selected Z={2,4}；实际Read选另一m仍正确。

zero-key K={0}控制让9个query同签名，仅需4森林，7380个小前缀query对照通过。它是合并规则控制，不用来选择弱human baseline。

## 5. 与下界兼容

M17检索族对q1≠q2取key=q1，score已不同；小d签名验证为2/4/8/16全异，且一般选择key的证明对所有d成立。原始签名是安全但非最大商，本文未声称任何行为等价类都无法再缩；retrieval的不同输出payload另有Ω(2^d)信息下界。

model-specific优化不能反驳generic最坏族下界，最坏族下界也不能否定用户某个baseline有特殊结构。

## 6. 测试和认证口径

本批运行完整KV、完整表、特化三条独立状态路径，按相同输入/随机序列逐步比较head qkv、输出、hidden、临时计数和RNG；分类/闭包metadata只读且实验前后hash一致。

有限结果及typed certificate的数学正确性分开。没有测实际200B、没有证明元数据/静态分析多项式模型开销、没有声称满足用户未指定的κ/预算，更不扩大现有T3或标准P/NP结论。
