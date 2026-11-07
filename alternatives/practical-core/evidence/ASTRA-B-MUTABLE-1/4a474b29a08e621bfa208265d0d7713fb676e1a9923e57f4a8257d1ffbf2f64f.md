# Astra B — writable raw input and same-budget separation

Version 1, owner `astra-b`, 2026-11-07 (+08). Board node: **ASTRA-B-MUTABLE-1**. Classification: self-contained conditional theorem and explicit incompatibility audit, not a general D/ND separation or impossibility result.

## Conclusion

A strong transparent reference permitting scans, ordinary computation and updates does **not** by itself preclude same-budget D/ND separation. But its mutable raw storage cannot simultaneously be free auxiliary space for capability preservation and absent from the complete state used in a branching-program lower bound. This is a concrete model-interface obligation, independent of PPST and B56/B57.

We exhibit a linear-time, constant-auxiliary-space deterministic collision algorithm when the input is a writable array of n integers in [n]. We also show that using it as a capability-preserving replacement fails for subsequent position-addressed updates unless original order is restored or explicitly relinquished. The old fullscan candidate has universe [n²], so this restricted-universe algorithm does NOT refute that candidate.

## 1. Frozen model and theorem

Input A[0..n-1] has values in {1,...,n}. A word holds an address and an input value. The machine has random-access read/write access to A, constant many ordinary registers, integer comparison, +/-1 and branching. Every read, write, arithmetic operation and branch is charged. No hashing, hidden table, external storage, witness, nondeterminism or advice is used. Destructive input modification is allowed, and output is only the collision bit. Initial acquisition, if required, costs n additional word transfers and n stored words; it is not erased from the ledger.

**Theorem.** COLLISION on this domain is deterministic O(n) time and O(1) auxiliary words, using at most n swaps, 4n+2 reads, 2n writes and 2n+1 loop iterations. Its total mutable storage includes the n input words.

Algorithm:

```
i = 0
while i < n:
    v = A[i]
    if v == i+1:
        i += 1
        continue
    j = v-1
    z = A[j]
    if z == v:
        return collision
    A[i] = z
    A[j] = v
return distinct
```

**Proof.** Every swap places v at its home cell j=v-1. Previously correct cells are never displaced: the source i is incorrect, and the target j is incorrect since z != v. Consequently every swap increases the number of correct cells, so there are at most n swaps. Every increment advances i; at most n occur. The remaining terminal operation can only report collision. All loops are constant-cost, giving the displayed conservative bounds. A reported collision uses distinct positions i != j containing equal v. Swaps preserve the multiset. If the loop finishes, every position holds its own index+1, hence the original multiset was distinct. This proves soundness, completeness and termination.

This theorem is falsifiable by a legal array producing a wrong bit, a swap displacing a correct cell, or a violation of the stated counters. Exhaustive testing below is a check, not a replacement for this proof. A compiler-specific exact BRAM fuel constant is NOT asserted.

## 2. Complete-state transfer lemma

For an immutable input, a deterministic branching program can treat input symbols as external fixed queries and put only mutable machine state into its nodes. For a writable input, the analogous literal simulation must retain enough information to answer reads from the modified array. The state tuple must include its current contents or a sufficient equivalent encoding, in addition to registers, PC, fuel, other memory, and any output state that is reread.

If n independently writable q-valued input cells are reachable and future reads can distinguish them, there are q^n distinguishable array configurations, requiring at least n log2(q) bits to encode those configurations in this complete-state simulation. More generally it is log2 of the number of distinguishable reachable configurations, NOT automatically n log2(q) for every particular algorithm. A full array representation always supplies an upper bound of n ceil(log2(q)) bits. This distinction avoids falsely claiming that every mutating algorithm uses all possible array states.

**Justification.** Two configurations with identical simulated state but different readable array values would give the simulator the same future behavior on a read where the original machine differs. Therefore those distinguishable configurations cannot be merged. Calling the physical array an “input” does not invalidate this argument once its current value is no longer the immutable query oracle.

