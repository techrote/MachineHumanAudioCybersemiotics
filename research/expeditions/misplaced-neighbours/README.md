# The Dial That Misplaces Its Neighbours

Synthetic expedition, issue #280, 2026-11-24. This is not a selected empirical study, a claim about listeners, or a production interface. All code and scores here are original AI-assisted artifacts; no human review is claimed.

## Model and motivation

A linear dial enumerates every binary preset exactly once. An n-bit preset represents n independent binary switches, with all switches equally weighted. Define J as the largest Hamming distance between successive dial detents and B as the largest absolute index gap between any pair of presets differing in exactly one bit. J measures local change during a sequential sweep; B measures the worst number of detent advances needed to visit an arbitrary one-bit neighbour. Lower is preferable for each objective under these definitions. The dial has no wrap, no shortcuts, and no duplicate presets. Neither measure is an empirical usability measure.

A Gray traversal guarantees J=1, but that guarantee runs only one way. In reflected Gray order, the first and last presets are one-bit neighbours, so B=2^n-1 (n>=1). If wrap-around is allowed, that particular witness disappears: this is an important boundary, not evidence for the circular-layout problem.

## A constructive alternative

Let g be the reflected (n-1)-bit Gray order, of length m=2^(n-1). For n>=2, concatenate g in the lower subcube with g rotated right by one position in the upper subcube. Reflected order is cyclic, including for the two-vertex case. Thus each half consists of one-bit steps, and the bridge connects corresponding copies of the last lower-subcube vertex. All vertices occur once. Within either half, index gaps are at most m-1. Across the halves, the one-bit matching has gap 1 for the last vertex of g and gap m+1 for every other vertex. Consequently J=1 and B=m+1 exactly. For n>=3 it strictly improves the reflected order in this metric; no general optimality claim is made for n>=6.

## Exact bounds and small-case census

The established unconstrained hypercube bandwidth theorem is due to Harper: H(n)=sum over k=0..n-1 of binomial(k,floor(k/2)). Hales numbering attains it. In a Gray path, vertex parity alternates along the order. Therefore every one-bit edge has odd index gap and B must be odd. The smallest odd integer at least H(n) is a lower bound for all Gray paths. It is not always attainable.

The solver appends unused vertices within the allowed step cap J. When position i is being assigned, all neighbours of the vertex at i-B must already be assigned or occupy i. More than one missing neighbour is impossible; one missing neighbour forces the next choice. The algorithm checks all remaining choices, excluding already assigned vertices and edges exceeding the cap. By cube automorphisms the first vertex can be zero and the second can be the low J' bits for every possible first-step weight J'. These restrictions preserve both metrics. A complete unsuccessful search certifies infeasibility; exhausted node budgets do not.

| Bits | Reflected B | Exact minimum B with J=1 | Minimum B with J<=2 |
|---:|---:|---:|---:|
| 2 | 3 | 3 | 2 |
| 3 | 7 | 5 | 4 |
| 4 | 15 | 9 | 7 |
| 5 | 31 | 17 | 13 |
| 6 | 63 | unresolved (23..33) | 23 |

For n=2,3 parity and Harper's bound suffice with a witness. At n=4 the search rules out 7; at n=5 it rules out 13 and 15. The shifted family supplies the upper bounds. The two-step solutions for n=2..6 attain the established unconstrained lower bound, so are optimal with that cap. We do not claim that two steps are necessary at n=6. The exhaustive Gray census starts at zero, retains all coordinate permutations, and counts 2, 18, and 5712 paths for n=2,3,4 respectively. Of the 5712 four-bit paths, only 48 attain B=9. Independent enumeration of all 40320 labelled three-bit orders gives the frontier B=5 at J=1 and B=4 at J>=2.

## Escaping an exact-search stall

