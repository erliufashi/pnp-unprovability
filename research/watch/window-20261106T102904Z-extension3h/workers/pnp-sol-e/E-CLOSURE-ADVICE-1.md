# E-CLOSURE-ADVICE-1 — typed closure and joint auxiliary leakage

## Scope
This is a local theorem about a finite description-budget algorithm class. It is **not** a theorem about standard P/NP, human coverage, or the historical T3 proxy. It addresses a gap in the current contract: component-wise independence is insufficient once the permitted strategy class has a pairing/combination operation.

## Model
Let `C_b` be a class of Boolean advice/auxiliary maps whose descriptions have length at most `b` bits. Assume the class contains two independent one-bit projections `p_0(x)=x_0`, `p_1(x)=x_1`, and a binary composition operator `xor` whose description overhead is `k` bits. A composite program therefore has description length at most `2b+k` (or, if the library charges shared syntax once, at most `2b+k'`; the argument only needs an explicit overhead).

For independent uniform bits X,Y, each marginal P(X=1)=P(Y=1)=1/2. Define Z=X xor Y. Then Z is also uniform, but conditioned on X, Z determines Y exactly: `P[Y=Z xor X | X,Z]=1`. Thus marginal independence of each component from an individual observable does not imply joint independence after composition. In particular, an auxiliary channel carrying `(X,Z)` leaks Y despite each of X and Z individually being unbiased.

## Proof obligations discharged
1. **Finite-budget closure is not free.** If the allowed description ball is exactly `C_b`, closure under binary composition is not guaranteed: composing two members may leave the ball because its description costs `2b+k`. Any claim of closure must either enlarge the budget to `B >= 2b+k` or restrict inputs to a smaller ball (e.g. `b <= (B-k)/2`). This is a syntactic counting fact, independent of runtime semantics.
2. **Joint leakage counterexample.** Let the hidden target be Y and the visible auxiliary pair be `(X,Z)`, with X,Y independent uniform and Z=X xor Y. Each single bit is uniform, so a marginal-only test reports no bias. The pair has conditional entropy `H(Y|X,Z)=0`, hence perfect recovery. The recovery algorithm is one XOR gate and its description is bounded by the explicit composition overhead.
3. **Budget-aware repair.** A valid theorem may quantify a closed family `C_B` and require every composition tree's total code length and runtime to remain within B. Alternatively impose a leakage condition on every permitted tuple, not merely each coordinate. Neither repair supplies standard P/NP separation; they only prevent an invalid inference from marginal independence.

## Negative control
Exhaustive enumeration of all four `(X,Y)` values gives:
`00 -> (X,Z)=(0,0), Y=0`; `01 -> (0,1), Y=1`; `10 -> (1,1), Y=0`; `11 -> (1,0), Y=1`.
Both X and Z have two zeros/two ones, but the pair maps bijectively to (X,Y). This rules out an artifact of sampling or approximation.

## Classification
`proved-candidate` conditional finite-description lemma plus explicit counterexample to coordinate-wise independence. The result only updates the closure/description-budget obligations adjacent to M21/M22/M23. T1/T2 remain unresolved and T3 remains historical qualified-proxy evidence only.

## Reproducibility
No external source or model claim is required. The four-row table above is the complete finite check. SHA-256 is recorded by the transactional board at publish time.
