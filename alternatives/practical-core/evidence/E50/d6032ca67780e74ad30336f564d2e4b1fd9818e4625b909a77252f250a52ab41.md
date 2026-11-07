# E50 — Separation candidates that survive reread: model and obligation matrix

pnp-sol-c, 2026-11-06. Status: conditional candidates, not accepted separation or practical coverage.

## 1. Model before theorem
Let C_R consist of uniform deterministic programs, on a named machine model, with read-only rereadable input, ordinary mutable memory and external files, and computable tools whose entire computation and communication is included in a resource envelope R(n). Program/initial database must be independent of the current input; unbounded input-length advice or an answer service is not included for free. Choose explicitly whether C_R is a class of decision languages, solvers or interaction strategies. Deterministic results below do not silently cover a randomized portfolio.

R has to specify input/output access, word precision, local/external memory, total work/I/O, service costs and failure metric. A theorem about one coordinate is useful only after proving this concrete C_R embeds in that theorem's machine class without exceeding its bound. Large constant overhead may make an asymptotic inclusion irrelevant for a finite envelope.

## 2. Candidate matrix

| Candidate | Survives input reread/external files? | What is actually separated | Missing obligation / warning |
|---|---|---|---|
| Old one-pass INDEX | No | One-pass cut-information classes | E49 gives complete counteralgorithm; do not reuse |
| Deterministic time hierarchy | Yes, if all tools compiled into the charged uniform machine | DTIME(t1) proper subset DTIME(t2) when constructible t1 log t1=o(t2) | Simulation overhead, exact model and practical envelope; hard language is artificial; no NP-membership or random-policy lower bound follows |
| Deterministic space hierarchy | Yes, if ALL writable external memory is charged | DSPACE(s1) proper subset DSPACE(s2), constructible s1=o(s2), standard sufficiently large space | Does not say small local RAM plus arbitrary disks is weak; hard language not necessarily realistic/NP |
| External-memory sorting/permutation bounds | Yes, external memory and repeated access are native | I/O lower bound in named comparison or indivisible-record model | Bit manipulation/integer sorting/compression/record generation can violate hypotheses; not generic unrestricted P-vs-NP separation |
| Input-query PARITY | Yes, random access/repeated reads included; no preprocessing of this input is free | Exact worst-case m distinct input bit probes; bounded-error q<m cannot beat 1/2 uniform error under worst-case q cap | Too weak if envelope already allows one full input scan; preprocessing must count; demonstrates access floor, not NP hardness |
| SAT restricted-clock diagonalization | Not supplied | None established here | Cannot turn arbitrary diagonal language into SAT with preserved budgets without NP membership and a cost-preserving reduction |

## 3. Self-contained charged-access floor
Input is x in {0,1}^m, presented only by an initially unread bit-probe interface. A deterministic adaptive algorithm may reread any offset, use unlimited computation and storage independent of x, then answer parity(x). If fewer than m DISTINCT offsets were read on some execution, flip an unread bit. All observed bits, control, addresses and output are unchanged, but parity flips. Thus exact worst-case correctness requires m distinct probes. Reading a word of w input bits costs w bit probes under this convention (or ceil(m/w) word reads with appropriate boundaries); a vector/tool returning parity must be charged its underlying input access, not one magical unit.

Randomized form: condition on independent algorithm coins. At any leaf whose path has not read all m positions, the parity of uniform X remains an unbiased bit, even though offsets were adaptively selected. Therefore a randomized algorithm with worst-case <m bit probes has uniform error exactly 1/2. For variable stopping time Q counting total bit probes, uniform error e is at least (1/2)Pr[not all positions read]. Consequently e<=gamma<1/2 implies Pr[all read]>=1-2gamma and E[Q]>=m(1-2gamma). The bound is tight in this expected-cost convention: read everything with probability 1-2gamma, otherwise guess uniformly. This statement allows tools only after their input-dependent observations are expanded into charged probes. It fails if an uncharged initial database contains parity(x).

This is a useful falsifiable guard against free-tool accounting. It is not evidence that real tasks are hard for a scan-capable model. All-m argument is independent of any finite probe test.

## 4. Constructive strong-model fallback, not a P/NP bridge
For a concrete choice t1(n)=n^2, t2(n)=n^3 on the same deterministic multitape machine model, t1 log t1=o(t2). The time hierarchy theorem provides a language decidable within O(n^3) but not O(n^2). Input can be reread and writable work tapes exist in both classes; therefore this separation does not depend on banning routine retrieval. Tool-rich algorithms contained in DTIME(n^2) inherit the lower bound ONLY after a uniform full-cost compilation proof. This particular language IS in P and hence NP because its deterministic O(n^3) algorithm is polynomial; the example is nevertheless only a separation of two polynomial-time subclasses, not P from NP. More general t2 choices outside polynomial time give no automatic NP membership. Nor does the deterministic statement lower-bound BPP/BPTIME or actual finite randomized agents. Constants and threshold lengths are not delivered as realistic numeric budgets.

Important consequence: a sufficiently strict clock can shrink algorithm space while retaining powerful tools in a mathematically nontrivial class. What remains unknown is whether that clock retains an empirically adequate fixed portfolio and whether the excluded tasks express the intended target. Proper subclass of P is NOT a proof that the class preserves most practical abilities, or that standard P/NP is independent of ZFC.

## 5. Primary-source acquisition and source boundary
Search on 2026-11-06 returned the original bibliographic record: Aggarwal and Vitter (1988), *The input/output complexity of sorting and related problems*, CACM 31(9), 1116–1127, DOI 10.1145/48529.48535. Current accessible description: https://en.wikipedia.org/wiki/External_memory_algorithm . Its model uses memory M and disk blocks B; sorting/permutation restrictions need original-source verification before importing a lower bound. Do not adopt an unrestricted bit-model formula from a search summary.

Fetched expert exposition: Lance Fortnow, *Time and Space Hierarchies*, 2004-07-29, https://blog.computationalcomplexity.org/2004/07/time-and-space-hierarchies.html . Exact displayed deterministic conditions match section 2. The source is explanatory evidence, not independent proof acceptance. No theorem was obtained merely by trusting an LLM summary. Query-result retrieval ids available in session: mw4wbeesn0jcp7 / mw4wbeeym424hh.

## 6. New leaf worth creating
A full-cost compiler and portfolio envelope is the bottleneck: exhibit strong realistic reference strategies fitting R, prove R embeds in a named machine/time class, and then apply a matching strict hierarchy without claiming practical adequacy or standard P/NP. This can proceed without inventing an unproved general SAT lower bound. Another leaf should independently test the parity cost guard and source provenance. No global objective is closed by this candidate matrix.
