# 最新：v2恢复研究 checkpoint（2026-11-06 20:26）

本节优先于下方19:37历史交回：chief已明确数据阻塞只挡正现实覆盖认证，本轮已据此恢复并完成两项新模型研究，而非继续等200B包。固定截止仍01:29:04；未续期，未启动代理。

## 新的实际动作

核current-contract-v2，claim原mail身份、roster、refresh/next。E-chief-cert-1由sol-c先占用，避开后claim E-chief-dom-1；完成并publish后next无空闲叶，自主创建A57→M22，完成并publish。自己的租约都已结束。最近board check通过23节点25边round26；next无未占用eligible叶（chief-compose及PPST由chief/sol-b持有）。旧文件与已发布源码不改。

### 1. E-chief-dom-1：自然可执行强表达模型与正包含候选

状态done/proved-candidate，未独立验收。

- 自己cwd文件：`E-chief-dom-1-native-reference-v1.md`、`bounded_vm_v1.py`、`bounded-vm-self-test-v1.json`。
- 不可变共享证据：`evidence/E-chief-dom-1/1388c00ed1ec9cc2e5ffcb16bf915afc47dcb9177862091821b9bd5135f7be4f.md`，内嵌完整源码和测试。
- BRAM候选：固定字宽、fuel、代码/初始化data字节、可写内存、输出预算；支持随机访问重读输入、付费只读数据、可写外存、一般算术/循环。初始化、代码fetch、各类读写、固定精度乘法全部有显式账本。宿主Python资源不冒称等于VM抽象计数。
- 精确原生包含：SUM所有合法输入恰7n+9步；DOT恰11n+10步。任意合法原生reference取自身作为策略时，轨迹/所有计数完全一致。不是只由一个成功样本推出全域。
- 普通k带位TM的构造性包含：H步机器可编译为P_H+c_R(H+1)步、k(2H+1)+b_R工作word；字宽、输入转换、代码与数据、初始化全部收费。是付费多项式开销构造，不声称保原空间或同精确预算；未调用未经核原始模型的层级定理。
- 无slack反例：实际SUM输入[3,2,3,5]恰30步；29fuel因最终HALT未执行而失败。不是全类29步函数下界。
- 19项规范测试通过，含256组4-bit求和穷举、code/data预算拒绝、重读外存与输出边界。

### 2. A57：同模型收费ND严格分离，同时否决其现实覆盖适格性

状态done/proved-candidate，未独立验收。

- 文件：`A57-spec-v1.json`、`A57-paid-OR-separation-v1.md`、`bounded_vm_nd_v1.py`、`paid_certificate_or_v1.py`、`paid-certificate-or-test-v1.json`。
- 不可变共享证据：`evidence/A57/c06631756405738ffadd6b9a51053470f0b88297495654e04c6082c88006c673.md`，内嵌完整源码/输出。
- BRAM只增加一次生成1bit并正常计fuel的GUESSBIT。地址见证逐bit生成并打包，真实代码循环w轮，共6w+2步，存于已计16w寄存器；验证≤10步。无免费只读证明带、无重猜一致性漏洞。
- 同Γ：w=ceil log2(n+2)、F=6w+12、B=512字节、M=0、O=1。n≥128时，ND_OR在Γ内精确计算OR；任意D程序即使有任意input-independent advice，也至少需要n次输入bit读取，因此不在相同F内。证明用全零/未读位置翻转不可区分性。
- 随机化界：若每实例误差≤ε且至多q次数据查询，则q≥n(1−2ε)。ND存在性不等于实际随机猜测成功率或高效确定性找证据。
- 511输入、16352见证路径检查通过，包含所有无效/最大证书地址及全零soundness。
- **关键否决**：该O(log n)fuel不能包含全输入SUM。若改Γ以包含原生SUM的7n+9步且B≥204，D-OR_SCAN最坏7n+8步已可解OR。故这个易证分离不能充当“强现实能力+同模型严格分离”联合验收，只是明确模型诊断结果。

### 3. 补充边界验收

未改冻结v1文件；新增`check_paid_or_boundaries_v1.py`及`paid-or-boundary-test-v1.json`。在`/tmp`、`env -i`、仅普通Python PATH下，从绝对脚本路径执行，264项字宽跨界/最高地址/最大证明值/实际n≥128燃料关系检查通过（n从16到4095）。这是本地补充规范证据，非新增shared-board结论，非现实能力认证。

复现（研究产物，不是已安装应用）：

```sh
cd /home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z/workers/pnp-sol-a
/run/current-system/sw/bin/python3 bounded_vm_v1.py --self-test
/run/current-system/sw/bin/python3 paid_certificate_or_v1.py
/run/current-system/sw/bin/python3 check_paid_or_boundaries_v1.py
```

## 独立核对与下一缺失引理

已将两个增量notice发chief；另向sol-c发单owner request `20261106T122352Z-pnp-sol-a-a57-nd-or-6w-12-2858cb`，请求核A57的同Γ计费/严格分离证明，未冒称已验收。

当前模型研究缺口已不是“等实测数据”：具体是**在足以包含全输入/强reference的Γ内，取得不靠sublinear输入访问弱化的同模型全类分离**。本轮收费BRAM包含与失败OR候选精确定位此问题；PPST原模型审计由sol-b持有，compose由chief持有，未复制它们的同一任务。真实分布与数字Γ仍另缺数据，但不把它们当整个定义研究都不能行动的理由。

标准T1/T2以及T3-v2全局均UNRESOLVED；没有宣布新现实覆盖、标准P/NP分离或指定侧ZFC不可证性通过。

---

# 以下保留上一轮历史checkpoint
