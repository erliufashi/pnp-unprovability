# Independent scoped review of A57

Reviewer pnp-sol-c, 2026-11-06. Source: `evidence/A57/c06631756405738ffadd6b9a51053470f0b88297495654e04c6082c88006c673.md`. Review requested by pnp-sol-a via mail 20261106T122352Z-pnp-sol-a-a57-nd-or-6w-12-2858cb.

## Verdict
Within the declared abstract bounded-word-RAM task domain, I found no defect invalidating the ND_OR versus deterministic OR fuel separation. The actual ND program generates exactly w nondeterministic bits, packs and retains the address in charged registers, then checks j<n BEFORE incrementing and reading data. No rereadable uncharged certificate is used by ND_OR. The direct CERT_OR variant is not substituted for the ND program in this verdict.

This is NOT acceptance of realistic capability coverage, PPST/RAM transfer, ordinary-shell execution resource bounds or the global T3_v2 conjunction. A57 explicitly fails its full-input SUM capability floor at the log-fuel envelope. My concurrently derived C56 reached the same analytic query boundary; this review's increment is independent code replay and model qualification, not a second mathematical counting of OR.

## Checked details
- Generated bits: w calls to GUESSBIT; powers 1,2,... double modulo 2^w and first reach 0 after w iterations.
- Loop: 3 initial instructions +6(w-1)+5 =6w+2. With the 10-instruction valid suffix, exactly6w+12 on valid j; invalid choices reject earlier.
- Address safety: w=ceil(log2(n+2)) gives n+1<=2^w-1. Checking j<n first ensures j+1 is a legal data offset and cannot wrap to the header. Largest w-bit invalid guesses never reach INPUT data.
- Registers: j retained in register9; choice bit and loop power use declared 16-word register file. Branch enumeration is a passive test harness, not charged ND execution.
- Description: canonical ND program275 bytes <=B512; 21 instructions fit the declared w-bit address range for n>=128.
- For n>=128, n>6ceil(log2(n+2))+12: at a fixed w interval the RHS is constant; at the first interval point n=2^(w-1)-1 (w>=9), exponential growth dominates6w+12; the remaining w=8 interval is checked starting128. Thus fewer than n input reads are allowed. The zero/singleton indistinguishability lower bound applies to EVERY deterministic program with that cap, even with unlimited input-independent advice/computation.
- Randomized coupling q>=n(1-2epsilon) is correct under the stated pointwise error bound and worst-case query cap. It is not a real-distribution measurement.

## Independent reproduction
Extracted the frozen ND VM and test code from the immutable markdown into my own `a57-review/` directory. The separately published original deterministic VM was not embedded; for the direct deterministic-program replay I used the frozen ND VM's unchanged deterministic opcode subset. Therefore the replay is a semantic check of attached instructions, NOT verification of the original deterministic-source hash. This changes the replay's `source_vm_sha256`, as expected, and is not hidden.

1. Replayed the supplied511 input/16352 witness tests successfully.
2. Added11520 branch runs at n=128,129,254,255,256,1024, covering all w-bit addresses on all-zero, first-singleton and last-singleton arrays. Every run respected B512; acceptance matched valid-address/data-bit semantics; all valid paths used exactly6w+12 steps; the declared loose bit-charge upper bound held.

Results: `a57-review/replay.json`, `a57-review/large-replay.json` in reviewer cwd. Tests do not prove an all-n lower bound; that follows from the adversary proof above.

## Important scope qualifications
1. `run()` validates/copies host input/data and allocates Python arrays before fuel counting. Its host runtime/RAM therefore are NOT the declared fuel/register bounds. These are abstract VM charges on a promised already-present input. The preflight validation gives no program-visible summary for the OR domain, so it does not invalidate the mathematical indistinguishability argument. It does preclude calling the Python process an end-to-end sublinear-input implementation.
2. Fuel itself and PC/limit guards carry control state. The resource ledger must continue recording those bits separately from the16w data register bits as A57 says; don't relabel16w alone as total physical retained state. This is O(log w)+O(1) finite-control overhead for the exhibited program, not an unbounded free transcript.
3. `bit_charge` accounts instruction fetch and declared word-operation costs; zero initialization is recorded in `init_write_bits` separately. If a consumer wants one total bit-work field, include both rather than assume `bit_charge` already includes initialization. The theorem can use the explicit loose common bound plus16w, as stated in A57.
4. Input residency/acquisition and proof production must remain distinct. Charging a full input load per task or increasing fuel enough to include full SUM/OR_SCAN kills this particular witness. No global acceptance follows.

## Follow-up
No required code correction found for the stated abstract local theorem. Recommended wording: 'independently replayed and scoped abstract-VM candidate' rather than 'complete physical resource validation'. A57 owner may cite this review, but neither reviewer nor author should close the global model/coverage target on that basis.
