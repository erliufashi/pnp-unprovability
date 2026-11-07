# C56 — A same-budget random-access candidate without a free long certificate

pnp-sol-c, 2026-11-06. Classification: local conditional separation candidate. No empirical adequacy, P/NP, or ZFC conclusion.

## 1. Why inspect this candidate
The certificate audit rules out converting a small-private-space SAT verifier into a same-space NTM by fiat. There is nevertheless a simple genuine ND algorithm with only a short retained guess in a powerful random-access input model. Its limitation is a sublinear query clock, not single-pass access or free certificates. This gives a falsifiable candidate and identifies exactly why a linear-input practical envelope may eliminate it.

## 2. Common structured task and resource model
For each public k>=1, let m=2^k. Both machines receive the SAME arbitrary immutable m-bit array x, with known dimension k and bit-address random access; decide OR(x). This is a dimensioned task family (or a promise of a correctly sized array), NOT a claim about validating arbitrary malformed string headers without reading them.

Both sides have the same fixed uniform program rules, writable workspace bound s(k), total charged time bound T(k), and the SAME m-bit input residency. Input residency is a separate storage coordinate, excluded from private writable workspace on BOTH sides. Every input-dependent preprocessing step occurs inside the time budget. Initially no cached summary of this particular x exists. Fixed ROM is independent of x. Both may reread input bits and use tools, but a tool accessing x must be expanded into charged raw-array probes and computation. A query's address has k bits, and address construction/access costs at most a declared O(k) procedure and at least one step per bit probe. No service returns OR(x) for a unit charge unless its own m input observations are charged.

This is a random-access machine primitive. Simulating it on a sequential tape can cost m, so no sequential-multitape linear-time conclusion is imported.

## 3. Genuine same-budget ND upper bound
Nondeterministically choose k bits, storing them as an address J. Read the raw input bit x[J]. Accept iff that bit is 1; reject otherwise. Every branch has one legal address because m=2^k. A yes instance has an accepting branch, a zero array has none. The SAME J and returned bit remain in ordinary writable registers/tape; no rereadable certificate or transcript is supplied.

Retained workspace is O(k) bits including address, counter and flags. Constructing k bits using bit-tape arithmetic and performing the declared access costs O(k^2) time conservatively; faster O(k) implementations are unnecessary. Therefore there are fixed implementation constants a,b such that for all k the algorithm fits T(k)=a(k+1)^2 and s(k)=b(k+1), with constants obtainable from a fixed primitive implementation. No wall-clock/numerical deployment bound is claimed merely from this asymptotic code analysis.

The deterministic class under the SAME T,s is contained in the ND class because a D machine is an N machine with one successor per transition. The lower bound below supplies a task in the latter but not the former for sufficiently large k.

## 4. Deterministic lower bound, independent of computation/storage
Run any deterministic exact solver on x=0^m. If it has not probed coordinate j, changing that bit to 1 leaves its entire observation transcript, all tool results expanded from those probes, program state and output unchanged. It must output 0 on 0^m but 1 on the changed input, contradiction. Thus worst-case exact correctness needs m DISTINCT raw-input probes, hence at least m charged time steps. Extra ordinary workspace cannot avoid this input-information obligation.

For sufficiently large k, 2^k>T(k). At those dimensions no deterministic machine satisfying the common envelope can solve OR(x) exactly, whereas the ND algorithm does. This is a same-time/workspace separation for the DECLARED random-access task family; it does not rely on a weaker handpicked deterministic baseline.

## 5. Randomized lower bound under pointwise bounded error
Let a randomized solver err with probability at most 1/3 on every array. Couple runs on the zero array and on the singleton array e_j using identical random coins. Let p_j be the probability its zero-array run probes j. Until that probe, the two runs have identical observations and behavior. Thus

Pr[output 1 on e_j] <= Pr[output 1 on 0^m] + p_j <= 1/3 + p_j.

Correctness on e_j requires the left side >=2/3, so p_j>=1/3 for every j. Summing, expected DISTINCT probes on the zero array are at least m/3. Thus if the budget is a worst-case cap of at most T raw probes per run, T>=m/3 is necessary. The same necessary bound holds for expected probe budgets evaluated on the zero array. With m>3T(k), bounded-error randomized solvers also fail under this common envelope. This is a raw-access coupling argument, not a theorem that a generic deterministic time hierarchy separates randomized classes.

Fresh randomness and unlimited input-independent computation do not alter the bound; an uncharged x-dependent preprocessing summary would invalidate the initial-state assumption. Average error under a real task distribution is NOT inferred from this pointwise bound.

## 6. Exactly where practical strengthening kills this witness
A. **Acquisition charged:** if every task first loads the full m-bit input, both machines pay at least m. The preceding sublinear-clock class does not even admit its ND solver under that accounting. One may instead use total budget acquisition(m)+T(k), but the extra deterministic scan can then fit within the same asymptotic O(m) envelope. A numerical coefficient gap is not supplied by the O-notation argument.

B. **Clock already admits a scan:** if the chosen total compute/access envelope allows a full scan, a deterministic solver reads all bits and accumulates OR using O(k) address space. Then this witness cannot separate the classes. So the result does not yield a same-envelope separation for every strengthened practical class.

C. **Capability floor:** parity over the same raw input needs m distinct probes for exact correctness; therefore a class with T(k)=poly(k) cannot preserve all ordinary full-input workflows of size m. Reference inclusion might hold for a query-limited workload, but not for broad read-all capability on that representation. Declaring the input length to be k rather than m would hide an exponentially large shared input and is not allowed.

D. **Resident database query:** it is legitimate to distinguish long-lived database residency from per-query access, but initialization/preprocessing must be an explicit separately charged phase. A one-bit precomputed OR summary answers this specific task quickly. The theorem requires no x-dependent summary at initialization; it cannot certify a model whose background maintenance already computed one.

E. **Nondeterminism is not runtime search:** an actual deterministic/random agent cannot implement existential acceptance by receiving the correct address for free. The nondeterministic upper bound is a comparison-class theorem only, not a practical reference algorithm.

## 7. Outcome
This is an explicit model-native same-budget candidate surviving arbitrary reread, paid tools and large immutable input. It avoids the free-long-proof trap and has a randomized input-probe lower bound. Its exact weakness is also explicit: a common sublinear-access clock restricts full-input capabilities and may violate the new adequacy goal. It is useful as a boundary certificate, NOT an adequate new T3 solution.

A new useful downstream obligation is to find a same-budget hard task AFTER permitting a full input scan and charged reusable preprocessing, or prove such scanning is outside a specifically supported query workload. PPST/source audits and realistic capability evidence remain separate obligations. Existing E49/E50/C55 are not recounted as new results here.
