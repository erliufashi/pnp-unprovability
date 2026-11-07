# C55 — Uniform paid-tool closure and the fixed-envelope trap

Author: pnp-sol-c, 2026-11-06. Classification: conditional local theorem candidates, independent review outstanding.

## Motivation and scope
E49 removes the old one-pass INDEX bridge. E50 suggests hierarchy results that permit reread and ordinary storage. A missing step is whether a genuinely tool-rich algorithm class can be placed inside the hierarchy's charged machine model. The following gives a sufficient construction, and identifies two reasons an apparently restrictive definition can silently recover unrestricted behavior. This does not certify any actual reference portfolio or new practical coverage.

## 1. A precise, non-oracular tool model
A strategy has one finite deterministic controller and a finite library of deterministic tools. Their joint code is fixed independently of input x and its length n. All input arrives on an ordinary read-only tape which may be scanned both ways; any seek movement is charged. Scratch files are ordinary writable tapes. Calls are synchronous, with finite-byte input/output protocols. Every tape read, write, head move, branch and emitted/copied symbol inside caller AND callee is charged one primitive step on their respective fixed finite tape machines. Constructing input/output buffers, resetting work areas, reading files, changing tools and marshalling messages all count. There is no unit-cost unbounded arithmetic, pre-filled input-dependent database, precomputed length-dependent advice or remote oracle.

Fixed initial ROM/program constants can be arbitrarily large but finite; their access is implemented by the declared finite machine. Large constants do not become measured practical efficiency. Any mutable weights, input history or caches are tape contents and must be acquired/modified under the same charges. Input-independent persistent data may be part of the fixed code only if finite; input-dependent data may not appear for free.

Let total ledger work be T(n)>=n. The number of primitive actions includes tools, not merely controller actions or API call counts. This permits parsing, code execution, data processing, reread and persistent scratch in principle. It does not automatically permit all network services, arbitrary concurrency or randomness; those require extensions and their own simulation proofs.

## 2. Full-cost compilation lemma
For any fixed such strategy p, there is an ordinary deterministic Turing machine deciding the same language in O_p(T(n)^2) time.

Proof construction. There are only constantly many distinct finite tool/controller machines and thus constantly many tape/head types. Encode active continuations, finite control, scratch tapes, message tapes, head markers and input on one simulator tape, separating tracks with delimiters. A total of T primitive actions can visit/write only O_p(T+n) tape positions: each head move and data acquisition is charged, and fixed initial constants add only a p-dependent constant. Simulate an action by sweeps over the encoded configuration, updating head markers and symbols, and switching finite control at calls/returns. Each action uses O_p(T+n) simulator steps; call-boundary copying/resetting is already represented by charged primitive actions, not a bulk free operation. Repeated tape sweeps may themselves require a quadratic upper bound but no additional asymptotic storage beyond O_p(T+n). Hence O_p(T(T+n))=O_p(T^2). This intentionally conservative one-tape simulation avoids claiming an unproved realistic constant or fast-RAM overhead. Calls can be inlined into the fixed transition system; no unbounded stack is free.

This proof fails for a tool declared to return an arbitrary answer in one step, for arbitrary-precision registers at unit cost, or a seek whose unbounded physical displacement is ignored while using a tape hierarchy theorem. A word-RAM or disk model can still be used, but must receive a separate bit/tape simulation cost with bounded word/address width.

## 3. A mathematically proper class with ordinary tools
For each fixed integer k>=1 let C_k contain the languages decided by the strategies above with ledger O_p(n^k) on every input. A plain deterministic multitape algorithm can act as the controller without tools. Therefore, with the same underlying conventions,

DTIME(n^k) subseteq C_k subseteq DTIME(n^(2k)).

By deterministic time hierarchy, there is a language in DTIME(n^(2k+1)) not in DTIME(n^(2k)): n^(2k) log(n^(2k))=o(n^(2k+1)). That language is in P but not C_k. Hence C_k is a proper subclass of P. No streaming prohibition was used, and no P-versus-NP claim follows. The witness might be artificial and its useful lengths/constants are unspecified. This is a conditional mathematical route to shrinking algorithm space while allowing tools, not a practical adequacy theorem.

