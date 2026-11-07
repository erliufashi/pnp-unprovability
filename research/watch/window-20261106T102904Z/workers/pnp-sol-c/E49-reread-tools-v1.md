# E49 — INDEX under reread, external storage and charged tools

Author pnp-sol-c, 2026-11-06. Classification: counterexample plus conditional local lemmas; independent acceptance not claimed.

## Reference audited
Read unchanged `sublinear-stream/proof/{FINITE-BUDGET-SEPARATION-v2,FINITE-BUDGET-RANDOM-v2,FINITE-BUDGET-SCOPE-v1,CAUSAL-CONTRACT-v1,CAUSAL-RESOURCE-QUALIFICATIONS-v1}.md`. Those texts explicitly exclude payload reread and uncharged readable logs; they are not refuted internally. What fails is transferring their certificate to the newly required practical class.

## 1. A complete deterministic counteralgorithm
Task: public m; receive x in {0,1}^m, then j in [0,m). Retain no x bits. After j, rewind the read-only input and scan its first j+1 positions; emit the last bit. Registers hold j, current position and one bit, plus fixed phase flags. Workspace is O(log m), total input symbols inspected at most 2m+ceil(log2(m+1))+O(1), and there are two forward scans (only one query-informed scan). The input owner stores m bits. If the input offers random access, request offset j and read exactly one payload bit after receiving the query. Address width and offset construction cost O(log m); a bit-address interface must not be billed as unit-cost unbounded integers.

This solves EVERY x,j exactly, with one fixed uniform program, not a selected weak baseline, average-case anecdote, advice or oracle. For any sufficiently large m, its workspace is smaller than m, so the old m>s collision argument cannot hold for this protocol. The distinguishing information is in a reachable input copy, not the retained local configuration.

Communication formulation makes the break especially clear: old proof is one-way Alice(x)->Bob(j). Reread is interaction: Bob sends j (ceil(log2 m) bits), Alice returns x_j (one bit). A one-way lower bound cannot be applied to that interactive protocol. This analogy does not grant a physically free Alice: the implementation above pays for storage and access.

## 2. An external log is storage, not a miracle
During first scan append x bits to a file, keeping a counter. After query read file[j]. Local workspace O(log m); external occupancy m bits plus metadata; m bit writes and one post-query payload read (or O(m) sequential read). Thus charging only local RAM would silently admit the same counteralgorithm. Charging external capacity does NOT make it one-pass small-total-state: the configuration now includes the file contents and has at least 2^m possibilities. It merely records correctly why no contradiction exists.

Immutable input storage and mutable scratch should be separate fields: practical algorithms commonly share the former. Counting the entire input as active workspace would force every input-reading method to have total space >=m and destroy the intended streaming discrimination. Neither accounting convention is wrong, but the theorem must name which one it uses.

## 3. What remains provable without removing tools
### Cut-state lemma (deterministic exact)
At a query-independent cut after x but before j, suppose all future x-dependent accessible data jointly have at most 2^B possible values, and every other future resource (program, fixed ROM, fresh randomness for a deterministic claim) is independent of x. If the suffix must answer every j exactly without new x-dependent access, then B>=m. Proof: two x sharing the complete accessible state differ at some j; identical suffix behavior cannot answer both. B may include local state, an external database, modified weights, input-dependent addresses, logs and a precomputed index. A retained input copy contributes m already.

### Randomized average-error version
For uniform independent X,J, query-independent complete retained data Z with H(Z)<=B, and future randomness independent of X conditional on Z, average error <=gamma<=1/2 implies B >= (1-h2(gamma))m. Derivation: for each i, H(X_i|Z)<=h2(e_i), sum and use entropy subadditivity and concavity. This is precisely an information-at-cut bound, NOT a blanket theorem against search/storage tools. If a query-specific tool response A_j depends on X, the required Markov condition fails; one cannot hide A_j inside an independent fresh-randomness variable.

### Explicit escape checklist
- Query known before payload: keep only x_j and position; old late-query hypothesis fails.
- Query late plus one rewind: counteralgorithm above.
- Query late plus stored/readable transcript: database algorithm above.
- Query late plus tool returning x_j: feasible only if tool provenance accounts for its input copy/computation/access; retrieval is not an independent ROM.
- Query late plus input-independent fixed ROM only: no escape from cut-state bound; selected address is part of state.
- Output log append-only and never readable: cannot serve as external memory. Letting a later tool read it changes that contract.
- Compression with complete accessible state B<m: cannot exact-encode all x, even if decompressor runtime is unlimited.

## 4. Resource vector needed for a practical model
Use (description/advice bits and uniformity; peak local workspace; mutable external occupancy; immutable input residency; input reread/seek counts and bytes; total external bytes read/written; tool computation and calls; precision; elapsed-time/deadline; output/quality). Name access order and whether j is revealed before each pass. Charge tool execution recursively under the same resource rules, except declared physical service constants. A call count alone cannot distinguish grep over m bits from an answer oracle.

No chosen numeric envelope or parameter count is certified here. Real workflow coverage requires empirical distributions, strong reference portfolios, costs and success metrics; proving INDEX easy with reread is not proving practical adequacy. Conversely prohibiting reread to rescue this old certificate would violate the current requirement to preserve routine capabilities without a demonstrated coverage justification.

## 5. Recommended dependency update
M22 must treat INDEX as an audit witness for access contracts, not the new strong-model separation. E50 needs another hard problem or an independently justified time/I/O envelope under which INDEX exceeds budget. A new bridge obligation is to construct a lower bound that survives input reread and paid external memory at an envelope admitting real retrieval/code/data workflows. This result neither separates standard P/NP nor proves either side unprovable in ZFC. Global state remains UNRESOLVED.

## Reproducibility
`python3 probe_e49.py` exhaustively checks every x,j for m=1..12 and both explicit algorithms, checking symbols read and external capacity. This finite check verifies implementations and unit accounting only; the all-m proof is above. Its result is recorded in `probe-e49-result.json`. No old static file changed.
