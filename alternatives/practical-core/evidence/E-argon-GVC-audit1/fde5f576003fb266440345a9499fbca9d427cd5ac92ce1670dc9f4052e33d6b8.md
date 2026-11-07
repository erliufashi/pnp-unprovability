# E-argon-GVC-audit1 — Conditional retry amplification, live resources and feedback units

pnp-sol-c, 2026-11-06. Classification: local conditional lemmas and counterexamples, not practical coverage or standard P/NP success.

## 1. The valid amplification hypothesis
Fix an input/task and a single executable generator-verifier policy. Trial i runs only while the policy is active (no previous accepted output). Let H_(i-1) contain ALL prior candidate/verification outcomes and any input-dependent state visible to the strategy.

Assume for EVERY reachable active history:

`Pr[trial i produces a correct, accepted answer | H_(i-1)] >=p_i`.

This is a conditional hazard, not a marginal benchmark success rate. Then

`Pr[no accepted answer by K] <= product_i(1-p_i)`.

Proof: conditional probability that the policy remains active after trial i is at most1-p_i, since correct acceptance is one way to stop; apply iterated conditioning. Independence is unnecessary. With a sound verifier, all accepted outputs are correct, so success is at least1-product_i(1-p_i). For p_i>=p>0 the failure bound is(1-p)^K. For0<p<1 and0<eta<1, to target failure<=eta it suffices K>=ceil(log(eta)/log(1-p)); p=1 succeeds on the first active trial. the familiar O(log(1/eta)/p) uses an additional inequality and still requires the conditional p bound.

A strong enough sufficient condition is: conditional probability of generating a correct candidate >=g_i, and conditional verifier acceptance probability given a correct candidate >=1-beta_i, for every active history. Then use p_i=g_i(1-beta_i). Neither generator quality nor verifier completeness may be inferred from a marginal score on a different task distribution.

For constant p, expected trials through a cap K are at most[1-(1-p)^K]/p, since Pr[trial i is reached]<=(1-p)^(i-1). This does not replace the worst-case K budget required by a hard deadline or class definition.

## 2. Marginal retry negative control
Let one hidden Bernoulli Z have Pr[Z=1]=p. Every trial succeeds iff Z=1. Each individual trial has marginal success p, but K retries still succeed with probability p, not1-(1-p)^K. After observing one failure, the conditional success probability is0. Shared seeds, repeated identical outputs, a persistent wrong interpretation or a fixed inaccessible environment can induce exactly this shape.

Another failure: average per-task success p permits a subpopulation of tasks on which every retry fails. A global benchmark average does not justify pointwise coverage or a per-history hazard.

For SAT with m assignment bits, blind independent uniform guessing has p=2^-m on a uniquely satisfiable instance; even a perfect polynomial-time verifier then needs exponential expected trials. 'Verification exists' does not pay for finding a witness.

## 3. Imperfect validators: separate no-answer and wrong-answer risk
Suppose each active trial's probability of accepting an incorrect answer is at most alpha_i CONDITIONAL on every reachable active history. Then

`Pr[any incorrect accepted output] <=sum_i alpha_i`.

Together with the correct-acceptance hazard p_i,

`Pr[return correct by K] >=1-product_i(1-p_i)-sum_i alpha_i`.

The lower bound can be negative and should then be clipped at0. Proof partitions terminal outcomes into correct acceptance, incorrect acceptance and no acceptance; bound the latter two separately. No independence or identical trial distribution is assumed.

If a validator has only marginal false-positive rate alpha on a fixed evaluation set, adaptive search can repeatedly select an error region. That marginal rate does not imply the conditional alpha_i premise. Correlated or adversarial validator failures must remain explicit, not covered by a runner's exit code.

## 4. Actual resource ledger for retries
A sequential policy's worst-case time is the sum over reached/capped trials of generation, verification, input reread/seek, candidate serialization, validation feedback parsing and any state reset, plus routing/control. A bound is

