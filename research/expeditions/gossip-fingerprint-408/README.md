# The Average That Leaves a Fingerprint

**Exploratory synthetic mathematics, not empirical MHAC evidence.** Refs #408. Base: `495a98ca12bae467a507031f04931aa4254b1866`. Live README, authority map, programme, runbook, issue search and related #276 were reconciled before writing. #276 concerns stopping debt under repeated partition averaging; this packet concerns exact minimum-round pairwise circuits and fault localization, not stopping criteria. No frozen record or shared index modified.

## Model and scope

Let n=2^k >=2. A round is a perfect matching of n labelled registers. Each edge replaces both values by their arithmetic mean, simultaneously. Real-valued exact arithmetic, known fixed schedule, complete observation of every output and independently controllable inputs. A missed gate acts as identity on its two endpoints, not as zero, delay or arbitrary corruption. Nominal target J/n, where J is the all-ones matrix. A k-round exact circuit is minimum-round: an output can depend on at most 2^r inputs after r rounds. On a complete graph the binary hypercube gives such a circuit. For other graphs the compiler only decides existence of a k-round schedule, for n=2,4,8. It does not decide eventual exact consensus in arbitrarily many rounds.

Context: Shi, Li, M. Johansson and K. H. Johansson, *Finite-time Convergent Gossiping*, IEEE/ACM Transactions on Networking 24(5), 2016, pp. 2814–2826, DOI https://doi.org/10.1109/TNET.2015.2484345, author preprint https://arxiv.org/abs/1206.0992v6 . Accessed 2026-11-24, abstract only: symmetric averaging admits finite-time convergence iff n is a power of two on unrestricted networks; optimal node update count n log2 n; topology matters. These are established results, not discoveries of this packet. The proofs below are self-contained for the stated restricted model; no literature-wide priority claim or screened evidence claim.

## Exact fingerprint theorem

Write M_l for the matching average in round l, indexed 0,...,k-1. Every final coefficient is 1/n. Expand each coefficient as the number of time-respecting binary paths from input to output divided by 2^k. Thus every input/output pair has exactly one path. No prefix row can contain a repeated input path (it extends via self-edges to a final row). Each prefix of length l therefore has exactly 2^l distinct inputs of weight 2^-l. The two prefix supports entering a gate must be disjoint, else the next row repeats a path. Reverse the schedule: each M_l is symmetric and the full product is symmetric J/n, so the same facts apply backwards.

For gate (a,b) at round l let d=e_a-e_b, P=M_(l-1)...M_0 and Q=M_(k-1)...M_(l+1). Replacing this one gate by identity changes its round matrix by dd^T/2. Consequently the exact final error operator is

    E = (1/2) Q d d^T P = v u^T / n

where u=2^l P^T d and v=2^(k-l-1) Q d have entries -1,0,+1. Their support sizes are 2^(l+1) and 2^(k-l), respectively, each with equal positive and negative counts. Hence rank(E)=1, there are 2n nonzero entries of magnitude 1/n, and

    ||E||_2 = ||E||_F = sqrt(2/n).

The unique right singular direction is u/||u||. All constant inputs give zero residual; many other inputs do too. An early omission affects many outputs but depends on few inputs; a late omission affects few outputs but depends on many inputs. The worst-case Euclidean sensitivity is stage-invariant. A nonzero residual's output support identifies l from 2^(k-l) in this exact model. All claims concern the mathematical transfer, not dB, listening or real devices.

## Single-probe compiler

At any fixed round, each input/output pair has a unique path crossing precisely one gate. The rectangles supp(v) x supp(u) of its n/2 gates therefore partition the n x n pairs. Distinct gates at that stage cannot have identical nonempty rectangles; different stages have different support dimensions. Thus all one-fault error matrices are distinct and nonzero.

