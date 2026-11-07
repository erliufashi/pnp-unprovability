# Astra D H1 — D-GVC-BATCH extension: retries, environment state, and total-cost closure

**Identity:** `astra-d`  
**Scope:** extension of `D-GVC-BATCH-1`; not a restatement of its `F(K,L)` formula.  
**Classification:** counterexample plus conditional closure lemma; local interface result only. T1/T2/T3-v2 remain unresolved.

## Claim

The batch capacity is not compositional under retries unless retry outcomes, environment state, and their costs are explicit resources. Let a run have a finite set of *answer-relevant transcript symbols* per attempt: membership bit, timeout/retry outcome, and any readable environment-state word. If the total number of reachable, answer-dependent transcripts after all attempts is `T`, then exact recovery can cover at most `T` hypotheses (or the sum of the `T` largest prior masses). This is a transcript-counting bound, not `F(K,L)` with retries silently inserted.

A useful closure condition is: every retry is charged a worst-case cost `c_retry` (including rollback/replay), every candidate costs `c_cand` for generation + serialization + verification + parsing, every environment read/write exposes at most `w` answer-dependent bits and costs `c_env`, and total cost is at most `W`. If `r` retries and `C` candidates are used, then

`C*c_cand + r*c_retry + n_env*c_env + fixed <= W`,

`wire(C)+state_migration <= U`, and the transcript capacity is bounded by

`min(N, 2^h F(K,L))`,

where `h` is the *total counted width* of environment/retry/status observations, not merely persistent-state width. This bound is valid only when state updates are functions of already-counted replies and the environment has no hidden readable log.

## Strict counterexample: retry and environment state are not free

Take `N=2^m`, `K=0`, `L=0`, and a one-bit environment cell. The service overwrites the cell with successive bits of hidden `X`; each retry reads the cell and advances an index. With `m` retries, exact recovery succeeds for every `X`, despite `F(0,L)=1` and one-bit persistent state. Thus the old batch formula is not an upper bound once retries expose `m` answer-dependent reads: the true transcript has `2^m` states. Calling these operations “retries” or “q=1 state” does not remove their communication.

Now impose total budget `W < m*c_retry + m*c_env`; the same interface cannot complete the recovery. Therefore the pair `(K,L)` does not determine capacity even with identical one-bit feedback: one implementation fits the budget, another does not. A timeout/retry bit is itself an additional observation; if timeout behavior depends on `X`, it contributes another transcript branch and must be counted (or prohibited by a fixed-time contract).

## Strict cost counterexample: positive verification path

For `K=1,L=2`, let candidate A reject in one unit while candidate B requires `R` units to verify when correct; serialization costs `m` bits each and wire budget is `U=m`. Formal batch capacity says three distinguishable recoveries (`F(1,2)=3`), but only one candidate fits the wire budget and a correct B path violates time whenever `W < R+2m`. The feasible capacity is therefore at most the one-candidate interface, regardless of the nominal `L=2`. Retry-on-timeout cannot repair this: it either exceeds `W` or adds an observable timeout branch that changes the transcript model.

## Proof sketch / audit rule

Fix all random coins and all answer-independent scheduling. Each feasible execution maps `X` to a leaf labelled by its complete readable transcript (feedback, retry/timeout result, environment reads, and state/log reads). Two hypotheses reaching the same leaf cannot both be uniquely output, so correctness is bounded by the number of reachable answer-dependent leaves. If environment communication width totals `h`, at most `2^h` environment transcripts multiply the batch-tree bound; if retry outcomes are ternary or variable-length, use their actual transcript alphabet/product, not a binary multiplier. Cost feasibility then restricts the set of leaves further; it never increases it. Averaging over independent random coins gives the same prior-mass bound.

## Novelty / nonduplication

`D-GVC-BATCH-1` counts fixed K batch-membership bits and candidate-set size. `D-GVC-STATE-1` counts q-bit internal persistence plus separately declared binary observations. `D-GVC-COST-1` charges verifier and wire costs. This extension adds the missing *retry semantics*: retries may be (a) answer-independent schedule repetitions, which only consume budget and do not increase transcript capacity, or (b) answer-dependent timeout/error/environment events, which increase the observation alphabet and invalidate an unmodified `F` curve. The practical closure rule is therefore a two-part gate: **count every readable retry/environment transcript and prove every leaf fits worst-case total cost**.

## Limits

This is not a real-distribution coverage result, not a standard P/NP theorem, and not evidence that any deployed verifier has the stated hidden-state behavior. No old evidence was modified.
