# C59 — Original-source audit: efficient coding distinguishes RAM from strong sequential access

pnp-sol-c, 2026-11-06. Classification: sourced conditional model evidence, NOT a D/ND same-budget separation or an empirical coverage certificate.

## 1. Source acquisition and reading scope
Joshua Cook and Dana Moshkovitz, *Explicit Time and Space Efficient Encoders Exist Only with Random Access*, CCC 2024, LIPIcs 300, article5, pp5:1–5:54, DOI10.4230/LIPIcs.CCC.2024.5.

Official page: https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2024.5
Original PDF: https://drops.dagstuhl.de/storage/00lipics/lipics-vol300-ccc2024/LIPIcs.CCC.2024.5/LIPIcs.CCC.2024.5.pdf

Downloaded complete54-page PDF,1,089,147 bytes; sha256 `c4b308ef922eee1b95140a1d9672cd2430c383f95dc9d370408e1be61e5eed15`. Local files `ccc2024-encoder.pdf` and pdftotext extraction `ccc2024-encoder.txt` in my exclusive cwd. No package/config install or shared-source modification. First transfer timed out; resumed it and successfully parsed the complete PDF.

Read original introduction/main statements/model pp5:1–5:7 and the COMPLETE lower-bound subsection9.1 pp5:40–5:46, including definitions, nonadaptive warmup and adaptive proof. I did NOT independently verify the entire54-page condenser construction or the matching upper-bound construction. The positive RAM encoder is therefore a source-reported theorem with its exact statement inspected, not a newly independently accepted implementation.

## 2. Exact model facts, not title-level inference
**Theorem1, p5:3:** for fixed constant epsilon>0, an explicit constant-rate, constant-relative-distance linear code has a uniform encoder with random access to its N-bit message, time N^(1+o(1)), and O(log²N) workspace; output alphabet has constant bit length for fixed epsilon. This is almost linear time, NOT O(N). Do not silently improve the upper bound to linear time.

**Definition6, p5:6:** sequential oracle has h head positions in[N], initially all1. Each operation can move one chosen head +1, move it -1, read its current bit, or jump it to the position of another existing head. It is NOT arbitrary integer-address seek. Working memory may itself have random access. This model permits arbitrary re-reading, backward motion, multiple simultaneous saved cursors and head-to-head jumps. It is much stronger than one-pass streaming, yet not the RAM input model.

**Theorem2, pp5:3 and5:46:** if a code encodes N message bits with relative distance delta, and its encoder uses h sequential input heads, time T and space S with S>h log N, then

`h S T = Omega(delta N²)`.

**Remark44, pp5:40–41:** S is complete retained state, including work tape, head positions and number of output bits already written. The output is written IN ORDER. Previously printed output bits and the input are excluded. If one starts with work-tape space only, the premise S>=h logN allows the complete-state correction up to a constant factor.

**Remark45, p5:41:** lower-bound transitions may be arbitrary nonuniform functions of working state and bits under the input heads. Its time lower bound is actually on head movements, so extra free internal computation in this deliberately powerful comparison does not rescue sequential input access. This is a lower-bound model fact, not license for free arbitrary input-dependent tools.

The proof is deterministic as written; it gives no automatically transferred randomized or nondeterministic encoding lower bound. A statement earlier in the introduction about nondeterministic branching-program codeword recognition concerns another paper/model/task, not Theorem2's encoder.

## 3. A concrete asymptotic incompatibility
Fix constant delta>0 and target workspace S=Theta(log²N). Even permitting h=Theta(logN) heads, with the constant adjusted so S>h logN, Theorem2 forces

`T = Omega(N² / log³N)`.

Thus it excludes N^(1+o(1)) encoding at that workspace, while Theorem1 supplies a random-access encoder with those asymptotic time/space bounds. With only constant h the lower bound strengthens to Omega(N²/log²N).

This witness survives ordinary reread and multiple cursors, unlike the old INDEX single-pass certificate. It gives a meaningful explicit coding-task ACCESS-MODEL gap. It does not separate D from ND within one strengthened model. Replacing one side's input interface with RAM to obtain the upper bound is exactly a model change and cannot be relabeled same-budget nondeterminism.

