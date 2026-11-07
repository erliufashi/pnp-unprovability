# C60 — A self-contained boundary-transcript lower bound with rounding and variable-length transcripts

pnp-sol-c, 2026-11-06. Local proved-candidate, NOT independently accepted. Motivated by the textual counting mismatch identified in C59, but the argument below states its own precise model and constants. It does not alter the source or any old proof.

## Theorem and model
Let C:{0,1}^N -> {0,1}^M be a binary code with relative Hamming distance at least delta, where 0<delta<=1 and N>=2. A deterministic algorithm computes C on every input. It has:

- h>=1 read-only input heads, all initially at position1;
- one chosen head may move left/right by one, read its current bit, or jump to another EXISTING head's position; no arbitrary offset seek;
- complete retained machine state has at most2^S values, with S>=1, including all input-head positions, control/clock information and sequential output cursor; input and previously emitted unreadable output bits are excluded;
- deterministic time-homogeneous transitions, or any changing control schedule encoded in that complete state;
- output is append-only, in increasing coordinate order, one bit per output operation, never reread;
- T is an upper bound on all primitive operations, including head moves and output. An operation that moves a head does not simultaneously read an unknown input bit and emit an output; split such operations at constant cost if needed.

The state-update function may be arbitrary and nonuniform for each N, but is fixed independently of this input. All input-dependent accessible data are included in S or reached through the declared heads.

Then

`h S T > delta N² / 18432`.

The strict sign is merely a consequence of the deliberately loose derivation; no numerical implementation or optimal constant is claimed. Since C is injective, M>=N, and emitting its M bits gives T>=N automatically.

This is a deterministic encoding/access-model theorem. It is NOT a separation of D from ND in the same model or a practical adequacy certificate.

## 1. Marked intervals and visit budget
Choose an integer I, with2<=I<=N/2. Partition the first mI input positions into m=floor(N/I) FULL consecutive intervals B_1,...,B_m, each of length I. The remaining short tail is NOT selected as an interval; its bits remain ordinary outside input.

For each B_i maintain an analysis-only covered flag. It becomes1 if a head enters B_i, and becomes0 once every head is distance at least I from B_i; otherwise keep its old value. Initially only B_1 is covered. These flags are proof bookkeeping, not a new computational resource.

At any time at most3h full intervals are covered: a covered interval has a head at distance<I, and a given head can be that near at most its own interval and its two neighbors.

Let a marking mean0->1, including the initial B_1 marking. The TOTAL number of markings over all full intervals is at most1+T/I. To see this, after the first free marking, each marking of B_i starts with nearest-head distance at least I (at initialization or after its previous unmarking) and reaches0. A head-to-head jump cannot decrease the minimum distance to B_i because it creates no new occupied coordinate. A unit move can decrease that minimum by at most1. The final I units of distance reduction occur while moving a head through an adjacent interval toward B_i. Attribute that move to the target adjacent interval. A unit move receives at most one such attribution. Thus every noninitial marking needs at least I attributed moves and the total attributed moves is at most T. Unmarkings are no more numerous than markings because each consumes an earlier marking.

This uses EVENT counts, not the number of time steps for which an interval remains uncovered.

## 2. Good restrictions exist, including the short-tail case
Choose a uniform random X in{0,1}^N and an independent uniform full interval index i in[m]. Let U_i(X) be its unmarking count. Since m>=N/(2I) and T>=N>=I,

`E[U_i(X)] <= (1+T/I)/m <= (2T/I)/(N/(2I)) =4T/N`.

Let K=ceil(16T/N). Markov gives `Pr[U_i(X)>K] <=1/4`.

Let F_i(X) be the fraction of the M output coordinates emitted while B_i is covered. At each output event at most3h full intervals are covered, so

`E[F_i(X)] <=3h/m <=6hI/N`.

Take rho=delta/2. Provided `I<=delta N/(256h)`,

`Pr[F_i(X)>rho] <=6hI/(rho N) <=12/256 =3/64`.

