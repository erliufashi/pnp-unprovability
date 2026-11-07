# E-chief-cert-1 — Read-only certificates are not free nondeterministic workspace

pnp-sol-c, 2026-11-06, goal specification v2. Classification: conditional/local theorem candidates and a simulation counterexample. No independent acceptance or new T3 coverage.

## 1. The exact distinction
Let V(x,w) be a deterministic verifier with input length n, certificate length at most c(n), private writable workspace s(n), and worst-case time t(n). The existential language is {x: there exists ONE fixed w such that V(x,w) accepts}. A read-only certificate is allowed to depend on x existentially. It is not independent ROM/advice, and its consistency across repeated reads is an essential resource.

A standard NSPACE(s) machine has nondeterministic choices but no uncharged, persistent readable transcript of those choices. Forgetting a guessed bit and guessing it again does not guarantee it is the same bit. Thus an upper bound on V's private work tape alone is NOT an upper bound on a same-workspace nondeterministic decider for the existential language.

Do not conflate three models:
- read-once certificate: consumed bits cannot be revisited;
- two-way read-only certificate tape: head movements and rereads are charged;
- random-access read-only certificate: address width, addressing, and bit access use a specifically declared cost model.

All allow a finite certificate fixed for the entire run; only the first supports guessing bits and immediately forgetting them in general.

## 2. Positive simulation for a read-once certificate
For a verifier whose certificate head only moves right and never revisits a cell, an NTM can guess a certificate bit on first consumption and feed it to the verifier. If the verifier pauses on the same cell, retain the current bit; when it moves right, forget it. The NTM stores V's work state, input head, the current bit and a length/budget counter. Space is O(s+log(n+c+t)); time is V's charged time plus length/clock bookkeeping under the named machine model. For logspace and polynomial certificate/time bounds, this gives NL.

Conversely a logspace NTM has polynomially many configurations. An accepting path can be chosen without repeating configurations, so polynomially many transition choices suffice. Place those choices on a read-once certificate and deterministically simulate the path with O(log n) workspace. Hence the familiar read-once logspace verifier characterization is NL, not a general rereadable-proof characterization.

Source fully read: Mark Bun, CAS CS 535, Fall 2026, Lecture Notes 9, pages 1–4, https://cs-people.bu.edu/mbun/courses/535_F26/lectures/lec9.pdf . Page 2 states the read-once condition repeatedly and explains why writing the whole witness consumes polynomial space. The local derivation here makes access and clock bookkeeping explicit.

## 3. Why unrestricted two-way logspace verification already gives NP
Define VLOG_2way to allow polynomial certificate length AND polynomial deterministic verification time, O(log n) private workspace, and two-way read-only access to the SAME certificate. Then VLOG_2way=NP.

Upper containment: an ordinary polynomial-time NTM guesses the entire polynomial certificate, stores it, and runs V. This uses polynomial space, which is allowed for NP; no logspace claim follows.

Lower containment, direct tableau proof: let N be any polynomial-time nondeterministic machine. A certificate consists of its entire bounded accepting computation tableau. Each row is polynomially long, with a constant-size alphabet coding tape contents/head/control state. A verifier checks start configuration, accepting end condition, legal row lengths/boundaries, and every local successor relation. It needs only row/column indices and a constant number of symbols, thus O(log n) private space. A two-way certificate tape can find each indexed cell by repeated scans using counters. The number of checks and scans is polynomial, so time is polynomial. Accept iff the tableau is valid. One fixed certificate must pass ALL checks. This proves every NP language has such a verifier without assuming a logspace SAT solver.

Alternatively canonical CNF-SAT has an explicit assignment verifier: for each literal with a binary variable index, seek the corresponding assignment bit; keep only index, clause-OR and global-AND flags. For an encoding with n total bits and variable indices at most n, workspace is O(log n); repeated sequential certificate seeks cost at most polynomial time (a conservative O(n^3) bound suffices), while random-access cost may be smaller but needs an explicit bit/word model. This is a verifier bound, not an O(log n)-workspace ND algorithm bound.

If one inferred 'two-way O(log n) verifier => NL', the tableau argument would imply NP subseteq NL, hence P=NP because NL subseteq P subseteq NP. That implication is a warning about an unproved simulation, not a proof of a strict separation between verifier models (NL vs NP is not known to be unequal).

