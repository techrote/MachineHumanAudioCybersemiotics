# The Sleeping Commutator

**Refs #207 · 23 November 2026 · exploratory mathematics / original synthetic audio · not Track E/G evidence.**

## Question

Two individually reversible controls can agree in both orders on the factory preset and nevertheless disagree after a history of other control operations. How many preparatory operations can conceal the discrepancy? Can we extract a shortest reproducible counterexample instead of merely labelling two controls "noncommuting"?

This is a distinct question from #188 (whether a palindromic event sequence restores state), #183 (whether ordering is warranted by a partial causal record), #205 (trace equivalence and choice) and #199 (collisions in signal descriptors). Here the state and operations are fully specified and the target is endpoint equivalence under interchanging actual adjacent operations. No change to the core programme, frozen records or other branches is proposed.

## The exact finite model

Let A and B be permutations of n labelled states; execute event words from left to right. For a known starting state s, let R be the states reachable by finite words in A and B, including the empty word. Define D as the set of x in R for which B(A(x)) differs from A(B(x)). A test of AB against BA at s checks only whether s is in D. A breadth-first search over R gives the shortest prefix w that reaches D, if any. The certificate consists of the prefix, reached state and both complete state paths for wAB and wBA.

If D is empty, all adjacent A/B swaps in any reachable context preserve the endpoint, because their prefix reaches R and any identical suffix then acts deterministically on the same resulting state. Repeated swaps prove endpoint equality for any two words with equal multiplicities of A and B. Conversely, endpoint equality for every such pair of words implies D is empty by considering wAB and wBA. This is not equality of intermediate paths, timing, audio, logs, or externally visible effects.

### Sharp bound

**Proposition.** If D is nonempty, the shortest preparation depth d satisfies d <= |R|-3 <= n-3.

Proof: Since R is finite and closed under A and B, their restrictions are injective self-maps and therefore bijections. Write P=B∘A and Q=A∘B on R. Then Q inverse composed with P is an even permutation: sign(P)=sign(Q), so their quotient has positive sign. Its moved points are precisely D. A nonidentity permutation cannot move just one point, and one moving just two points is a transposition (odd). Thus |D| >= 3. A shortest directed path from s to D has d distinct preparatory states outside D: a repeated state could be deleted together with its intervening loop. Therefore d <= |R|-|D| <= |R|-3.

**Sharp construction for every n >= 3.** Let A exchange n-2 and n-1, fixing every other point. Let B cycle 0,1,...,n-2 and fix n-1. Start at 0. Direct evaluation gives disagreement exactly at n-3,n-2,n-1. Until state n-3 is reached, A does nothing and B increments the state by one. Hence the first disagreement needs n-3 copies of B; all n states are reachable. The bound is attained. For n=3 this means immediate disagreement; no hidden witness can exist for n<=3.

For an eight-state instrument the two compared paths are:
 
    BBBBBAB: 0 1 2 3 4 5 5 6
    BBBBBBA: 0 1 2 3 4 5 6 7

At state 0 the nominal AB and BA tests agree. After five B operations the same comparison diverges. Both controls remain reversible throughout.

### Boundary counterexamples

- Global disagreement is not necessarily reachable: A=(0,2,1,3) and B=(0,1,3,2), expressed as image tuples, fix 0 while disagreeing on 1,2,3. A test restricted to the start orbit legitimately certifies endpoints there, not globally.
- Nontrivial commuting maps exist: rotations by one and two positions on a four-state cycle commute everywhere.
- The sharper bound relies on permutations. For arbitrary total maps on three states take A=(0,0,2), B=(2,0,1). At 0 both orderings end in 2, but after B reaches 2 the two outcomes differ: B(A(2))=1 and A(B(2))=0. Depth 1 exceeds n-3=0. The implementation rejects nonpermutations rather than silently applying the proof.
- A and B commuting on all reachable states does not certify order invariance of intermediate outputs. Even two commuting nontrivial rotations can produce distinct state paths.
- Adding another operation C may enlarge R and invalidate a previously scoped certificate. An incomplete state description, resets, partial maps, concurrent observers or side effects require another model.

## Executable experiment

[commutator.py](commutator.py) uses only the standard library, enumerates all ordered pairs of labelled permutations for n=2..6, and fixes start=0 (other single starts are equivalent by relabelling). Counts are not weighted by realistic controller distributions; they are finite census results. The unreachable-disagreement column is a subset of reachable-equal, not a fourth disjoint outcome.

