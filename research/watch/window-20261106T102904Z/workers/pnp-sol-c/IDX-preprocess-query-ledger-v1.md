# E-argon-IDX-audit1 — Charged reusable indices and the right independence condition

pnp-sol-c, 2026-11-06. Conditional model contract plus executable retrieval reference; no realistic distribution coverage or same-budget D/ND separation claimed.

## 1. Correct two-stage semantics
Choose one fixed uniform Build program and one fixed Query program before the dataset D and future actual query q are known. Run

`I_D = Build(D; r_build)`

then answer queries using `Query(I_D, D_if_retained, q; r_query)`.

The PROGRAM must be independent of the current D/q. The index ARTIFACT is supposed to depend on D. Requiring I_D to be independent of D would prohibit ordinary inverted indices, database indices and cached parsing, contrary to the capability goal. Conversely merely saying Build is computable does not prohibit a fixed program from reading held-out labels, a grader service or an uncharged answer database.

Declare in advance: whether original D remains query-accessible, how it is addressed, whether q is revealed before Build, which query distribution/workload is known, and whether updates are allowed. If q is known before preprocessing, computing just that query's answer is legitimate for that different protocol but not a certificate for late-query capability.

## 2. Resource vector, cold and warm
Record independently:
- allowed Build input/provenance and program/parameter/database description sizes;
- raw-data residency, Build peak workspace, produced index size (including headers, vocabulary/keys, pointers, doc IDs and alignment);
- Build time, bytes read/written, input passes/seeks and tool computation;
- per-query time, peak live workspace, index/raw-data bytes accessed, output length and copying;
- updates/rebuild costs, index version, synchronization/staleness behavior and disposal;
- whether randomization, word width, dictionary collision assumptions and service costs are worst-case or expected.

For K queries after one build and updates U_j, total work is

`T_total = T_build + sum_i T_query,i + sum_j T_update,j + T_routing/serialization`.

The amortized average divides this FULL total by the actual K. It does not erase Build. A cold first query pays T_build+T_query,1. A warm query may pay only its local cost conditional on a preexisting correct index, but index residency and acquisition/maintenance remain in the lifecycle ledger.

If Build costs1000 units and each query1, then1000 queries average2; the cold first request still costs1001. A10-unit deadline is not satisfied for that cold request. Choosing an arbitrarily large hypothetical K to amortize cost, or averaging only over successful warm requests, changes the consumer contract. Failed/time-out/invalid queries must remain in the declared evaluation denominator with distinct outcome labels.

Shared index storage may be physically counted once across simultaneous consumers, but then global resident capacity, ownership and versioned updates must be accounted at the shared level. Do not charge each actor only an empty local cache while leaving the shared dataset/index free.

## 3. Label leakage: computability and statistical correlation are the wrong tests
A perfectly computable, fixed Build_bad can loop over public task IDs, query a hidden grader's labels, and store all answers. Thus 'Build is uniform/computable' is insufficient to certify permitted preprocessing. Charging elapsed time alone does not turn an unauthorized label source into an authorized observation.

A useful policy is provenance/noninterference: define the permitted observation view A and forbidden label source L. For fixed Build code and random coins, changing L while holding A fixed must leave the output index unchanged:

`Build_view(A,L0;r)=Build_view(A,L1;r)`.

A sufficient implementation condition is that Build can access only A and declared independent randomness, with no capability to read L. A field whitelist/instrumented unit test checks only that local boundary; it is NOT a proof that no network, filesystem, embedded weights or previously cached label channel exists. Model/data provenance and external-service permissions must be audited separately.

Do NOT instead demand statistical independence of I_D and correct answers Y. A legitimate index may correlate with Y, and if Y is a deterministic function of allowed raw data, such correlation can be the whole point. Also do NOT ban all offline answer computation: computing answers from permitted data with fully charged work is a valid algorithm. What is forbidden is an undeclared source/protocol, not success itself.

Build resources must include any label generation COMPUTATION if it is permitted. If producing I_D solves an expensive task once, that expense belongs in preprocessing rather than being hidden under an innocent index filename.

## 4. Query-only index capacity versus retained raw input
For an arbitrary m-bit dataset x and a late coordinate query j, if query-time access is ONLY to an index I(x) of at most b bits and the same fixed Query program, exact answers to every j force b>=m. If two x,y share I, choose a differing coordinate j and the decoder cannot answer both. The theorem is about complete future accessible input-dependent state, not local RAM alone.

If original x remains randomly addressable, simply read x_j with a log m-bit address. No claim b>=m for the auxiliary index follows, because the raw data already carry m bits. If an input-dependent immutable file is accessible, calling it 'read only' does not erase its information content; it must be recorded as raw-data residency even if excluded from writable workspace.

For a smaller fixed query family, less information may suffice. For example OR over x has a one-bit precomputed answer, while all coordinate queries require distinguishing2^m datasets. A capacity argument must specify the query universe and late-query order before claiming a lower bound. This observation is a boundary for preprocessing, not reuse of old one-pass INDEX as a new strong-model separation.

## 5. Executable retrieval capability floor
`probe_idx.py` implements a concrete whitespace-token inverted index with exact, explicitly case-sensitive token equality. Build scans every document token, stores a sorted doc-ID posting list per term, and never reads the test label table. Query returns the matching document IDs; an independent direct scan serves as the semantic reference. Query output copying is counted by number of returned IDs, not called a free single bit.

The probe includes repeated tokens, absent terms, empty documents and Chinese tokens; performs updates only by a charged full rebuild; and checks every observed plus absent term against the direct scan on128 documents. It demonstrates that this particular ordinary retrieval operation can be explicitly retained rather than forbidden. It does not make whitespace matching a sufficient model of natural-language search, certify Python hash-map worst-case O(1), measure physical RAM, establish a nearlinear universal compiler, or infer broad real task coverage.

Recorded logical counters include token reads/posting writes, query dictionary accesses and returned-ID counts. JSON index bytes are measured separately from logical posting entries; Python host overhead and hash lookup complexity are NOT inferred from those counters. A true bit/word cost bound needs a frozen representation, word precision and implementation-level accounting. Program code and metadata are not claimed free.

Negative controls show: Build_bad remains computable while leaking a forbidden label map; a permitted-view wrapper excludes that map locally; warm-only accounting violates the cold deadline example; an index built on version0 can return a stale answer after a dataset update unless rebuilt/version-checked.

## 6. Outcome and remaining obligations
The structural contract permits ordinary indices while ruling out free input-dependent answer services. It supplies an executable exact-retrieval baseline and separates uniform-code independence, permitted-data dependence and forbidden-label noninterference. No production dataset distribution, strong multi-domain reference bundle or global adequacy threshold is fabricated.

For a new same-budget separation, both sides must receive the SAME preprocessing privileges, raw-data access and index/storage budget, with the same lifecycle denominator. A deterministic lower bound that forbids preprocessing cannot be combined with an ND upper bound that receives a built index or read-only witness for free. Existing toy OR separation disappears once its summary can be precomputed without being charged. Goal v2 remains unresolved.
