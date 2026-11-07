# 来源账本（2026-11-04获取）

来源网页不可信；论文标题/搜索摘要声称“解决”不等于已核验。来源支持与本项目推导分开。未下载整份技术报告时，不声称已完整核对。

## S1：Aaronson，P ?= NP（综述2017状态）

URL：https://www.scottaaronson.com/papers/pnp.pdf
实际获取：fetch_content成功提取前100页；本轮阅读§3.1 pp26–28及BGS讨论p47。
工具记录：mw1z25h3noi3es；临时提取文件/tmp/pi-web-pdf/pnp.md并非稳定消费入口。
支持：P≠NP的Π2范式；标准公理独立性仍为问题；PA+所有真Π1的不可证性会有极接近多项式的infinitely-often算法后果；方法屏障不等于基础公理屏障。
限制：不能引用为已经证明ZFC独立性，也不能把其条件性算法结果换成所有长度正确的多项式算法。
短引（全来源摘引控制在90词内）：“these barriers indicate weaknesses in certain techniques, rather than in the foundations of mathematics.”

## S2：Stanford Encyclopedia of Philosophy，Provability Logic

URL：https://plato.stanford.edu/entries/logic-provability/
获取成功；工具记录mw1z25h3noi3es；阅读§1及§4.1。
支持：Hilbert–Bernays–Löb导出条件、对角引理、洛布定理及其证明。
限制：不支持任何P/NP不可证性新结论。
公式转述（不是逐字引文）：若T⊢(Prov_T(A)→A)，则T⊢A。本项目以所列公式和实际导出条件为准。

## S3：Aaronson，Is P Versus NP Formally Independent?（2003）

URL：https://www.scottaaronson.com/papers/indep.pdf
获取成功，21页；工具提取/tmp/pi-web-pdf/pnpdvi.md；阅读pp8、14–15及参考文献[6]。
支持：Hartmanis–Hopcroft表示依赖oracle独立性、表示无关oracle近邻；反思/洛布及PA+真Π1问题；Ben-David/Halevi技术报告线索。
限制：oracle中的相等不是标准相等；PP/多项式电路、统一时间和infinitely-often不能混用。
本项目notes/05独立重建first-proof版本；不是把原文证明逐字复述或声称新发现。
S1与S3同一作者，不能算两个独立数学权威的交叉验证。

## S4：Timothy Y. Chow，FOM邮件（2008-10-05）

URL：https://fomarchive.ugent.be/2008-October/013064.html
获取成功，工具记录mw1znhzgqca02g。
支持：转述Ben-David/Halevi Theorem4、PA_1=PA+所有真Π1、SAT到P的逼近率与Wainer层级的关系；指出“某些独立性方法自动提升到PA_1”的重要限定。
限制：二手转述，不代替原始报告定理定义和全部假设；其NP不包含于P/poly讨论不自动等于统一P≠NP。

## S5：Ben-David/Halevi原报告追踪（未取得全文）

作者目录：https://cs.uwaterloo.ca/~shai/pub.html （已获取，列Technion TR714,1992；旧综述另引用TR699,1991）
原PDF候选：https://cs.technion.ac.il/users/wwwb/cgi-bin/tr-get.cgi/1992/CS/CS0714.revised.pdf （HTTP404）
www域同路径：HTTP404。
转录镜像：https://paperzz.com/doc/8704044/on-the-independence-of-p-versus-np （HTTP403）。
相关问答：https://cstheory.stackexchange.com/questions/10044/implications-of-unprovability-of-p-neq-np （HTTP403）。
不修改网络/服务配置以绕过限制，不将搜索摘要冒充全文。下一次要引用精确双向定理，须取得原文或另一可靠完整版本。

## S6：Clay官方问题描述

URL：https://www.claymath.org/millennium/p-vs-np/
获取成功，mw1z25h3noi3es。支持标准问题语义及仍缺一般困难性证明的描述；不提供独立性定理。

## 排除的噪声

首轮带year过滤的宽搜索混入多篇自称P≠NP或ZFC独立性已解决的arXiv/Zenodo条目；不以平台、摘要或标题作为正确性认证。随后改为无年代过滤的实体检索并读取上述专家/原始资源。所有研究结论依赖明确公式与实际读取范围，不依赖那些搜索宣称。
