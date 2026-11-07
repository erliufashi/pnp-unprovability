# C61 — Randomized sequential encoding: a separate boundary-transcript argument

pnp-sol-c, 2026-11-06. Local proved-candidate awaiting independent review. This does NOT say the deterministic source theorem automatically covered randomized encoders.

## 1. Claim and exact success criterion
Let C:{0,1}^N -> {0,1}^M be a binary code of relative distance at least delta>0, N>=2. A randomized encoder has the same sequential-head access rules stated below, always emits exactly M output bits, and uses at most T primitive operations on EVERY input and random tape. Coins are independent of the input and consumed one bit at a time, at most T draws. Suppose

`Pr_{uniform X, independent R}[A(X;R)=C(X)] >=2/3`.

This is whole-codeword equality probability, not coordinate-average accuracy. Pointwise success>=2/3 implies the displayed average condition, but this is NOT a real-world task distribution claim.

There are h input heads initially at1, allowed unit moves/read/head-to-existing-head jumps, with no integer-address seek. Output is sequential and unreadable. Let S bound complete retained state bits except for a possibly implicit fresh-coin cursor. Define

`S_aug=S+ceil(log2(T+1))+c`,

where c is a fixed bookkeeping constant so S_aug>=1 and the augmented state includes all control, output cursor, head positions and coin-draw count. If the original full-state convention already includes a random-tape head, that part need not be double-counted; the displayed expression is a safe conservative bound.

Then

`h S_aug T > delta N² / 18432`.

No standard P/NP separation, finite deployment envelope or practical coverage follows. In the common case S>=log(T+1), this is an asymptotic hST=Omega(delta N²) lower bound up to a constant factor. When S is smaller, the logT augmentation MUST NOT be omitted.

## 2. Why freezing coins needs a state qualification
Fixing a length-T random tape r gives an input-independent constant string. The deterministic simulation can put r into a nonuniform fixed ROM (the lower-bound comparison permits arbitrary input-independent transitions). But if it forgot the random-tape position, two otherwise equal snapshots reached after different numbers of coin draws could have different future coins. Recording the cursor/count resolves this: equal augmented states now yield the SAME future behavior on equal outside input. This is why an unqualified 'fix a seed' argument may fail for space-sensitive transcripts.

The seed is not input-dependent advice; it is fixed only for the lower-bound argument. No actual randomized program is claimed to retain all T coin bits in S_aug. A ROM/tape index suffices for the fixed-seed deterministic analysis, whose description complexity is unrestricted. Expected-time-only encoders, correlated task-dependent randomness and random-access query coins with unbounded addresses are outside this statement.

## 3. Geometry and good-input counting, derived here
Let I be an integer with2<=I<=N/2. Use only m=floor(N/I) FULL intervals of length I; any short tail belongs to the outside restriction. For a given interval mark it covered when a head enters; unmark it when all heads are distance>=I; otherwise retain its flag. Initially only the first interval is covered.

At most3h intervals are covered at any time, since each is within distance<I of some head. Total marking and hence unmarking EVENTS are at most1+T/I. A newly marked interval requires nearest-head distance to decrease from at least I to0, costing I unit steps; each such step can be charged to at most one adjacent target interval. A head-to-head jump creates no new occupied coordinate and cannot decrease nearest-head distance. These bounds hold for every X and fixed r, independent of whether the output is correct.

Select X uniformly, R independently, and i uniformly among full intervals. Let U_i count unmarking events and F_i be the fraction of output positions emitted while covered. Using m>=N/(2I), T>=N and I<=N/2,

`E U_i <= (1+T/I)/m <=4T/N`,

`E F_i <=3h/m <=6hI/N`.

Here T>=N holds because C is injective, M>=N, and even incorrect paths emit exactly M bits under the stated interface.

Let K=ceil(16T/N), rho=delta/2, and choose I<=delta N/(256h). Markov gives

`Pr[U_i>K] <=1/4`,

`Pr[F_i>rho] <=3/64`.

Therefore geometry fails with probability at most19/64. Correctness holds with probability at least2/3. A union bound gives

`Pr[correct AND U_i<=K AND F_i<=rho] >=2/3-19/64 =71/192 >1/4`.

Averaging first over r,i and then over all input bits outside interval i implies existence of ONE fixed r, ONE full interval B and ONE outside restriction for which MORE THAN one quarter of the2^I assignments to B are both correct and geometrically good. Call these assignments Y. Thus `|Y|>2^(I-2)`. No seed is claimed to work for every input; the proof only needs this large correct subset under one common seed/outside restriction.

## 4. Transcript collision on correct inputs
For each y inY record augmented S_aug-bit states at every UNMARKING event of B. Initial state is input-independent and common. At most K snapshots occur, giving at most

`sum_{ell=0}^K 2^(S_aug ell) <2^(S_aug(K+1))`

possible transcripts (the leftmost sum itself is the cardinality upper bound; the strict right inequality uses S_aug>=1).

If `S_aug(K+1)<=I-2`, two distinct correct assignments share a transcript. Between snapshots, every uncovered phase reads only the fixed outside input. Equal snapshots include the coin cursor, head positions and output coordinate, hence identical outside phases emit the same bits at the same coordinates until the next entry into B or halt. The initial outside phase is also common. Thus the two outputs differ only in their covered output coordinates, at most rho M. Since BOTH assignments are inY, these outputs equal their actual codewords. This contradicts minimum distance delta M>rho M.

Consequently an encoder must satisfy `S_aug(K+1)>I-2` for these parameters. Recording every uncovered TIME STEP instead of unmarking EVENTS would not give the required cardinality bound; output-coordinate state and coin-cursor state are both essential.

## 5. Rounding and explicit constant
If delta N>=1024h, set `I=floor(delta N/(256h))`. Then I>=4, I<=N/2, and `I>=delta N/(512h)`. Since T>=N,

`K+1<=18T/N`.

The previous section gives

`18S_aug T/N >=S_aug(K+1)>I-2>=I/2>=delta N/(1024h)`.

Therefore `hS_aug T>delta N²/18432`.

If delta N<1024h, use S_aug>=1 and T>=N directly:

`hS_aug T>=hN>delta N²/1024>delta N²/18432`.

This handles small intervals, nondivisible input lengths and all stated parameter ranges. In products above, `S_aug T` denotes augmented retained-space bits multiplied by the charged time bound.

## 6. Output-length qualification and limitations
The fixed-length output interface is deliberate. If an implementation may halt early with fewer than M bits, pad with zeros using up to M extra operations. Since any successful path emits M bits and T is a common worst-case bound, M<=T; the normalized clock is at most2T. Thus a conservative corollary can use an additional factor2 in the denominator and the corresponding augmented cursor bound. Overlong output should be rejected/truncated by an explicit output cap. Do not silently treat normalization as zero cost.

The theorem does not cover approximate per-symbol codeword outputs, quantum probes, arbitrary RAM input addressing, readable output storage, or input-dependent initial caches outside the space ledger. It supplies an independent argument for one randomized ACCESS-model lower bound, not a transfer of PPST, a generic randomized time hierarchy, or same-model D-versus-ND separation.

The local deterministic transcript derivation was separately published as C60, but all ingredients used for this randomized proof are explicitly restated above rather than hidden as a graph-level premise. Both remain independent-review candidates. Real-distribution coverage and standard P/NP/ZFC goals remain unresolved.
