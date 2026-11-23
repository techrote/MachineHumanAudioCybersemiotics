# The Question That Erases Its Answer
**Expedition #203 | 23 November 2026 | original bounded formal model and artistic instrument**

## The anomaly

An instrument can truthfully answer a diagnostic question while destroying the evidence needed to answer the next one. The question can improve knowledge of a past state and simultaneously reduce its future recoverability. A successful reset can even make the present state perfectly known while rendering its origin unknowable.

A plausible engineering example is a diagnostic register whose first read clears an entire bank of latched signals. Reading a specific bit is not the same operation as obtaining an atomic snapshot. This is a hypothetical register, not a claim about any particular device or hardware standard. An analogous machine voice could announce a truthful status and then acknowledge/clear the record. A second query would describe an altered record. Nothing needs to be false for the final inference to fail.

This is the difference between a question as a partition of an unchanging world and a question as an intervention in the world. The latter may be modeled as a sequential experiment.

## Lineage and disciplinary boundary

Edward F. Moore, *Gedanken-Experiments on Sequential Machines*, in Shannon and McCarthy (eds.), *Automata Studies* (1956), pp. 129–154, [DOI](https://doi.org/10.1515/9781400882618-006), [accessible scan](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf). Read printed pp. 129–131, including the diagrams on pp. 130–131, using extracted text and visual page inspection. Moore's introduction defines deterministic finite machines; the experiments section distinguishes fixed and output-contingent input sequences and experiments with several identically initialized copies. The examples explicitly consider experiments that destroy access to future information. This is direct mathematical ancestry, not a novel discovery of the phenomenon. Full chapter not reviewed or redistributed.

Lee and Yannakakis (1994), *Testing finite-state machines: state identification and verification*, IEEE TC 43(3), 306–320, [DOI](https://doi.org/10.1109/12.272431): bibliographic identification only through DBLP; the original was not read. Hierons, Jourdan, Ural and Yenigun (2008), [*Using adaptive distinguishing sequences in checking sequence constructions*](https://doi.org/10.1145/1363686.1363850), abstract inspected on the ACM record, establishes that the literature already distinguishes preset and adaptive distinguishing sequences. Van den Bos and Vaandrager (2019 preprint), [*State Identification for Labeled Transition Systems with Inputs and Outputs*](https://arxiv.org/abs/1907.11034), abstract inspected, discusses the more general input/output transition-system setting and the possibility of no suitable adaptive test. Do not attribute the implementation here to these authors or claim state-of-the-art complexity.

J. L. Austin, *How to Do Things with Words*, second edition (1975), [Oxford Academic book abstract](https://doi.org/10.1093/acprof:oso/9780198245537.001.0001) and [Lecture IX abstract](https://doi.org/10.1093/acprof:oso/9780198245537.003.0009). Publisher-provided abstracts were visible in search retrieval; direct retrieval of the lecture abstract later failed. No full lecture reading. Austin's analysis distinguishes acts done through language from effects on the hearer. This offers a useful interpretive contrast: an interrogative may participate in a conventional action, while the register example has a mechanically specified side effect. Neither is proof that all speech acts are finite-state transducers, that questions necessarily erase memory, nor that socially consequential utterances are mechanically deterministic. The analogy is deliberately non-identical.

## Three indistinguishable endings

Let each possible initial register contain two binary fields:

| Origin | q0 | q1 |
|---|---:|---:|
| A | 1 | 0 |
| B | 0 | 1 |
| C | 0 | 0 |

The operation q0 or q1 returns the corresponding bit and clears the entire register to a common state S. All later probes return an identical empty symbol. All pairs are individually distinguishable: A/B by q0, A/C by q0, B/C by q1. But no single adaptive experiment can distinguish all three.

If q0 comes first, B and C emit 0 and both reach S. If q1 comes first, A and C emit 0 and both reach S. Neither remaining pair can ever be separated, regardless of later questions. Thus the proposition "for each pair, there exists an experiment that distinguishes it" does not imply "there exists a single experiment that distinguishes all pairs." A bank of identically initialized copies, if legitimately available, changes the experiment and makes the combined observations informative. Merely resetting to S does not provide such a copy.

There is an exact contrast in what is known. Before the query the current and initial states are uncertain. After the query the current state is known (S), but in at least one branch the initial state is not. A diagnostic report must specify which state it is about.

### General impossibility certificate

Let deterministic transition T(s,a) = (y,s') and belief B contain pairs (i,s) of original candidate i and its current state s. The pair list retains initial identities even when several candidates reach one state. Suppose a reachable belief contains (i,s) and (j,s) with i different from j. Both produce the same next observation and successor for each admissible input; induction gives identical future traces for any fixed word. For an adaptive policy, identical observations select identical subsequent inputs, so the induction also holds. The two initial identities are irrecoverable under the declared experiment. This does not rule out external logs, independent copies, new sensors or altered experimental permissions.

A different criterion, current-state identification, can accept such a merged belief. That is not an error unless substituted for the original objective.

## Exact policy, not greedy entropy

The supplied Python oracle builds the finite graph of reachable beliefs. A probe is admissible only when defined for every candidate's current state. Its observation-indexed successors keep original candidate tags. No missing transition is treated as an ordinary observation. Goals can be origin identity or current-state identity.

Let W0 be the terminal beliefs. Recursively add a belief to W(k+1) if it is already in Wk or if there exists an admissible probe for which every possible observation successor belongs to Wk. By induction Wk is exactly the set with a guaranteed terminating policy of worst-case length at most k. The first entry rank is therefore the optimal worst-case number of probes, and choosing a probe whose successors have smaller rank yields a policy. Finite graph exhaustion with no new beliefs is an impossibility result for finite guaranteed termination under these assumptions. Infinite loops are not successful policies.

For m original candidates and n finite current states, there are at most (n+1)^m possible partial origin-to-state mappings, including the empty mapping (not reached in this model). This deliberately exponential reference method is not a production test-generation algorithm. Assumptions: known deterministic table, exact observations, no unmodeled transitions, no noise, no external evidence and unit query costs. Any use with actual systems would need a separate model and validation.

A locally uninformative probe can be essential: "prepare" returns the same symbol for A and B but moves them to distinguishable states X and Y; "read" then separates them. Thus a strict positive-immediate-information heuristic is incomplete even without stochastic uncertainty. Conversely a high-information destructive probe can lose options. For four candidates, imagine an immediate balanced bit that clears the bank; two bits that could otherwise be read persistently yield a complete identity in two reads. The first probe cannot be chosen merely because its initial partition is balanced. The oracle's rank treats future recoverability as decisive, not an extra rhetorical disclaimer.

A second example splits four candidates into left and right branches. A branch-specific second query is allowed only in that branch. An adaptive strategy wins in two queries while no single universally admissible preset word can identify all four. This is a control against the overbroad conclusion that state-changing probes are invariably harmful.

## Exhaustive fictional family and acoustic witness

Enumerate all labelled assignments of two bits to n candidates. For n=3 there are 2^6=64 assignments; for n=4 there are 2^8=256. In each family, pairwise distinguishability holds exactly when rows are all distinct. A persistent memory permits both probes and therefore identifies the origin in exactly those assignments. A single binary destructive probe cannot distinguish more than two candidates; later probes give no information. Analytically, the distinct-row count is 4!/(4-n)! = 24 for both n=3 and n=4.

An independently executed JavaScript enumeration of row signatures and single-query partitions in this session yielded:

| n | Matrices | All pairs distinguishable | Read-once full identification | Persistent full identification | Pairwise-to-global gap |
|---|---:|---:|---:|---:|---:|
| 3 | 64 | 24 | 0 | 24 | 24 |
| 4 | 256 | 24 | 0 | 24 | 24 |

These are finite exhaustive counts, not prevalence estimates. The Python implementation independently builds the belief graphs for every row matrix; its own execution awaits exact-head CI at this checkpoint. The test bridge asserts the independently calculated totals and checks negative cases. No sampling, statistical uncertainty or human performance metric applies.

The original "read-once organ" is a tiny deterministic PCM synthesizer. It maps each probe and its returned symbol to successive integer triangle-wave pulses. The transcript q0=0, q1=empty is identical for B and C in the destructive memory; hence the deterministic renderer must produce exactly identical PCM. Under the persistent control q0=0, q1=1 differs from q0=0, q1=0, and the tests demand different PCM. This is a constructive illustration of the irrecoverable origin distinction, not a claim that listeners can discriminate the resulting sound or should be trained to do so. No borrowed sound, model-generated human data or playback study.

Run from repository root:

    python3 research/expeditions/question-that-erases/oracle.py --wav-dir /tmp/mhac-read-once
    python3 -m unittest discover -s tests -p test_expedition_question_that_erases.py -v

The CLI emits trace identities and PCM SHA-256 values and writes four WAVs on demand; the tests inspect PCM bytes, not human listeners. WAVs are generated rather than stored in the repo.

## Transfer and speculative afterword

Potential design exaptation: explicitly classify interface operations as nonmutating observation, observational mutation (read-clear), acknowledgment, reset, irreversible commit or other declared state change. Retain operation ID, before/after record version and observation scope. An atomic snapshot or auditable log may recover the original distinctions that a read-once interface loses. Repeating a voice message is not equivalent to repeating the original measurement. This is a proposed contract, not a validated safety policy. A snapshot itself can be incomplete or unauthorized; recovering the original state is not always necessary, and a known safe present condition may be the actual goal. Conversely, current-state convergence alone cannot prove the original situation was benign.

MHAC contrasts: #201 selects questions over a static candidate set and acceptable actions, whereas here the experiment transforms current state and can erase future distinctions between origins. #195 concerns joint feasibility from coexisting marginal summaries; here the summaries are obtained sequentially from changing registers. #199 studies static feature collisions; here the collision persists because the experiment coalesces states. #187 treats absent observations, #188 non-invertible actions, #56 message retraction and #178 hidden context. None is modified or claimed superseded. R005/R006/Track G and participant gates are untouched. The extension is not evidence for a Brier thesis or a claim to academic novelty.

*Fiction — The archivist's organ.* An archivist built a keyboard with one pipe for every question. Each pipe read a small part of a wax cylinder, then melted the whole cylinder. The instruments were wonderfully precise. A listener could distinguish every pair of cylinders if told in advance which pair might be present. Yet the archivist could not play a tune that identified every cylinder. He repaired the instrument by adding a second manual that made a copy before asking. His assistant, who was less fond of certainty, asked whether a copy was what they were authorized to make. The organ remained silent for a while; this time silence was a decision, not a missing measurement.

*Claim ledger:* finite proofs and counting are mathematical; the executed JavaScript enumeration is synthetic computational evidence; the PCM construction is art and a deterministic model witness; Austin and Moore comparisons are bounded interpretation of cited material; the organ story is fiction. No human evaluation or independent reviewer is claimed. AI-authored expedition. Base at reconciliation: 495a98ca12bae467a507031f04931aa4254b1866. Review and landing depend on exact head checks.