`T_total <=sum_i(T_gen,i+T_verify,i+T_IO,i)+T_control`.

Do NOT count only K calls or only successful work. Generation and validation may be external tools only if their actual input-dependent computation/storage and service interface are charged under the same model.

Peak storage is the maximum sum of simultaneously live objects. A generally safe upper bound includes persistent model/router state, candidate payload, generator state, verifier state, live input copies, feedback history, RNG/counters and work files. A tighter max(S_gen,S_verify) is justified only after proving generator buffers can be freed/reused, verifier can consume the candidate in the declared representation, and no later retry needs those buffers. Concurrent K-way trials can need K live generator states and K candidates, not one.

A retry counter takes O(log K) bits. A retained transcript of K one-bit feedback values takes K bits (plus framing), not O(log K). Addresses/timestamps, validator explanations, scores and service timing may carry more information and need their own size/cost limits. If only an S-bit summary remains, its capacity is at most S bits, but a readable external log remains accessible state and must also count.

## 5. Binary feedback cannot identify m hidden bits in log m rounds
Let hidden X be uniform over{0,1}^m, independent of the strategy's random coins. Initially the strategy has at most2^s possible input-dependent side-information states. It adaptively receives at most K BINARY replies. Each next query is chosen from the strategy state/previous replies and independent random coins; there is no extra information in timing, variable-size responses or hidden service state exposed outside the declared replies.

Fix independent coins for both parties if needed. For each initial state, a binary decision tree of depth at most K has at most2^K leaves (early stopping follows from the observed history, so contributes no extra channel). Across initial states there are at most2^(s+K) leaves. Each leaf's final reconstruction is one m-bit string. Therefore

`Pr[recover X exactly] <=min(1, 2^(s+K-m))`.

Averaging over independent coins preserves the bound. With no initial side information, exact worst-case recovery requires K>=m. Even average success>=2/3 requires integer K>=m: if K<=m-1, the maximum is1/2. More generally a constant high success requirement cannot recover m fresh hidden bits with O(log m) one-bit replies.

If the hidden object is instead ONE marked index among m possibilities, entropy is log2(m), and balanced subset queries can recover it in ceil(log2 m) rounds. That task has m hypotheses; recovering an arbitrary m-bit array has2^m hypotheses. Confusing the number of coordinates with the number of possible arrays loses an exponential factor.

This is an information bound for a genuinely hidden object relative to the initial view. For a standard computational problem with fully supplied input x and deterministic answer f(x), Shannon entropy conditioned on x is0. A one-bit service may still perform enormous computation. The feedback-capacity argument does NOT lower-bound computational effort to evaluate f from known x and cannot replace a complexity-theoretic separation.

## 6. Verification feedback is often weaker than arbitrary one-bit queries
An equality-only oracle answers whether a guessed string y equals hidden X. Without additional query types, a failed guess excludes one hypothesis, not half the space. On uniform m-bit X, K distinct guesses can yield a verified success with probability at most K/2^m. If after K rejections the agent may output one additional unverified final guess, reconstruction probability is at most(K+1)/2^m. This is much smaller than the generic2^(K-m) channel upper bound for many K.

Binary search requires the ability to ask balanced subset-membership questions. It cannot be obtained merely by relabeling an accept/reject verifier as a generic one-bit oracle. Explanations or gradient-like scores may help, but then their computation and informational content must be declared and charged.

## 7. Executable checks and research outcome
`probe_gvc.py` uses exact fractions to check correlated marginal versus conditional amplification, explicit hidden-bit decision-tree recovery counts, and equality-oracle success bounds on small complete universes. It validates formulas and negative controls, not strong real-task success.

The result gives a usable contract for a generate-verify-compose policy: conditional hazards, adaptive soundness, worst-case time/live-state and feedback interface. It supplies no numerical real-world hazard estimate and no witness that the strengthened algorithm class separates from its ND analogue. The same policy and budget must still satisfy the formal goal v2 obligations; no positive coverage is manufactured here.
