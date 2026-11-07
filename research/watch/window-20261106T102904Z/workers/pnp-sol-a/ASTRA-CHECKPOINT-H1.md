# Astra checkpoint H1 — Yao/public-multiset BRAM audit

时间：2026-11-06 23:47 +08；身份 pnp-sol-a；当前板截止仍为 2026-11-07 01:29:04 +08（不把用户所述04:00扩展为本窗口授权）。

## 节点与动作
- 读取 ACTIVE、state、TEAM-CONTRACT-v1、current-contract-v2；按 board `next` 选择并 claim `A-H3-YAO-PROMISE-1`，未重复 chief pair-sampling。
- 运行 `yao_public_multiset_probe_v1.py`，输出 `astra-yao-public-multiset-result-v1.json`。
- 该候选是公开可重读输入上的 SUM_DIFF 字节码：在 promise（输入是 permutation 或单次 replacement）上精确分类；不是一般 ED 算法，也不是随机化算法。

## 可核对结果
- 穷举 permutations：152；single replacements：2728；均通过 promise 分类。
- 程序源码 canonical bytes=217，sha256=`40b743da5b93c2af9376114d0f43ce3f1e8f484a37e011c44722433f67fd2d55`；VM sha256=`a6361e8f0f9299d80b8861b91b70fe236181d852541ab7ed6027a82b81282a41`。
- fullscale n=128,255,256,1024,4095 均通过：w=15,16,17,21,24；寄存器 bits=240,256,272,336,384；array bits=165,240,272,672,1512；随机带=0；初始化+获取预留步=156,287,289,1073,4175；总步=1190,2337,2347,9275,36945，均低于 F=32n+512；charged input reads=258,512,514,2050,8192。
- 每个 n 都构造 equal-sum 的非-promise collision，算法输出 0，明确显示该算法不是 worst-case ED 解法。

## Yao/下界判定
此构造反驳“permutation-vs-single-replacement 分布自动给全类 ED 下界”的直接迁移：公开 multiset/总和信息可在同预算中区分该 promise。它不提供 distributional lower bound，也不反驳一般 ED 的 BPP/BRAM 下界；仅说明该 hard distribution 候选过窄。要得到常数 1/3 下界，仍缺能覆盖合法输入族的 Yao 分布及对每个固定随机带的 BRAM transcript/状态计数证明。BSSV 高置信错误条件不能免费降为 1/3；前一份 `RAND-ED-H2-source-audit-v2.md` 的限定结论保持不变。

## 资源与状态
完整账本计入 16 个寄存器、数组、初始化、输入读取、源码描述字节；该程序不使用随机带。分类：`counterexample`（反驳候选分布迁移），不是 T3-v2、现实覆盖或标准 P/NP 结论。共享板发布应以事务 CLI 完成；旧104及旧证明只读。
