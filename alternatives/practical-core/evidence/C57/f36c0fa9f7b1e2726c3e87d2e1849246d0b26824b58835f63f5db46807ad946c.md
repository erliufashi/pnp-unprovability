# C57 — Two monotone proof heads can restore NP

pnp-sol-c, 2026-11-06. Status: self-contained local theorem candidate, independent review outstanding. Not a new practical coverage certificate or a claimed strict NL-vs-NP separation.

## 1. The ambiguity in “read once”
The completed certificate audit used the standard NL characterization: one read-once certificate head, polynomial certificate/time and O(log n) work space. A subtle variation allows TWO independent monotone heads over the SAME immutable existential certificate. Each head reads every cell at most once, but a cell may be observed once by each head at different times. Thus the certificate provides a shared, consistent history across observations; it is not a consumed single stream of fresh guesses.

This variation matters for implementations that expose two cursors, duplicate read handles, multiple streaming consumers, resumable reads or a server that retains a shared proof blob. Describing each individual cursor as “one-way” does not restore the single-read-once theorem.

## 2. Precise class and theorem
Let V_2mono be the languages having a deterministic polynomial-time verifier with:
- ordinary two-way read-only access to x, |x|=n;
- one fixed existential binary certificate w of polynomial length;
- TWO read heads over that same w, initially at its left end; each may stay or move right, never left;
- O(log n) writable private work space, with proof-head positions O(log |w|) included in any full-configuration representation;
- explicit finite-alphabet, sequential-symbol access; moving a proof head and processing a symbol costs time.

Claim: V_2mono = NP.

This is a statement about a verifier model with free read-only proof residency, NOT NSPACE(log n). We do not assert V_2mono differs strictly from the single-head class: that would entail NL != NP, which is not proved here.

## 3. NP upper containment
Guess the entire polynomial proof into an ordinary polynomial-time NTM work tape. Simulate two read heads with positions/copies of the proof. Even a crude scanning simulation takes polynomial time. Proof storage is polynomial, so this establishes V_2mono subseteq NP, not a logspace nondeterministic implementation.

## 4. NP lower containment by a single shared tableau
Take any NP language with deterministic polynomial-time verifier A(x,z), with |z| bounded by a fixed polynomial. Pad z to a fixed polynomial length using a conventional length tag or a verifier that handles padded witnesses. Compile A into a deterministic single-tape verifier M with polynomial slowdown. Let P(n) be a polynomial time bound for M and choose a polynomial row width W(n) containing its entire reachable tape interval. Modify halting configurations to self-loop, so exactly P(n) steps suffice; acceptance at the final row is meaningful.

A certificate w encodes rows C_0,C_1,...,C_P, separated by fixed delimiters. Each row has exactly W tape-symbol positions. A constant-size marked alphabet records the unique tape head and finite control state. Binary-encode that finite alphabet by constant-size blocks. C_0 contains the exact x, an arbitrary candidate z in the prescribed witness region, and blanks elsewhere, with the initial head/state. Private counters compute W/P and row/column positions in O(log n) space. Checking x can use the ordinary input tape; no copy of x is stored in workspace.

Position head H1 at the beginning of C_0. Move H2 forward exactly one row to the beginning of C_1. Then process pairs (C_i,C_(i+1)) in lockstep:

1. Check row lengths, delimiters, permitted symbols and exactly one marked machine head in each row.
2. For every cell j, the deterministic single-tape transition's next symbol/marker is a function of the constant-size old neighborhood j-1,j,j+1 (with fixed boundary conventions). Retain a three-symbol window from H1 and compare its predicted next cell with H2's current cell. A one-cell phase offset suffices; neither proof head moves left.
3. At the end of the pair, H1 is at the start of C_(i+1), and H2 at the start of C_(i+2). Repeat, using the SAME proof row C_(i+1) now encountered by H1 which H2 encountered previously.
4. Separately check the initial row against x/witness formatting, count the prescribed number of transitions, and require C_P to be accepting. The witness region is arbitrary only in C_0; every later occurrence is constrained by checked transitions.

A row may have delimiter/header bookkeeping of constant or logarithmic size; all such fields are checked with counters and consumed monotonically. Exact fixed row/transition counts rule out truncation and excess proof. During the last pair, H2 sees the final row and can collect its accepting-state flag without rewinding.

Space consists of constant symbol windows/flags and a constant number of O(log n)-bit counters. Time is polynomial: each proof head traverses the proof once and per-symbol arithmetic can be implemented in O(polylog n) bit time; initial-input checking and polynomial-bound calculations remain polynomial. Proof length is O(P*W), polynomial.

Completeness: an accepting witness z induces a valid accepting tableau, and the verifier accepts it.
Soundness: if the verifier accepts, C_0 encodes one actual candidate z for x, and EVERY adjacent pair is a legal deterministic successor. Since the same physical certificate fixes each shared row, the checked pairs form one globally consistent accepting computation. Therefore A(x,z) accepts. No local pair may silently replace its shared middle row.

Thus every NP language belongs to V_2mono.

## 5. Where a fake small-space ND simulation breaks
One might independently guess the stream seen by H1 and the stream seen by H2. That lets them disagree about C_(i+1): H2 used it as a successor row, while H1 later uses a different version as a predecessor. Each pair could look locally legal while there is no single accepting history from C_0. The shared proof tape prevents this for the actual verifier; a small NTM that forgot the previous head's bits has no such guarantee.

The lag between the two heads is one whole row. A straightforward sound ND simulation stores at least one row, O(W) symbols, or the whole proof; it is NOT justified by O(log n) private verifier space. No unconditional lower bound against all clever ND decision algorithms is claimed. The issue is failure of the purported direct semantic simulation.

## 6. Consequences for the research contract
- A “read once” flag is not enough in a model manifest. Specify number of readers, whether their data source is the SAME persistent object, total per-cell observations, ability to reopen handles, and whether a service retains a replayable transcript.
- A copied proof given to two readers is valid only if its equality is guaranteed by the model or checked; two independently existential proof strings need not match. Equality itself cannot be assumed for free.
- Constant readers do not imply tiny effective proof information: even two monotone heads suffice for the NP verifier construction above.
- Charging all proof residency or lag-buffer memory changes the common resource vector; do not continue applying a deterministic small-workspace lower bound without updating its allowance.
- The theorem has polynomial time, not linear time, and intentionally uses a tableau expansion. It cannot serve as an NTIME(n) membership assertion or PPST substitute.

This result strengthens the access-contract audit without depending on missing empirical data. Real-world capability preservation, accepted same-budget strong-model separation and named ZFC-unprovability remain unresolved.
