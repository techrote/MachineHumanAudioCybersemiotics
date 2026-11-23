# The Choir That Cannot Meet

**Scope:** independent expedition, [issue #195](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/195). Original finite model and art, not Track E/G evidence. 23 November 2026. Base main: f0927fbf4b20bef2a04b6e1220c7c78edda40e01. One ChatGPT research agent; no independent human review or participant data.

## The anomaly

Every musician can attend some rehearsal. Every pair can attend some rehearsal together. Nevertheless, there may be no rehearsal that the entire choir can attend. This is not a question of a missing alarm, delayed observation, mistaken identity, or dishonest individual. Every report can be exactly true.

Let A_i be the set of candidates satisfying constraint i. The weaker statement is “for each i there exists a candidate in A_i”; the stronger one is “there exists a candidate in every A_i.” The strong claim implies the weak one, but the reverse is invalid. Pairwise intersection improves the report, but does not generally resolve it.

In MHAC terms, truthfulness of each audio utterance does not compose into the truth of an implicit global conclusion. This is a scope problem, not necessarily an acoustic discrimination problem.

## An exact pair of worlds

Four candidate opportunities in each world, three constraints. A bit indicates whether a candidate satisfies a constraint; identical rows would be permitted but are not needed here.

| World E (even parity) | World O (odd parity) |
| --- | --- |
| 000 | 001 |
| 011 | 010 |
| 101 | 100 |
| 110 | 111 |

Both have population four, two candidates satisfying each individual constraint, and one candidate satisfying each pair. Yet E has zero candidates satisfying all three and O has one. Indeed every two-bit projection has the same multiset (00, 01, 10, 11). The complete proper-conjunction summary is (4,2,2,1,2,1,1), in binary mask order.

The title's choir could be told that all the voices have partners and each pair can meet. The difference is whether their witnesses can be **bound to one candidate**. “All individually ready” is not “jointly ready.” Distinct reports of one sound/source (X008) are a different problem; here the constraints and the counts can be correct and nonduplicated.

### Arbitrarily many constraints

For n ≥ 2, consider all binary n-tuples of even parity versus all of odd parity. Both contain 2^(n-1) distinct tuples. For any proper coordinate subset of size k, every fixed assignment to those k coordinates has exactly 2^(n-k-1) extensions in each world: choose all but one remaining bit freely and force the last by parity. Thus even complete proper-coordinate marginals cannot distinguish the worlds. Exactly one parity class contains the all-ones tuple.

Consequently no decoder of those summaries alone can always decide existence of a common witness. This is a finite indistinguishability proof, not a claim of newly discovered parity mathematics. Random guessing cannot be correct with probability one on both equal inputs. The summary is informative about many other questions; its loss is specific.

## The useful reversal: exact bounds instead of universal abstention

Let h(T) count candidates whose exact satisfied constraint set is T. Let m(S) count candidates satisfying at least S, so m(S) = sum of h(T) over T containing S. m(empty) = population. Supply every m(S) except m(U), where U is the full constraint set. Denote the missing count x.

By inclusion-exclusion, each exact cell is

    h(T) = sum over S containing T of (-1)^(|S|-|T|) m(S)
         = a(T) + (-1)^(n-|T|) x

where a(T) is the inversion with the missing entry set to zero. The first identity follows because the coefficient of h(V) in the nested sum is the binomial expansion of (1-1)^(|V|-|T|), hence zero unless V=T.

For each T with positive sign, nonnegativity imposes x ≥ -a(T). For negative sign, x ≤ a(T). Also 0 ≤ x ≤ m(empty). Their intersection is an inclusive integer interval [L,H]. If L>H the input cannot be realised by any nonnegative integer histogram. Conversely every integer in [L,H] yields one such histogram by inversion and reconstructs precisely the given proper counts. This proves sharpness, not merely a loose inequality. IDs are not recovered; histogram counts alone cannot identify a particular candidate.

The executable oracle uses a fast subset transform, O(n 2^n) arithmetic, and refuses n outside 1..12 to bound memory. Input is exact nonnegative integer conjunction counts, not percentages, noisy sensors, arbitrary inconsistent denominators, or rounded estimates. A shared candidate universe and consistent constraint meanings are mandatory.

| Interval | Meaning |
| --- | --- |
| H = 0 | Common witness impossible in this model |
| L > 0 | At least one common witness guaranteed; no identity provided |
| L = 0, H > 0 | Undetermined |
| L > H | Invalid/inconsistent input; do not emit a conclusion |

For two constraints with population N, individual counts a and b, this reduces to max(0,a+b-N) ≤ x ≤ min(a,b). With N=3, a=b=2, a witness is guaranteed without the omitted joint count; requiring a full report would be wasteful if existence were the only question. With N=3, a=3, b=2, the count is exactly two. With a=0, it is impossible. Thus the strongest useful engineering result is **conditional sufficiency**, not a doctrine that every summary is defective.

Another positive countercase: if all nonempty opportunity sets are closed intervals on a common line, pairwise intersection implies global intersection. Choose the greatest left endpoint and smallest right endpoint; pairwise intersection between the intervals supplying those extrema ensures they are ordered. Arbitrary disconnected availability windows do not obey that premise. Do not assume a calendar consists of single intervals.

### A sharp population threshold for hidden conjunctions

There is a further consequence of the one-dimensional kernel. Let two compatible histograms have joint counts x and x+d, where d>0. Their cell differences alternate between +d and -d, with exactly 2^(n-1) cells of each sign. Nonnegativity forces the first histogram to have at least d candidates in every cell that decreases. Hence N ≥ d 2^(n-1).

Taking the extreme compatible histograms gives the sharp uncertainty-width bound H-L ≤ floor(N/2^(n-1)). In particular, if N < 2^(n-1), complete proper conjunction counts determine the missing full count uniquely (or are inconsistent). This does not mean a low-order summary, such as pairwise counts alone for n>3, is sufficient. The parity examples attain the bound: repeat each parity tuple q times and add the same r arbitrary candidates to both worlds, with N=q 2^(n-1)+r and 0≤r<2^(n-1). Their full counts differ by q, achieving the upper bound. No probabilistic independence assumption is used.

Thus a small candidate population can defeat the apparent worst-case marginal alias. For six constraints the full proper summary has 63 entries, yet hidden joint-count ambiguity requires at least 32 candidates. One would generally rather send the conjunction count than all 63 entries; the result is a compression diagnostic for situations where the proper counts already exist, not a recommendation to generate them.

## Source lenses and reading boundaries

Access date 2026-11-23. No third-party text or audio copied into this expedition; bibliographic links only.

- Katalin É. Kiss and Jürgen Pafel, *Quantifier Scope Ambiguities*, 2017, [publisher abstract](https://doi.org/10.1002/9781118358733.wbsyncom005), abstract paragraphs 1–2. Read abstract, not full chapter. It identifies scope interactions and emphasizes that multiple operators do not guarantee ambiguity. This warns against claiming every sentence with quantifiers has two legitimate readings. The formal example here is stipulated, not extracted language data.
- [Quantifiers and Quantification](https://plato.stanford.edu/entries/quantification/), Stanford Encyclopedia of Philosophy, introductory discussion and §1.1, revised 2022. Read those passages only. Classical quantifier notation and variable binding provide the notation used here; the quantifier swap counterexample is explicit reasoning.
- Scott AnderBois, Adrian Brasoveanu and Robert Henderson, *The Pragmatics of Quantifier Scope: A Corpus Study*, SuB 16 (2012), pp. 15–28, [author's publication page, abstract](https://anderbois.github.io/publications.html), and [proceedings landing page](https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/view/407). Read author-hosted abstract and metadata, not paper. The authors report effects of lexical choices, linear ordering and grammatical function in a logic-puzzle corpus. Neither that corpus nor its reported findings validate spoken machine instructions; publisher metadata cites a later online posting date.
- Elias Koutsoupias, [Probability and Computing, Oxford 2016–17, Lecture 18, Pairwise independence / Bits for free](https://www.cs.ox.ac.uk/people/elias.koutsoupias/pc2016-17/lectures.html). Read the two named subsections. The notes construct XOR-based pairwise-independent variables without full independence. This is the mathematical lineage for the parity example; the all-proper-marginal proof above is supplied directly.
- Eric Gottlieb, *Inclusion-Exclusion and the Topology of Partially Ordered Sets*, 2009, pp. 293–302, [publisher summary](https://doi.org/10.5948/UPO9780883859742.036). Read summary/intro only. It identifies inclusion-exclusion as Boolean-lattice Möbius inversion. The complete proof for our finite bounds is above rather than asserted on the authority of the unread chapter.
- Batya Kenig and Nir Weinberger, *Quantifying the Loss of Acyclic Join Dependencies*, PODS 2023, [author preprint](https://arxiv.org/abs/2210.14572), abstract only. They study loss of joining projected relations, including extraneous tuples. This is an analogy to global reconstruction from local projections; our bound is not their KL-divergence result. If shared candidate IDs are retained, intersecting those IDs can be lossless for this particular predicate; marginal counts deliberately discard them.

These sources establish conceptual ancestry, not an exhaustive novelty search or empirical synthesis. No human validation or Brier endorsement is claimed.

## Reusable communication contract

For a finite, well-defined candidate cohort, a reporting agent should distinguish:

- Local existence: constraint A has a witness (possibly different from B's).
- Joint existence: a single candidate satisfies a named constraint set.
- Joint count bound: an interval tied to a declared cohort, constraint versions and summary method.
- Joint witness: a named candidate verified against the entire constraint set at the specified snapshot.

For example, “All checks have passed individually; no common build revision verified” is useful and less misleading than “ready.” A system may report joint existence from a strictly positive lower bound without pretending to have a named build. A named witness requires identity-bearing evidence. In the software example, missing run identity, differing environments and moving revisions can invalidate the common-universe premise even before the maths applies.

Potential application to MHAC itself: three agents may each report progress on evidence retrieval, analysis, and software readiness, but no common claim revision may satisfy all three. This is a hypothetical workflow pattern, not an accusation about any actual MHAC PR. A minimal proof-carrying acceptance record could bind every required test to the same commit, dataset and environment identity; separate records may still be retained as useful partial progress.

Negative result: adding every possible lower-order combination is exponentially costly and still may fail. Often the right summary is directly to evaluate the target conjunction at source, provide a witness ID, or ask a targeted question. Lower-order bounds are attractive only if richer data cannot be exposed or the counts already exist. Do not treat marginal statistics as a substitute for traceability, permission or freshness. No automatically chosen abstention policy is safety-qualified.

## Sound work: four rehearsals that never happen together

The original integer triangle-wave instrument in [choir.py](choir.py) emits one 100 ms pulse per conjunction count in a fixed order. Count controls oscillator period. Proper summaries of E and O create byte-identical 0.7 second PCM wave files; adding the full joint count gives contrasting 0.8 second files. The program computes SHA-256 of the exact output, and tests assert identity and nonidentity. It does not test whether a human can hear or interpret the difference, and the sound encodes counts rather than real choir schedules.

Run from repository root:

    python3 research/expeditions/choir-that-cannot-meet/choir.py --out build/choir
    python3 -m unittest discover -s tests -p 'test_expedition_choir_joint_witness.py' -v

Generated WAVs are intentionally not committed; deterministic integer arithmetic avoids floating-point cross-platform synthesis differences. The exact receipt prints on execution.

A separate JavaScript enumeration executed during this research run used direct sums over all masks and explicit inclusion-exclusion rather than the Python subset-transform implementation. It examined all 1,287 nonnegative histograms on eight cells with population 0 through 5, yielding 1,278 distinct proper-summary groups, nine of which admitted more than one joint count. Every group's observed count set matched the calculated interval (zero mismatches). This is a same-agent cross-implementation numerical check, not independent review. Python and repository-wide CI are separate qualification steps.

## Speculative afterword (fiction)

The choir rehearsed in pairs. Each dyad reported its attendance honestly. A machine collected the reports and produced the same short melody every evening. The conductor interpreted the little cadence as the sound of the ensemble.

There was no dishonest singer, and no false note. There was a missing quantifier.

One day the machine added a final tone, the one belonging not to any singer or pair but to the possibility of everyone being there at once. On one evening it sounded different. The conductor had previously heard a perfect inventory of relationships and mistaken it for a gathering.

A synthesizer could treat conjunctions as a new layer of control: not merely an amplitude for each oscillator, but an oscillator for the intersection of their permitted states. Perhaps the absent tutti should be an explicit voice rather than an inference from the presence of other voices. This is an artistic suggestion, not a listener study.

## Separation and open questions

X001 concerns observation maps over hidden dimensions; X003 chronological ordering; X007 incompatible signed-graph assertions; X008 evidential ancestry; T004 binding and T011 modes. Our shared-witness problem is distinct but compatible with those research motifs. In particular, parity here is used to build **two feasible histograms**, not to certify an inconsistent signed cycle.

Would sparse higher-order queries yield tighter decision-relevant bounds under realistic resource budgets? What is the smallest reliable machine utterance that communicates the distinction between all-local and joint existence? Could a sonification expose a joint count without requiring listeners to mentally integrate many separate cues? None is answered by this finite proof. An empirical follow-up would need a protocol, real participants, appropriate approval and controls. Existing frozen programme and human gates remain untouched.
