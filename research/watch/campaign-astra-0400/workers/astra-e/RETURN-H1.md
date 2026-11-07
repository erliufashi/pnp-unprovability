# Astra E — reusable-index capability frontier (v1)

Owner: astra-e. Campaign: Astra 0400. Node: ASTRA-E-PARITY-INDEX-1.
Classification: **proved-candidate**, self-contained mathematical tradeoff, not independently reviewed. T1/T2/T3-v2 remain UNRESOLVED. No real-world coverage claim or measurement is supplied.

## Result and definition improvement

A description cap alone does not quantify the capability lost when reusable indexes are capped. For exact arbitrary binary inner-product queries on an N-bit database, an s-bit query-independent index and at most q adaptive raw-data bit probes per query necessarily satisfy

**2^s · Σ_{i=0}^{min(q,N)} binom(N,i) ≥ 2^N.**

The index may be nonlinear, Build may use unlimited computation, the query algorithm may adapt probes, and all index bits may be read for free. Consequently this is a permissive-model necessary condition: charging those resources only strengthens the obstruction. It is not a time lower bound for unrestricted word RAM, randomized bounded-error algorithms, or approximate queries.

A concrete tight example is N=3, s=1, q=1: store total parity, then answer any mask from either its single-bit residual or its complement plus cached parity. Thus banning reusable data-dependent indexes destroys a genuine elementary capability, while making them free conceals an equally genuine resource tradeoff.

## 1. Typed interface and quantifiers

Freeze one finite program pair (Build, Query), a dimension N and resource profile before evaluation. Database x ranges over {0,1}^N. Build sees x but **not the future query mask a**, producing z(x) with at most 2^s possible states. Query receives (z,a), may probe individual bits x_j, and returns a·x mod 2. Require one uniform implementation correct for every x and every a, using at most q raw probes for each query.

All data-dependent persistent state counts in s: cached tool state, compiled data-specific code, filenames/addresses if observable, selected program identifiers, and retained Build transcripts. Database-independent fixed code is separate. With variable-length states, pad to s bits or explicitly count the number of allowed states: permitting all lengths ≤s without a padding convention gives up to 2^(s+1)−1 states, not 2^s.

The raw database remains available. Its N-bit storage is a separate paid resource; q limits accesses, not whether that storage exists. Inputs such as the N-bit query mask and its decoding time are also paid in a complete resource profile, although deliberately free in this lower-bound abstraction.

## 2. Proof (nonlinear index and adaptive probes allowed)

For a fixed index value z, let F_z={x:z(x)=z}. Freeze z and a. The deterministic query computation induces a binary decision tree of depth at most q on raw input bits. Its ±1-valued output is represented by a real multilinear polynomial of degree at most q: each leaf indicator is a product of at most q literals x_j or (1−x_j), and summing signed leaf indicators gives the output. Repeated queries can be removed, or multilinearized using x_j²=x_j, without increasing degree. Correctness is required only on F_z; arbitrary outputs off F_z do not matter.

It follows that every parity character χ_a(x)=(-1)^(a·x), restricted to F_z, lies in the restriction of the space spanned by monomials of degree ≤q. That space has dimension at most D=Σ_{i≤min(q,N)} binom(N,i).

The full set of 2^N parity characters spans all real functions on the Boolean cube (the Walsh characters are an orthogonal basis). Restricting these functions to F_z therefore spans all real functions on F_z, a space of dimension |F_z|. Hence |F_z|≤D. There are at most 2^s fibers, partitioning 2^N databases. Summation proves 2^N≤2^sD.

This proof is finite and uses neither a complexity conjecture nor a reference population distribution. Build's computation and nonlinearity cannot evade it; only its number of distinguishable persistent states matters.

Corollaries: q=0 requires s≥N; q=1 requires s≥N−log2(N+1). For 0≤q≤N/2, the binomial-volume estimate gives s≥N[1−h2(q/N)]. The exact integer-volume inequality is the primary result. This is a necessary frontier, not a general sufficiency theorem for nonlinear indexes.

## 3. Constructive capability side and description accounting

Let C be an s-dimensional binary linear code in {0,1}^N with covering radius ≤q. Fix a basis c_1,...,c_s. Build stores z_i=c_i·x. On query a, find c=Σ_i λ_i c_i in C with Hamming distance at most q from a. Return Σ_i λ_i z_i XOR the raw bits selected by a+c. This computes a·x with at most q raw probes.

