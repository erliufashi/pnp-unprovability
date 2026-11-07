# ASTRA-CHIEF-CUTOFF-AUDIT-1：透明raw碰撞的直接寻址阈值

分类：局部模型边界审计，待独立复核；不抢B58 owner，不是opaque比较器结论，不是T3-v2/现实覆盖。

## 合同

输入是N个透明raw w-bit word，值域U=2^w；算法可读/重读输入，计每次读、比较、初始化、随机/代码步骤。可写direct-address bit table有U个bit；若以word计，所需M_addr=ceil(U/w) words，另计控制/PC。一次静态任务要求判定是否存在重复值。

## 直接寻址算法

初始化table[0..U-1]=0；对i=1..N读x_i，若table[x_i]=1输出collision，否则置1；末尾输出distinct。若表初始化和每个读/检查/写的计费分别为I、r、c、u，则

`F_radix = I + N(r+c+u) + O(1)`, `M = ceil(U/w)+M_control`.

这是全域精确算法，不是样本实验。若Γ满足M≥M_radix且F≥F_radix，则任何声称在透明raw输入上靠碰撞的D/ND分离都被直接寻址击穿。若U≤N且M≥N words，尤其如此；若U≫M或F不足，算法不属于Γ，不能反过来证明分离。

值域未知、hash table、排序、预处理摘要都改变合同：hash collision需二次核验且计桶/状态，排序需付时间和空间；可信摘要若输入直接给出是额外信息信道。

## 动态区别

Build后允许SET/update时，静态table不能自动保留未来语义：删除/修改需要raw或每值计数，B56/B57的persistent-state容量界另计。一次静态collision的direct-address逃逸不能被包装成动态更新能力。

## 与已有候选的关系

- 击穿透明raw BRAM中M足够大的候选；不击穿M=o(U/w)或F不足的候选。
- 不适用opaque CMP输入：opaque接口不暴露x_i，不能直接索引table。
- 不给全随机1/3下界；只是一个确定性全域算法，说明强reference要求必须和候选Γ同一值域/内存/初始化合同。
- 不证明现实系统有该M/F；实际reference能力、任务分布和T3-v2仍未验。