The exact solver failed to decide (n=5,J=2,B=13) within 30 million visited prefixes. This failure is deliberately retained in results.synthetic.txt. A separate seeded local search penalizes squared edge-span violations and squared sequential-jump violations, and swaps entries, sometimes restricting swaps to equal-weight layers. A zero penalty is a directly checkable witness, never a statistical proof. The n=5 witness was found at trial 0 / iteration 22409; n=6 at trial 42 / iteration 53377 (seed 280, GCC/libstdc++ local build). Both are preserved and independently checked in verify_audio.py and verify.mjs. A 20-trial n=7, B=43 attempt exhausted its budget with penalty 7, not an impossibility result. A 40-trial n=6 attempt previously stopped at penalty 2; extending the same seeded run found a valid witness. Floating-point annealing trajectories can vary by platform, but the retained permutations do not depend on the heuristic for verification.

## Reproduction and artistic scope

From this directory (Python 3.11+, Node 18+, GCC-compatible C++):

```sh
node verify.mjs
python3 verify_audio.py
g++ -O3 gray_check.cpp -o /tmp/mhac-gray-check
/tmp/mhac-gray-check
g++ -O3 anneal.cpp -o /tmp/mhac-anneal
/tmp/mhac-anneal 5 13 20
/tmp/mhac-anneal 6 23 200
/tmp/mhac-anneal 7 43 20
```

The last command is expected to return 1 on the tested build because the heuristic did not find a witness. Node receipt generation is deterministic and has no dependencies. Python checks use direct pair-of-position comparisons and enumerate small paths without deadline pruning. The C++ checker reimplements Gray feasibility with prefix masks, without forced-candidate branching. The Python renderer emits two original stereo PCM16 16 kHz WAVs, each 3.84 seconds. Each bit gates one sinusoid over a fixed common carrier, with a 10 ms raised-cosine ramp at each transition. One WAV sweeps the shifted versus two-step four-bit layouts. The other visits the same one-bit neighbour (0 -> 8) by reflected Gray (15 detent moves) versus the relaxed order (4 moves), holding the target after arrival. The acoustic mapping is arbitrary; differences in component changes are defined by the score, not demonstrated perceptual effects. The results do not apply to arbitrary perceptually weighted or continuous parameters, a circular dial, duplicated states, multi-axis controllers, or direct state access.

## Provenance and qualification

Wang, Xiaohan; Wu, Xiaolin; Dumitrescu, Sorina (2009), *On explicit formulas for bandwidth and antibandwidth of hypercubes*, Discrete Applied Mathematics 157(8), 1947–1952, DOI 10.1016/j.dam.2008.12.004. Author-hosted version: https://www.ece.mcmaster.ca/~sorina/papers/hypercube%20published.pdf . Accessed 2026-11-24; consulted pp. 1947–1948 definitions and Theorem 2 (PDF page index 1 visually inspected). This is the source of the established bandwidth theorem, not a claim of priority for it. The constrained construction, enumerated bounds and audio are scoped to this expedition. This was not an exhaustive novelty review.

Live base observed: 495a98ca12bae467a507031f04931aa4254b1866. Recent open expeditions and keyword issue searches for hypercube and Gray code were inspected before creating #280. No shared or frozen paths altered. V8 executed the JavaScript core and fetched-back source to reproduce the synthetic receipt. Python and GCC checks were executed locally; the committed source blob IDs were compared with the local tested sources. C++ outcomes: 4,7 infeasible (266 prefixes); 4,9 feasible (47); 5,13 infeasible (1607794); 5,15 infeasible (13999306); 5,17 feasible (1328). Python reproduced all Gray histograms, all 40320 three-bit layout counts, witness metrics for n=4..6, and both audio files on repeat execution. SHA-256: two-locality-objectives.wav 49154667f653c957d448fa84323e1a2c9214ec1bcd295bd87241fdc888c9ff48; one-bit-neighbour-trip.wav 407e57f33c0db72110c1ab6a6bce53d216f66330826254a5917f278e4e520ba7. No independent human reviewer, production UX test or live research-registry change. Native Node clean-checkout execution and repository-wide CI must be qualified separately.

## Exaptation

Use the bounded solver as a preset-order compiler, regression oracle for scalar encodings of multi-feature states, adversarial test generator for navigation structures, or composition tool for visiting a configuration space in a controlled order. A practical alternative may be a two-axis or direct-access interface; our bound does not constrain those. Future falsifier: find a smaller Gray B in a dimension n>=6; test weighted, circular and duplicated-state models separately. The distinction between adjacent dial positions and adjacent configurations is the actual transferable result.