The route is uniform and depends only on the observed mask and fixed code; no ground-truth selector is used. The basis, decoder, Build and Query code are included in the frozen description budget. A generic basis takes sN bits, but structured codes can have much shorter generators. Exhaustive decoding is effective but may be exponentially expensive: this construction certifies a probe tradeoff, **not efficient CPU time**. Build likewise costs the actual parity computations and input reads; the s cached bits are not a free oracle.

For N=3 choose C={000,111}, s=1, radius q=1. Build reads all three raw bits and stores their XOR. If the query mask has weight at most one, directly probe its support. Otherwise complement it, probe the residual of weight at most one, and XOR the cached parity. There are no data-dependent decoder tables. Here 2·(1+3)=8, attaining the bound. More generally the repetition code for odd N has radius (N−1)/2 and s=1, also attaining the binomial-volume bound, but this is not claimed to optimize CPU cost.

## 4. What preprocessing independence must mean

Data independence would forbid the useful z=Build(x) entirely. The relevant restriction is **future-query independence given the declared database/view and public setup**: Build receives x and permitted setup, not the future mask or hidden evaluation answers. Fixed Build code alone is insufficient to establish this provenance property.

Negative control: if Build can receive a, it can store the one-bit answer a·x; then s=1,q=0 answers the one prepared query for arbitrary N. This violates the reusable-index interface and its theorem, not the theorem itself. Similarly, allowing the query routine to select one data-specialized code artifact without counting its identity as index state invalidates the fiber count.

A lawful index can contain facts from which many future answers are recovered. 'Contains answers' is therefore not a sound prohibition. The right boundary is permitted Build inputs, persistent state size, charged preparation work, and the declared set of future queries it must support.

## 5. Proposed T3-v2 contract delta

Add the following fields to the resource/model contract, without marking the contract satisfied:

1. **Phase/provenance schema:** Setup; Build(database, allowed view); Serve(index, query, raw-data access); Update/rebuild if supported. Explicitly specify information available at each phase and whether the next query is known.
2. **Two storage ledgers:** frozen description L versus data-dependent persistent state s, plus raw-data storage, transient workspace and output. Data-specialized compiled code is persistent state, not free fixed code.
3. **Lifecycle envelope:** preparation time P, per-query CPU/probes/I/O, index build/rebuild costs, peak live state, and number H of served queries. Charge total P+Σ_j T_j. Amortization P/H is a reporting identity for the actual declared horizon, not permission to assume future queries will occur. Cold H=1 and warm reuse must be separate tests.
4. **Reference capability quantifier:** one frozen reference and route for all allowed database/query pairs (or an explicitly weaker distributional guarantee). Compare the compiler output under the same Build inputs, storage/probe units and lifecycle. In this test family, preserving an all-parity reference forces the volume inequality; it cannot be achieved merely by saying indexes are allowed.
5. **Interface audit:** raw access granularity matters. A q-word-probe algorithm with w-bit words is not a q-bit-probe algorithm; do not transfer this formula unchanged. Arbitrary functions of the whole database exposed as a unit-cost tool also fall outside the proof.
6. **Separate certificates:** formal reference preservation, same-model separation and real-population coverage are distinct obligations. This node supplies a capability frontier, not D/ND separation and not coverage data.

These fields make the reference stronger and the resource contract more falsifiable without banning ordinary reusable indexing. They also expose where a candidate separation paid for too weak a reference.

## 6. Executable finite checks and evidence boundary

Consumer entry: this report is self-contained. Supplementary standard-library test: `python3 verify.py` in this worker directory. It exhaustively checks all nonempty database fibers for N=1,2,3, computing optimal exact decision-tree depth for every parity mask, and checks the tight N=3 construction on all database/mask pairs.

Observed result in `verification.json`: 273 fiber checks and 64 construction cases passed. These finite checks are not the general proof and are not real-task experiments. No packages, services, user configuration, credentials or prior evidence were modified. Shared publication uses the transaction board's immutable evidence copy; this is a mathematical artifact, not an installed application. Desktop/API deployment tests are inapplicable.

## 7. Scope, review and preservation

Inputs reviewed: current-contract-v2.json; shared-board graph/state; historical TEAM-CONTRACT-v1 and E47 capability contract. Historical deadline prose is superseded by the current 04:00 +08 campaign authorization. Existing dynamic-OR state bounds and description/advice-closure nodes were not reopened or claimed as new work. This node studies a different static reusable query family and proves a nonlinear-index/adaptive-probe frontier.

Outstanding: independent proof review; any extension to bounded-error/randomized query algorithms; efficient decoder/resource instantiation at useful scales; actual strong-reference inventory; actual population and coverage evidence. No novelty priority over the mathematical literature is claimed. No external citation is needed for the self-contained proof, and no literature search was represented as completed.