Therefore the probability both `U_i<=K` and `F_i<=rho` hold is at least1-1/4-3/64=45/64>1/2.

Now condition on i and all input bits OUTSIDE B_i. Averaging implies some full interval B and some fixed outside restriction have MORE THAN half of their2^I interval assignments satisfying both bounds. Let Y be those good assignments. Thus `|Y|>2^(I-1)`. The short tail is automatically fixed among the outside bits; there was no illicit assumption that all intervals have length I.

## 3. Correct boundary transcript and its cardinality
For each y inY record the complete S-bit machine state immediately after each UNMARKING of B. There are at most K such events. Initial state is common and input-independent; its initial uncovered phase, if any, requires no extra recorded state. Call this variable-length list R(y).

A list with ell entries has at most2^(S ell) possibilities. Hence across all lengths0<=ell<=K,

`#possible R <= sum_{ell=0}^K 2^(S ell) < 2^(S(K+1))`,

using S>=1. We have NOT replaced a variable-length transcript by an unjustified2^(SK) count, and have NOT recorded every uncovered TIME STEP.

If `S(K+1)<=I-1`, then fewer than2^(I-1) transcripts exist, whereas more than2^(I-1) good assignments exist. Thus two distinct assignments y,z share the same transcript.

## 4. Why shared boundary states synchronize output coordinates
During an uncovered phase no head is inside B. From its initial snapshot, deterministic execution can be simulated using only the fixed outside input until a head enters B (making it covered) or the algorithm halts. No unknown B bit can be read before that re-entry. Thus equal boundary states imply the same uncovered execution, emitted bits, and end-of-phase output cursor.

This holds first for the common initial uncovered phase, then for every corresponding unmarking snapshot in R(y)=R(z). Every snapshot includes the output cursor, so the produced chunks occupy IDENTICAL coordinates in the two codewords. The analysis does not merely know that the two computations emitted the same number of unspecified bits.

Consequently the set of uncovered output-coordinate chunks is identical for the two runs, with identical bits. Their only possible disagreements are the remaining covered coordinates. In either good run at most rho M such coordinates exist. Hence

`dist(C(y outside), C(z outside)) <=rho M <delta M`,

contradicting the code's distance. Terminal covered phases cause no problem: all output length is fixed M and their coordinates are precisely the complement of the synchronized uncovered chunks. It follows that an encoder must have `S(K+1)>I-1` whenever the good-restriction premise holds.

## 5. Choose integers and derive an explicit constant
First suppose `delta N>=512h`. Set

`I=floor(delta N/(256h))`.

Then I>=2, I<=N/256<=N/2, and `I>=delta N/(512h)`. Section2 applies. Since T/N>=1,

`K+1=ceil(16T/N)+1 <=18T/N`.

Sections3–4 imply

`18ST/N >=S(K+1)>I-1>=I/2>=delta N/(1024h)`.

Therefore `hST>delta N²/18432`.

If instead `delta N<512h`, then S>=1 and T>=N directly give

`hST>=hN>delta N²/512>delta N²/18432`.

This proves the stated bound for all parameters in the theorem, with no missing small-I or truncated-interval case.

## 6. Scope of the repair
This argument provides one explicit conservative bound in a precisely declared binary sequential-head model. It repairs the EVENT-versus-TIME-STEP and transcript-length issues seen in the source's Lemma52 presentation, and separately handles integer intervals and output alignment. It does NOT certify the source's printed numeric800, its full positive encoder construction, a randomized/ND lower bound, arbitrary offset seeks, arbitrary output-address writes, or uncounted readable output logs.

Source context remains Cook–Moshkovitz, CCC2024, DOI10.4230/LIPIcs.CCC.2024.5. The proof here is a local independently written candidate and should be externally reviewed before an accepted theorem status. It is useful for testing model-preserving simulation costs after reread is allowed, not for declaring broad realistic capability loss or gain without evidence. Standard P/NP/ZFC and T3_v2 remain unresolved.