The inclusion does not prove a particular observed workflow belongs to C_k: the worst-case ledger, all service costs and input encoding must be supplied. For a finite task distribution, a measured envelope is more informative than a bare exponent; both are needed if invoking asymptotic hierarchy and real capability evidence together.

## 4. Trap A: existential polynomial exponent loses strictness
If the definition instead says 'some polynomial total work' with no common fixed exponent, the class is C_poly = union_{k>=1} C_k. The left inclusion above gives P subseteq C_poly, and the right gives C_poly subseteq P. Thus C_poly=P. Saying 'each tool runs in polynomial time' is additionally insufficient if exponentially many tools/calls are allowed; the bound must be on total work, not individual calls. A proper subclass needs a fixed clock/envelope or another actually restrictive condition.

Randomized policies are not covered by this deterministic hierarchy argument. If independent random bits are introduced with polynomial total worst-case time and error <=1/3, the corresponding unrestricted union is the standard BPP-type model under the simulation, not automatically a proper subclass of P or BPP. Fixing a random seed does not preserve the original success law. The finite portfolio must identify which policy class its evidence concerns.

## 5. Trap B: asymptotic properness does not shrink a finite task universe
Fix a maximum length N and let U be all finite binary inputs of length <=N. For ANY Boolean labeling of U, a finite program can embed its complete answer table and a trie lookup routine. Asymptotically, such a program can reject all lengths >N after scanning at most N+1 positions. The embedded table and huge constant become fixed program-dependent constants. In an ordinary multitape/tape model, trie traversal might be extremely expensive, but over a finite domain its runtime is bounded by a finite constant; with bounded early rejection it is O_p(n) for n>=1. Therefore for any fixed finite U, unrestricted finite-code C_1 already realizes EVERY labeling of U.

This does not contradict C_1 proper subset P: the exclusion is over all lengths, not any fixed finite task universe. It DOES show that asymptotic O_p(n^k), without a numerical code/advice/runtime bound, cannot by itself certify meaningful finite algorithm-space contraction. The same issue affects an arbitrary finite static-parameter count if unlimited external code/databases are allowed beside it.

Simple finite counting guard: with fixed binary encoding and program description length <=L, there are at most sum_{i=0}^L 2^i=2^(L+1)-1 programs, hence at most that many total deterministic Boolean functions on U, even if computation is unlimited. There are 2^|U| possible labelings. If |U|>=L+1, not all labelings fit (strict inequality follows even at equality because of the -1). This is existence by counting, not a constructive realistic hard task, not a lower bound against randomized finite programs, and not evidence that L preserves practical capabilities. Fixed code, included databases, prompt policies and adapter descriptions must all count consistently. An arbitrary language-specific lookup table cannot be relabeled as a free universal environment.

## 6. Deliverable boundary and next missing inputs
A plausible definition needs two separate contracts:
1. **Structural/math:** uniformity; fixed clock; code/advice bound; precision; all tools and mutable memory charged; compiler overhead; policy type.
2. **Practical:** fixed strong reference portfolio; task distribution and groups; numerical cost bounds; same output/loss/deadline; measured confidence and distribution shift policy.

This document supplies a sufficient mathematical construction for (1), plus explicit failure cases. It supplies no empirical data for (2). Next actionable input is a concrete code/database inventory and per-workflow ledger from the chosen reference portfolio. Without those, no defensible numerical common envelope can be selected and no claim of preserving most realistic problem-solving is licensed.

Reference for the hierarchy condition: Fortnow, 'Time and Space Hierarchies' (2004-07-29), https://blog.computationalcomplexity.org/2004/07/time-and-space-hierarchies.html , fetched during E50. The full-cost compilation proof and finite-domain warning above are explicit local derivations, not claimed as novel established literature results. T1/T2 standard P/NP/ZFC target remains UNRESOLVED.
