# h9候选：数值state预算下的有限INDEX见证（未认证）

fixed-H审计说明Big-O可隐藏巨大常数。最后一个研究批次可把state预算s固定为实际数值，而不是再造只在无限远分离的类。

## 独立、可自含证明的候选

public m固定，输入x∈{0,1}^m后才给late query j。read-once、answer-only after EOF、read-only模型独立x；prefix边界所有输入相关状态（PC/时钟/地址/RNG/可回读日志等）总共≤s bits。

- exact deterministic若m>s则INDEX_m不能全对：2^m前缀只有2^s状态，collision在某j答案不同。无限ROM不帮忙，ROM地址/控制若编码x也要计state。
- uniform X/J、平均error≤1/3时，独立重推链式entropy/Fano得s≥(1−h2(1/3))m。不要把此处平均保证直接当真实任务分布保证。
- c=1−h2(1/3)=5/3−log2 3 >1/16，可由精确整数3^48<2^77证明。所以m=16s+1是保守、无浮点依赖的随机见证阈值；最优系数约12.239仅作数值信息。

ND预先猜j，扫描时仅保留该位，最后比较late query，可用8ceil(log2(m+1))+64 bits的显式寄存器/控制预算（须给计费规范，不把Python宿主RAM当该数）。当这个上界≤s时形成同一数值预算下确定性/非确定性分离。时间仍poly(m)。这不是标准P/NP；应命名D_s/ND_s再解释对应受限模型。

## 必须保留的解释

若m超过reference的实际context/任务输入范围，仍只是外域见证。要保证存在within C的hard case，需阈值m≤C；若不满足只能说这个下界不给范围内证书，不能推出范围内易。

baseline已被类覆盖的任务子集里不能再放一个该类做不了的见证。没有量化reference实际state/human能力，不宣布新充分性或改T3。

## h9 MVP建议

E44 exact有限budget/collision；E45 randomized entropy与精确1/16安全系数；E46 ND协议/有限枚举和budget/context阈值账本。各叶自含证明/实验，不以M17作同层前提。

source/proof/报告全部新建，不改旧35或前8小时；优先在09:00前完成/复核，09:17:58绝对停止，不为新候选续期。若时间不足就保留明确未决项而不赶造通过。
