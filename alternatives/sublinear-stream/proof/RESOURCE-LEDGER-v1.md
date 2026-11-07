# 资源账本：当前、峰值与交叉点不能混同

状态：指定toy构造的逻辑数值槽分析与重放，待独立复核；不是实际200B/RSS/所有编译器的下界。

## 1. 范围和单位

冻结hour4实例有4个head，每头999参数森林，K=3996。位置t指已处理prompt/feedback token数，seed-inclusive长度L=t+1。

两个抽象布局的数值组件：

R(t)=8t（reference每头每位置一个key、一个value）；
A(t)=K·bit_length(t+1)（森林按层分配的逻辑数值槽）；
C(t)=K·popcount(t+1)（当前非空数值槽）。

这不是Python容器完整capacity/RSS；R是具体未压缩KV布局，不是最优编码下界。A含未占用层槽，C不含；code/权重、控制/RNG、临时carry、输入/输出缓冲另计。真实物理预算必须补齐账本，不能把一个组件的比值当整个设备比值。

## 2. 运行peak live的精确表达

对t之前所有稳定前缀，最大popcount为floor(log2(t+2))：令h为此数，2^h−1≤t+1，故可达到h个1；任何h+1个1的正整数至少2^(h+1)−1>t+1，故不能超过。

因此这个cache-array组件的运行peak为：

P(t)=K·floor(log2(t+2))。

源实现一条记录更新时，per-parameter低层先清掉再写carry；数组中的live数不超过旧/新稳定块数最大值。不同head暂时处于相邻前缀，也不超过全运行最大popcount；该最大值又在某个所有head同步的前缀达到。故post-feed重放可捕获这一cache-array峰值。临时carry/宿主allocator等仍不是此指标的一部分。

A单调增长，最终A也是该逻辑容量峰值；当前C则会上下跳，不能拿最后一刻当全程峰值。

## 3. 本批重放

同一128-token prompt、6步det生成实例结束于t=134，实际逐步重放得到：

reference KV组件峰值1072 word；
compiled逻辑分配峰值31968槽；
compiled当前live15984 word；
compiled post-feed cache live峰值27972 word。

分配组件比reference约29.8209倍。这不是声称总设备内存该倍数，更不是声称实际优化：在这个尺寸下该构造确实更大。数据与完整trace在adequacy-probe报告，冻结源hash单列。

## 4. allocated交叉点的全局证明方式

固定h=bit_length(t+1)，区间为2^(h−1)−1≤t≤2^h−2，A=Kh。区间内A≤8t当且仅当t≥ceil(Kh/8)。

枚举有限几个h找到首个整个区间从左端就满足的h0，并检查所有此前区间，就能得到精确首个和永久交叉点。不是扫描很多t后声称无限成立。

为什么以后也成立：区间左端a_h=2^(h−1)−1满足a_{h+1}=2a_h+1。若8a_h≥Kh且h≥1，则8a_{h+1}≥2Kh+8≥K(h+1)，故归纳覆盖所有以后区间。

本K=3996时：h=13的部分区间阈值6494；h=14左端8191已全满足，故首次及永久allocated交叉都为t=6494。

## 5. peak live和instant live的区别

P=Kh的区间为2^h−2≤t≤2^(h+1)−3，左端递推为a_{h+1}=2a_h+2，使用同一归纳法。此实例首次及永久peak-live交叉为5994，h0=13（左端8190）以后全满足。

当前C≤A，所以在allocated永久阈值以后必满足C≤R；在阈值以下完整有限检查即可找精确当前live的首次/最后失败。结果：首次为511，512立即又失败，直到5119之后才永久满足。

所以只挑2幂长度附近的低live数量，会把“偶然当前更小”误称“全程或以后更小”。三种阈值回答不同问题，都不等于物理RSS交叉点。

## 6. 功能等价并不自动保任何预算

作为明确的合成observer，给numeric cache-array peak设B=2048 word，并把超限返回记为BUDGET_FAIL。上述实例reference peak1072≤B，而compiled peak27972>B；功能输出完全相同，但resource-status law为两个不同点质量，TV=1，失败损失差为1。

这是根据指定组件指标构造的逻辑反例：没有真的强制OS失败，B不是用户已采纳阈值，也不是人类基准。它只反驳“word/law相同自动满足任何resource-sensitive任务”。

## 7. 不可外推的结论

- 这个构造差，不证明不存在更好的profile-specific编译器。
- 所给资源上界/槽数不是所有模拟器的下界；需要另证才可谈不可避免性。
- 不反推旧原生固定profile的T3模拟不成立。
- 真实模型的常数、权重/程序驻留、workspace、RNG、I/O、数据类型及墙钟未测；κ/c或硬预算必须独立指定。
