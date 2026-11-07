# h7实现/证明不能漏的点（未认证）

1. 给toy固定head从全部h∈F9、position word∈{−2,0,2}枚举φ像，得到Q_A/K_A；post/embedding闭包保证正常路径h仍F9。不是只采样prompt，字段源hash/config冻结。
2. 只有q只经σ(q,k)进入核、初值/primitive/树不依q时，完整raw score word签名相同才可共用状态。这是充分而非最粗等价；不要用sign或数值相近代替。
3. 对非空、无ERR的普通max，M_q从score像取。若max初值不是下界、μ含NaN语义或有ERROR，则不能无条件沿用“存在真实max leaf”的论证；需要另一证书。
4. 对每个q/m，只取score≤m的key生成(u, score=m)，把(0,false)及叶子在(⊕,OR)下做有限闭包。选true状态的z作Z_qm；它是所有B树/历史的过近似。实际m被选中时，必有至少一条real max leaf。
5. 证书是selected范围：D[q,m]在m当前未被选择时可以落在Z之外。例T域q=3,m=−4,key=−2使score=−3、u=3、counterfactual D=3，而该m的selected Z可能仅{2,4}；实际m=−3的Read仍正常。不能据此误报或丢状态。
6. Empty Read按reference初值单独返回0；非empty才可删empty-only参数。Push继续为所有保留(q,m,z)更新，不以running max/den替代固定参数。counterfactual异常仍隔离。
7. pruned cache需兼容append/query/count/parameters/shape，使用冻结forest primitive；模型ctor不要先分配完整表再替换，以免把full-table启动峰值藏掉。
8. 构造静态certificate一次、只读复用，不让输入/观察trace更新它。计readonly分类器/元数据bytes和静态枚举复杂度；小toy减少工作槽不代表实际200B可行。
9. 不安全负控制：同号query q=1与q=2在history[(-2,-4),(2,4)]的核输出可为0与4；只保留observed q=0后对新query默认0同样没有覆盖证明。
10. zero-key K={0}是合并控制例，可令全部query同签名，但它只是结构控制，不用来挑弱baseline宣称human任务覆盖。M17检索族query签名应两两不同，所以剪枝不反驳其下界。
11. 全KV/全表/pruned在被动test harness逐步比较，生产stream无observer、不保存输出历史。报告actual K及仍没满足的预算，不强行说内存必胜。

原T3、原35节点、已认证研究文件不修改；h7若发现反例应留最小reproducer和未解点，不伪造成功。