## 4. Lower-bound proof mechanism and a textual issue
The proof partitions the message into intervals. A marked/covered interval has some head nearby; at most3h intervals can be covered at once. A new visit after all heads were far requires traversing an interval's length, so Lemma49 bounds marking/unmarking EVENTS by1+T/I. A random-restriction averaging argument finds an interval whose contents can vary over more than half of all2^I choices while it has few unmarking events and few outputs produced while covered. Recording complete boundary states yields a collision between two interval contents; uncovered behavior depends only on those states and the fixed outside bits, so the encoded messages have too little output distance.

**Textual mismatch in Lemma52, p5:45:** its proof defines R(y) as the tuple of states at 'every step Bi is uncovered', but then bounds this by8T/N occurrences. Definition51 only bounds how often Bi is UNMARKED, not total steps uncovered. Those are different quantities; an interval can be uncovered for most of the computation after a single unmarking. As literally written, that cardinality step is not justified. The introduction and nonadaptive warmup instead refer to snapshots on unmarking, which is the intended boundary-transcript argument.

Safe local repair sketch (not a claim of complete new independent publication acceptance): take snapshots on UNMARKING EVENTS, plus the input-independent initial outside phase if needed. If there are at most K events and S-bit states, variable transcript length must also be counted. There are at most sum_{ell=0}^K2^(S ell) <2^(S(K+1)) possible transcripts, rather than silently at most2^(SK). The full snapshot includes head positions and output index, so each uncovered segment can be simulated with the fixed outside restriction; it cannot read a bit from the varying interval until becoming covered. If S(K+1)<I-1, more than2^(I-1) good assignments force a collision. With K=O(T/N), T>=N and integer/constant slack in I=Theta(delta N/h), this preserves the asymptotic hST=Omega(delta N²). One may use a smaller covered-output threshold, e.g.delta/4, to absorb a union bound over the two collided computations rather than rely on their covered-coordinate sets being identical.

The final proof also has inconsistent intermediate constant32/16 phrases. Therefore I do NOT import the printed numeric800 as a rigorously verified finite-envelope constant. Only the asymptotic source theorem plus the stated repair conditions is used here. Integer interval rounding and small-parameter cases require care before creating a numeric certificate. A source's typography issue is not evidence that the entire theorem is false; neither is a plausible repair a substitute for independent formal acceptance.

## 5. Why this matters for the new practical model
- If a proposed universal compiler preserves low workspace but realizes arbitrary input seek only by sequential replay/multihead snapshots, it may incur nearly quadratic time on a bona fide coding workload. 'It can reread' is not sufficient for nearlinear capability inclusion.
- A tool exposing integer-offset reads or an indexed database can move the strategy into the RAM side. It must be charged, but charging it does not justify applying the sequential-input lower bound anyway.
- Random-access writable files storing the entire message contribute N bits of workspace and destroy the low-space premise. Even with fixed static input residency, access order remains material.
- Out-of-order output, patchable output files or readable output logs need separate modeling. The proof explicitly uses output index to align produced codeword coordinates; it cannot be transferred untouched to an arbitrary output-address interface.
- This explicit code family gives an additional structural reference-capability candidate, not measured evidence that most real tasks need this exact encoder. No finite wall-clock constants, production codec, or representative workload coverage have been supplied.
- Nonuniform lower-bound robustness does not supply a fair description budget for the positive side; code/data/advice still need a shared ledger in the new model.

## 6. Result and next obligation
The source supplies a technically stronger warning than single-pass INDEX: nearly linear low-space capability can depend on TRUE random access even after backward reread, multiple heads and head-to-head jumps are allowed. It supports including access capabilities in the common resource vector and explicitly costing their compilation. It does not solve the required same-model D/ND separation or prove broad practical adequacy.

Next source-level work would verify a finite, uniform instantiation of the RAM encoder and a corrected lower-bound transcript lemma with constants, or audit whether a proposed reference compilation actually falls inside Definition6. Without those, do not turn this asymptotic access-model separation into a numerical or global success claim. Standard T1/T2 and T3_v2 remain UNRESOLVED.
