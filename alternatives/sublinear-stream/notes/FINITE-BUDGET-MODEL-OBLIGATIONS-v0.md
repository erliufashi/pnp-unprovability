# h9模型/计费约定候选（未认证）

为避免把有限budget混成标准空间类，先固定public m，b=ceil(log2(m+1))。U_m为m个payload bit、b个late-query bit与EOF，query<m；它是声明的有限任务宇宙。

若扩展为全字符串语言，无效长度可在读到第m+b+1个符号时早拒绝（仅有效输入承诺EOF后答案）。不能一边要求所有非法无限长输入也必须EOF后答，一边把无界物理input cursor放进固定s而不解释。可选择只作U_m任务，不冒称全域同一API。

所有影响future的state都计，包括ROM地址/PC、input cursor、时钟/RNG、可回读输出/log。没有外部payload副本或可读任意精度wallclock。模型/ROM固定于m但独立x，不能藏run答案。

ND的候选显式预算：I/J/Q/L四个b-bit语义register；input cursor最多m+b+1，可用2b bits；两个b-bit scratch（位级比较/进位/局部索引）；64 bits留固定PC/phase/flag/token，共8b+64。须证明这些寄存器足够、没有未计微码栈；Python只模拟logical machine，不能称其RSS只有这个数。

先guess b-bit J，扫描x仅取x_J，读late query Q，EOF时Q=J且选中位1才accept。无效guess不能accept；不会把harness的expected x_j喂回程序。

exact预算候选m=s+1；random γ1/3保守候选m=16s+1（3^48<2^77）。均须检查ND预算≤s，不对所有小s默认成立。随机证明自含entropy/Fano；浮点c≈.0817仅信息，不是精确证据。

within-context条件m≤C只给此下界的足够见证阈值；失败不推出域内所有任务容易。baseline state cap、实际context、人类adequacy均未测，不改T3。