To obtain one input separating all single faults and the healthy circuit, avoid u^T x=0 for each gate. For two gates with v=z or v=-z, also avoid (u-w)^T x=0 or (u+w)^T x=0 respectively. All forms are nonzero by the rectangle argument. Noncollinear output masks cannot yield the same nonzero vector, so other comparisons are unnecessary. Assign variables left to right; bucket each form by its last nonzero coordinate. At step i each form in that bucket excludes at most one integer, and earlier forms are already satisfied. Selecting the smallest nonnegative integer not excluded, from 0 through the bucket size, always succeeds. The returned exact integer probe distinguishes no fault and all single omissions. It is not claimed amplitude-optimal. Unknown gains, noise and multiple simultaneous faults require separate qualification.

## Graph compiler and preserved negative cases

The search enumerates graph-allowed perfect matchings; the state is a tuple of input-support bitsets. Reject any merge of intersecting supports. The unique-path proof establishes necessity, and disjoint union doubles uniform supports, establishing sufficiency. Memoization is exact. None means no minimum-round solution, not a general impossibility certificate. Four nodes: a spanning 4-cycle is necessary and sufficient. Eight-node witness outside cube topology: rounds [(0,1),(2,3),(4,5),(6,7)], [(0,2),(1,3),(4,6),(5,7)], [(0,4),(1,5),(2,7),(3,6)]. The union has odd cycle 0-1-3-6-4-0. Thus a bipartite hypercube is sufficient, not necessary. The eight-node path is refused.

An initially proposed *triangle* witness failed the exhaustive census; the actual nonbipartite witness has a five-cycle. Do not infer existence of a triangle from nonbipartiteness.

Multiple omissions need not add. In the four-node butterfly omit gate 0 in both rounds. If F_A,F_B,F_AB denote their respective transfers and T the healthy one, then 4(F_AB-F_A-F_B+T) has rows [1,-1,0,0], [0,0,0,0], [-1,1,0,0], [0,0,0,0]. The single-fault dictionary is not a multi-fault decoder. Floating-point implementations, arbitrary weights, longer circuits and incomplete observation are outside this theorem.

## Reproduce and exapt

Run `python fingerprint.py run > regenerated.json` from this directory. Python standard library; deterministic output on the tested runtime. `python independent.py` uses NumPy (tested 2.3.5), enumerates pairings independently via permutation quotient and multiplies integer matrices directly. It reproduces 480 exact schedules among 11,025 candidates with first matching fixed, and 5,760 single-fault checks. The primary oracle also checks all 64 labelled four-node graphs (10 feasible), audits canonical butterflies through 64 nodes, and compiles a separating probe for each of the 480 schedules. Multiplying by the 105 possible first matchings gives 50,400 labelled ordered exact schedules, not an additional executed census. 336 of 480 fixed-first schedules use nonbipartite edge unions (not distinct graph count). Maximum observed probe coordinate across the 480 is 5, not an optimality claim.

Audio: `run/early-vs-late.wav`, 2 s stereo PCM16 at 16 kHz. Each 125 ms block probes a different basis input of a 16-register butterfly; one sinusoid per output, signed amplitude proportional to residual coefficient, sin-squared window. Left omits first gate of first round; right first gate of last round. Early fault speaks through sixteen output carriers for two probe positions, late fault through two carriers for sixteen probe positions. These are mathematical residuals mapped artistically to tones, not human detection or physical listening evidence. Renderer and SHA-256 retained; WAV not committed. Repeated local run matched byte-for-byte, no PCM clipping. NumPy oracle is separately formulated by the same assistant, not human or independent external review.

Potential transfers: a diagnostic test vector for deterministic distributed averaging, exact regression fixtures for parallel reducers, a topology-constrained patch compiler, or a synthesizer in which the same nominal mixing result acquires different residual textures from a deliberate missing gate. A real implementation would need tests for asynchronous updates, missing measurements, rounding, unknown state, noise and false localization. No participants, production use, accepted design requirements or protocol changes.

Status: standalone synthetic qualification only. Draft PR for review; do not close issue or merge absent repository-wide checks and substantive review. AI-assisted proof/code/sonification; no external reviewer.