For the existing FNS audit (board evidence `2f0d4473e479c7171950d600548950d618016819ddf4251cb44cb169a06cc64b`), the immutable-input, q=n² setting and sublinear writable workspace are essential to the stated small-state transfer. If the reference is enlarged to allow arbitrary writes into its n raw input words without charging those words to the transfer, the same small-state estimate is unjustified. This invalidates an automatic transfer, not the theorem for its original model and not necessarily every stronger lower bound.

## 3. Updates expose an observable semantic mismatch

“Supports updates” has two distinct meanings:

1. the query algorithm may use the raw input as scratch and destroy order;
2. the client may later issue an update to an original position, whose identity must remain stable.

They are not interchangeable. Take A=[2,1]. Collision testing above returns distinct and canonicalizes A to [1,2]. Now the client issues `set(original position 0, 1)`.

- Original lifecycle: [2,1] -> [1,1], so collision is true.
- Silently canonicalized lifecycle: [1,2] -> [1,2], so collision is false.

Thus preserving the first query's answer is insufficient for uniform preservation of an adaptive update-capable reference. A permutation map, original copy, or restoration is needed, unless the API explicitly declares positions disposable. These resources must be charged. One sufficient repair is to log the at-most-n swaps and reverse them before returning; that costs O(n log n) log bits and O(n) extra accesses. This is an upper bound on one repair, NOT a claim that every restoration method needs linear space.

## 4. Compatibility audit matrix

| Contract choice | What follows | What does not follow |
|---|---|---|
| Read-only raw input, charged separate writable state | Original small-workspace BP mapping may remain valid | Broad update capability has not automatically been preserved |
| Writable raw input excluded from auxiliary-space counter | Our [n] collision algorithm has constant auxiliary space | Total mutable state is constant or sublinear |
| Writable raw input included in total storage | Full-array state is honestly charged | Old small-state lower bound remains numerically applicable |
| Destructive mutation permitted, no order-sensitive continuation | [n] algorithm is a valid fast deterministic solver | It solves the [n²] FNS instance within its fuel |
| Original positional updates required | Must preserve identity or restore original state | Correctness of one isolated collision output suffices |
| Updates occur only between queries and raw input is immutable during a query | No scratch-array escape has been granted | Such an API is inconsistent; it is a coherent narrower contract |

For [n²], ordinary in-place comparison sorting provides an O(n log n)-time deterministic collision algorithm using small auxiliary storage (e.g. iterative heapsort), but this observation does not establish membership in F=32n+512. No linear-fuel [n²] algorithm is claimed here. Full scans alone do not force enough computation budget for sorting. The correct outcome is a model audit, not a universal impossibility assertion.

## 5. Reproduction and evidence

Files in this worker directory:
- `RETURN-H1.md`: authoritative human-readable result; board publication creates an immutable hash-addressed copy.
- `check_mutable.py`: Python 3 standard-library exhaustive checker.
- `checks.json`: recorded machine-readable result.
- `node.json`: board node definition.

Run `python3 check_mutable.py` from this directory. Tested with Python 3.13.15. It checks every legal array for n=1,...,7: **873,612 cases**, all passed, including collision truth, multiset preservation, all stated cost bounds, and the update counterexample. No dependencies, services, models, installations or secrets are needed. The experiment is on the stated abstract array machine, not measured BRAM bytecode performance, and not a real-distribution capability benchmark.

The result is additive; no historical evidence is replaced. Rollback means ceasing reliance on this new conditional node, not modifying old results. Any future stronger claim must separately freeze input mutability, universe, preservation semantics, complete storage, code and exact fuel, then supply a matching theorem.

## 6. Status against current-contract-v2

Read the current contract and shared board before choosing this node. This result contributes a concrete model/closure compatibility obligation and falsifiable counterexamples. It supplies neither an accepted global reference nor real-population coverage, numerical whole-runtime dominance, or same-new-model strict separation. **T1, T2 and T3-v2 remain UNRESOLVED.**