| n | Ordered pairs | Immediate disagreement | Hidden disagreement | Reachable equal | Unreachable disagreement subset | Max hidden depth |
|--:|--:|--:|--:|--:|--:|--:|
| 2 | 4 | 0 | 0 | 4 | 0 | none |
| 3 | 36 | 18 | 0 | 18 | 0 | none |
| 4 | 576 | 384 | 54 | 138 | 18 | 1 |
| 5 | 14,400 | 10,800 | 2,088 | 1,512 | 672 | 2 |
| 6 | 518,400 | 414,720 | 73,920 | 29,760 | 21,840 | 3 |

Total: 533,416 ordered pairs. At n=6, 68,160 hidden cases have depth 1, 5,040 depth 2, 720 depth 3. Of 103,680 nominal-equal pairs, 73,920 are hidden failures in their reachable set. This is a combinatorial proportion, not an estimated engineering failure rate.

Reproduce from root:

    python research/expeditions/sleeping-commutator/commutator.py --out build/sleeping-commutator
    python -m unittest discover -s research/expeditions/sleeping-commutator -v
    python -m unittest discover -s tests -p test_sleeping_commutator.py -v

## The score and possible exaptations

Each state gets a triangle oscillator at 180+40s Hz. The two channels render the two state paths with identical timing, integer-only synthesis, 180 ms tones, 40 ms gaps and fades. The nominal-control render has identical initial and final state tones but different intermediate state tones (AB visits 0,0,1; BA visits 0,1,1). The main render shares the five-operation prelude and then separates, including its final state. This negative control is particularly important: audible path differences alone do not certify endpoint disagreement. This is a sonification convention, not evidence of human detection or musical meaning. Intermediate divergence is allowed; the theorem concerns endpoint differences. No borrowed samples or melodies.

Potential applications: shortest regression traces for parameter-order bugs; deciding when a scheduler can interchange two reversible commands within a known finite state orbit; adversarial fixtures for preset/undo machinery; and an instrument whose latent state determines whether swapping two gestures alters the final note. The latter is an artistic proposal, not an established synthesizer usability benefit. The proof is not a full partial-order-reduction algorithm and does not establish safety of arbitrary real systems.

A useful conceptual separation: reversible does not mean interchangeable; interchangeable at one state does not mean interchangeable after a history; endpoint interchangeable does not mean observationally identical.

## Provenance and qualification

- UCL, [MATH0005 Algebra 1, section 2.17](https://www.homepages.ucl.ac.uk/~ucahmto/0005_2021/Ch2.S17.html), Definition 2.17.2 and Lemma 2.17.5: multiplicative sign of a permutation. Consulted HTML section on 2026-11-23 for the standard algebraic lemma; the sharp delay argument above is derived here, without claiming priority.
- Kurshan, Levin, Minea, Peled and Yenigun, [EP0913781A2, Static partial order reduction](https://patents.google.com/patent/EP0913781A2/en), 1999, description paragraph defining independent transitions: the definition requires preservation of enabledness and agreement of orderings wherever jointly enabled. Relevant description passage consulted; no patent-status or legal interpretation, no full patent review.
- Godefroid and Wolper (1993), [Using Partial Orders for the Efficient Verification of Deadlock Freedom and Safety Properties](https://orbi.uliege.be/handle/2268/163844), DOI 10.1007/BF01383879. Repository metadata and abstract only read; context for partial-order methods, not an asserted source of the sharp bound or a full paper assessment.

AI-assisted expedition, implementation, proof and self-review by ChatGPT GPT-6.2, no external reviewer or participant. Base 495a98ca12bae467a507031f04931aa4254b1866. Python 3.13.5 on Linux: eight tests passed; word-enumeration cross-check independently enumerates prefixes for all 576 pairs at n=4; extremal family tested n=3..64; survey n=2..6 executed. The local run produced results.json SHA-256 fd5fbb7660e11c91627cde1070a1f12912f4d45ee41bbb4b29ef4c694a4c6e8f. WAV SHA-256: sleeping-commutator.wav 290424bbdb428566536b4f777e4c0c11abf89c6344a90c52deed52bd972644a2 (28160 frames); nominal-control.wav 690f48f2a46dcb2e43d1af657250ea01b70122a86b7f33717dc24c5059f5d471 (10560 frames). Both PCM16 stereo 16000 Hz. Source Git blob IDs: commutator.py f6a8ecefb66bb7cc0d0fe5266f5bf62945c8a6b0; test_commutator.py ccb14ffc0d9e3d64aaf2784a504c2a763e2aa0d4. Tests verify byte repeatability and compare stereo frame blocks. No human listening, formal proof assistant verification, or independent review claimed. External sources are linked rather than redistributed. No new licensing grant.