## 4. Safe simulations and their real resource costs
### Whole-certificate storage
For an ordinary sequential-tape verifier, guess w into a writable tape and simulate its read-only head on that tape. Space: O(c+s+log(n+c+t)), not O(s). Time: O(c+t) on a multitape model with fixed-machine overhead, plus the specified clock costs. This restores the usual NP verifier equivalence at polynomial resource scales, but does not preserve a sublinear same-space budget when c is linear/polynomial.

For a RANDOM-ACCESS certificate verifier simulated on sequential tapes, O(c+t) is NOT automatic: each certificate request may cost O(c) scanning and address manipulation. A conservative bound is polynomial in c+t (e.g. O((c+t)^3) under bounded-bit address conventions). To claim a linear-time or fine-grained bound, keep both sides in a common random-access model or prove a tighter simulation.

### Lazy consistency dictionary
If a run makes at most q distinct certificate-address queries among c positions, an NTM may store pairs (address, guessed bit). On first query to an address, guess a bit and save the pair; on repeated queries, return its saved value. Every accepting run extends to one global certificate by filling unqueried bits arbitrarily. Conversely a real accepting certificate induces an accepting run by making matching guesses.

Additional space is O(q(log(c+1)+1)), plus verifier state, counters and address scratch. On a sequential dictionary, each lookup costs O(q log(c+1)) bit operations/sweeps up to representation overhead; total time is therefore not the verifier's bare oracle-query count. Full storage and the dictionary are separate safe constructions; one may choose the smaller certified implementation once c and q envelopes are fixed. Neither gives O(s) in general. An unconditional language lower bound against a more clever nondeterministic algorithm is NOT claimed.

### Why independent re-guessing is unsound
Formula (z) AND (NOT z) is unsatisfiable. A broken implementation reading a witness bit for each literal and independently guessing on every read chooses 1 for the first occurrence and 0 for the second, and accepts. No single assignment certificate induces that accepting trace. Therefore 'guess on demand' without a consistency mechanism recognizes a different language.

The finite probe `probe_cert_workspace.py` checks the consistent-cache simulator against ordinary assignment existence on all ordered formulas of one to three unary/binary clauses over two variables, and records the explicit inconsistent-read failure. It tests simulation semantics, not an asymptotic NSPACE lower bound.

## 5. Same-budget accounting alternatives
A defensible declaration chooses one and uses it for BOTH deterministic and nondeterministic sides:

1. **Standard workspace NTM:** nondeterministic choices are free only while made; any retained assignment/log/database consumes work space. To establish membership in NTISP(t,s), exhibit an NTM with t time and s writable bits, not a verifier whose private tape fits s.
2. **Existential read-only-proof model:** track (time, private workspace, proof length, proof access order, proof read/move costs, consistency contract). Call the class a verifier/proof class rather than silently NTISP. Deterministic baseline with no proof and existential side with a proof differ in a specifically declared primitive. A separation in these classes is not automatically the required same-model ND separation.
3. **Charged witness storage:** add c to the memory ledger on the existential side, even if read-only after acquisition. Compare against the SAME total storage allowance on the deterministic side. Existing small-space deterministic lower bounds may no longer apply when this enlarged budget is used.
4. **Read-once proof:** may recover standard small-space nondeterminism, but then establish that the chosen hard language has a verifier in that access pattern. Rereadable SAT assignments and tableau verifiers cannot simply be relabeled read-once.

The original read-only input may stay excluded from writable space, provided BOTH sides receive the same input access. That does not entitle one side to an additional input-dependent read-only certificate for free under a claimed workspace comparison.

## 6. Consequence for SAT time-space candidate audits
A theorem 'SAT not in deterministic time t and space s' plus 'SAT has a logspace assignment verifier' does not by itself establish SAT in NTISP(t,s). Required missing derivation is a genuine ND algorithm with the exact common time and retained-storage bounds. Standard guessing of the whole assignment uses its length in storage. Looking up assignment values by variable index is cheap only in an access model explicitly supporting that lookup. Repeated independent guesses are invalid. A logspace tableau verifier may also require much more than t time and a much longer witness.

Likewise deterministic SAT lower bounds say nothing automatically about bounded-error randomized solvers. Machine uniformity, input encoding, RAM word size, certificate handling and all persistent external memory must agree before transferring the result to the new goal.

## 7. Remaining actionable question
Look for a model-native nondeterministic algorithm under the SAME resource vector as a proven deterministic lower bound; or explicitly keep a proof-verifier separation as a different, weaker certificate. PPST may supply a same-time multitape result, but its full original model and compatibility with random access/tools must be checked independently by that source-audit leaf. Nothing here certifies realistic coverage, standard P/NP separation or a named ZFC-unprovable side. Goal v2 remains unresolved.
