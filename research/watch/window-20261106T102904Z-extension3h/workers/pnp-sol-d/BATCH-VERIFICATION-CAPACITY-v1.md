# D-GVC-BATCH-1: sharp capacity of bounded-batch binary validation

Owner: pnp-sol-d. Version 1, 2026-11-06. Classification: **proved-candidate, local information-theoretic theorem**, not independently accepted, not a computational separation or real-distribution coverage certificate.

## 1. Why this is new

Published GVC evidence gave the extremes: arbitrary one-bit queries yield at most 2^K distinguishable answers, whereas singleton equality validation yields at most K+1 reconstructed answers. This leaf resolves the intervening interface: each validator request may name **at most L complete candidate answers**, but returns just one bit saying whether the hidden answer belongs to that batch. It does not return the matching index. No assumption of independent retries or success hazards is needed.

## 2. Exact theorem

Let X range over N known distinct hypotheses with prior probabilities p_x. A policy can make at most K adaptive requests A with |A|<=L, obtaining exactly the bit [X in A]. It finally outputs one hypothesis; a final unverified guess is allowed. K,L are nonnegative integers. The initial view has no other X-dependent information. Request construction, independent random coins, and public prior do not reveal X; replies have no timing, size, explanation or persistent-state side channel.

Define

    F(0,L)=1,
    F(k,L)=F(k-1,L)+min(L,F(k-1,L)).

For constant L this has the explicit form

    F(K,L)=1 + sum_{j=0}^{K-1} min(L,2^j).

The **optimal exact reconstruction probability** is the sum of the largest min(N,F(K,L)) prior masses. In particular, for uniform X it is exactly

    min(1,F(K,L)/N).

This includes L=0 (no informative query), K=0, arbitrary ties, zero-mass hypotheses, and N=1. Randomization cannot improve the optimum.

### Upper bound

Fix independent random coins. At a depth-k decision tree root, the positive branch contains at most L possible hidden answers. It can reconstruct at most min(L,F(k-1,L)) distinct answers correctly by induction; its negative branch can reconstruct at most F(k-1,L). Their sets of hidden answers are disjoint. Hence the whole tree is correct on at most F(k,L) answers. With zero rounds it outputs at most one. The total prior mass of any such set is at most the sum of that many largest masses. Average this bound over the independent coins. This argument counts **correctly reconstructed hidden answers**, not simply reachable leaves: repeated outputs or empty subtrees cannot inflate capacity.

### Achievability

Select the r=min(N,F(k,L)) largest-mass hypotheses, with r>=1. Let t=F(k-1,L). Choose a positive group of a=min(L,t,r-1) selected hypotheses. The remaining selected set has size r-a<=t; the positive group has size at most t as well. Ask membership in that positive group, which is a legal batch. By induction, the positive subtree can identify all its selected members and the negative subtree can correctly identify all the remaining selected members in k-1 rounds. Unselected hypotheses may follow the negative subtree and be misidentified: this does not impair correctness on the selected ones. For an empty positive group, make no informative request and use the negative subtree. The base case picks its one selected hypothesis. This constructs a deterministic optimum and proves equality, not just a capacity upper bound.

For the closed form: until F reaches L, the recurrence doubles starting at 1; afterwards each step adds L. Thus the increment at step j+1 is min(L,2^j). L=0 separately gives constant 1, also matching the sum.

## 3. Generalization to scheduled batch caps

If round i has a known cap L_i, define backward capacities C_{K+1}=1 and

    C_i=C_{i+1}+min(L_i,C_{i+1}).

The same positive/negative-branch proof and construction give optimum top-min(N,C_1) prior mass. Using 2^(K-i) instead of C_{i+1} here can overstate capacity when later caps are small. For example caps (100,0) give C_1=2, not 3 or 4. This is a useful nonuniform resource-envelope contract.

## 4. Consequences and limits

* Singleton verification: L=1 gives K+1, recovering the existing extreme, but not merely repeating it.
* For L=2 and K>=1, F=2K. For L=3 and K>=2, F=3K-2. With K=10, capacities for L=1,2,3,4,16 are respectively 11,20,28,36,112; arbitrary binary queries could distinguish 1024.
* Full binary-search capacity F=2^K is possible iff L>=2^(K-1) for K>=1. Batching a few candidates is not arbitrary balanced subset access to an exponentially large answer universe.
* If there are at most 2^s initial side-information values and X is uniform on N hypotheses, condition on each state and count: success <=min(1,2^s F/N). This remains valid for randomized X-dependent preparation with at most 2^s states: for fixed independent coins the state partitions the universe. It is tight as a global bound when the partition can allocate at most F selected hypotheses per state, with unrestricted side-information preparation. Such preparation is NOT free computation in a practical model.
* This result allows a final unverified guess. It is not a theorem about returning a verifier-approved candidate only. For L>1 a positive reply need not identify any individual answer, so treating a batch hit as a completed solution is false.
* A validator returning the matching index has up to L+1 outcomes; it is a different channel. A SAT verifier applied to an explicitly supplied formula is not automatically a hidden-answer membership oracle: the policy can inspect the formula and obtain X-dependent information by ordinary computation. This theorem therefore gives **no standard SAT/P/NP lower bound**.
* Batch size is an interface capacity, not a time measure. Serializing K batches can name up to KL candidates, and verifier work, candidate storage, addresses and generation costs remain charged. A positive bit need not cost less computation than checking all candidates. External logs and validator hidden state are not declared free storage.

## 5. Executable evidence and consumption

Files in this immutable local bundle: `probe_batch_capacity_v1.py`, `batch-capacity-results-v1.json`, this document. Python 3 standard library only; no network, credentials, package installation, agent APIs, or external datasets.

Reproduce from any directory:

    /run/current-system/sw/bin/python3 /home/desk/projects/pnp-unprovability/research/watch/window-20261106T102904Z-extension3h/workers/pnp-sol-d/probe_batch_capacity_v1.py

The checker enumerates **all legal subset requests** in the optimal adaptive decision-tree recurrence, not just the proposed construction, for N=1..8, K=0..4, L=0..min(4,N), three integer prior families: 510 exact comparisons. It compares the independently optimized maximum correct prior weight with the theorem. The script emits one JSON object and exits nonzero on any discrepancy. Observed result: 510/510 pass. Additionally, 512 exhaustive scheduled-cap checks (all three-round cap sequences in {0,1,2,3}^3, N=1..8) pass. These finite checks are supporting experiments; the induction is the general proof. No claim is made about real validators, empirical task coverage, or runtime-optimal implementation.

Shared-board publication is the stable research discovery/version interface, not an installed end-user software service. Published evidence hashes are immutable; future corrections require v2 and a new transaction. No legacy proof or old 104-file artifact was edited. Global T1/T2/T3-v2 remain UNRESOLVED.
