# 数值state见证的范围账本

本组针对固定public m、有限U_m与逻辑保留配置容量，不冒称标准P/NP、实际Python RAM、真实200B或人类覆盖。

## 单位澄清保留版本

SEPARATION/RANDOM-v1保留首次引用字节；v2仅将C澄清为payload范围C_x或完整data-bit容量C_wire，没有新数学定理。完整数据有m+b个bit symbol，EOF是另一个协议事件；若有头部/传输编码还须另付。

例如s128的exact见证m129、b8、ND编码128：payload范围129可容纳m，但完整data容量129不容纳137个data bit。不能因前者fit就说实际模型context fit。

## 模型与实际部署

8b+64是声明寄存器/有限转移模型的保留配置编码上界；源码的encoder/round-trip验证这个逻辑对象，Python宿主、模拟所有ND分支、SHA诊断和expected payload属于被动harness。不声称CPython进程只有这些bits。

若想从硬件资源预算得到结论，必须把所有实际输入相关可回读信息编码进s，包括PC/地址、RNG、缓存/日志/adapter、可观测时钟。若假设不成立，不能套容量下界。

## 精确、随机与ND别混

m>s给D_s exact失败。m16s+1给R_s在均匀X/I下平均error不能≤1/3；平均并非真实任务分布的测量。ND编码fit是另一个条件，上界未fit不证明ND不能。

固定ROM独立本次x/j允许很大，但选择ROM地址或可修改权重若保存本次x的信息也须计state。早知query、二次读取原input、外部memory或任意精度可读时间均是另一协议，不属于本见证模型。

## 与研究目标的关系

这些阈值使常数和见证大小可检查，比只写Big-O多一些操作信息；仍不能把超context的反例说成人类相关范围内难题。是否存在更小见证、实际baseline的s/C、风险分布及human能力均未确定。

原T3保持限定代理结论；标准P/NP与ZFC不可证性仍UNRESOLVED。后续若要加强终止条件，应先选共同任务宇宙/数值资源/大小范围，再验收，不在本批暗改。
