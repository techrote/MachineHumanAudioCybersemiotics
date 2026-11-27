# The Composer Who Reviews Her Own Disappearance

Exploratory expedition, 2026-11-27, [issue #778](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/778). AI-assisted research and original synthetic art; no independent human review, participant data, empirical promotion or claim of machine consciousness. Draft/HOLD for independent integration.

## A salon with no chairman (original fiction)

The composer invents three critics. The Surveyor dislikes distance; the Spark dislikes recurrence; the Archivist dislikes revision. They are invited to alter the same six notes. Each is allowed one adjacent exchange, and every intervention must improve the intervening critic's own criterion. After six alterations the original composition returns. The publisher prints a certificate of improvement after every alteration. Nothing on the certificates is false, except the implication that they describe a common direction.

A fourth person arrives, the reader. She requests not the final edition but the six reviews, with their attached musical drafts. The composer's disappearance is not a deletion: it is the withdrawal of the demand for one final authorial verdict.

## Sources and reading record

- Fernando Pessoa, letter to Adolfo Casais Monteiro, 13 January 1935, [Martin Earl translation, Shantarin](https://www.shantarin.com/page/fernando-pessoa-s-letter-on-the-genesis-of-the-heteronyms). Read the passages beginning with the genesis question, the account of Caeiro and his disciples, the fictional circle and aesthetic disagreements, the retrospectively written Opiary, and the different writing practices (web text lines 179–211). Pessoa describes writing distinct literary figures with relationships, histories and conflicting judgments. His account is retrospective self-description, not a verified chronology of composition or clinical evidence. His own period-specific psychiatric language is not adopted. The Casa Fernando Pessoa indexed Portuguese passage and Richard Zenith translation (Selected Prose, 2001, pp. 256–257) were consulted as discovery cross-checks; direct museum URLs failed/redirected. No manuscript inspection.
- Tobias Hermans, “Poetics of the Periodical Paratext: Editorial Footnotes and Reader Agency in Robert Schumann’s Davidsbund Writings,” Colloquia Germanica 49(2–3), 2016, 157–175. [Institutional record and abstract](https://biblio.ugent.be/publication/8054392); [publisher indexed text](https://elibrary.narr.digital/xibrary/cg20162-30157), especially the discussion of the Schwärmbriefe and the Museum and Hummel reviews (pp. 162 onward), and conclusion (around p. 170). The indexed passages describe conflicting fictional critics and an editorial apparatus which does not settle their disagreements. Direct publisher retrieval redirected; no claim of full-text or image inspection. No primary Schumann journal or score read. Hermans's interpretation of the role of the reader is an important precedent for making editorial mediation itself material.
- Kivanc Tatar and Philippe Pasquier, “Musical agents: A typology and state of the art towards Musical Metacreation,” Journal of New Music Research 48(1), 2019, 56–105, [institutional abstract and metadata](https://research.chalmers.se/en/publication/540194), DOI 10.1080/09298215.2018.1511736. Abstract read; reviews musical agents and evaluation. Multi-agent musical generation is established, not a novelty claim here.
- [Personalising behaviours of the multi-agent autonomous looper with a corpus of annotated co-performances](https://www.cambridge.org/core/journals/organised-sound/article/personalising-behaviours-of-the-multiagent-autonomous-looper-with-a-corpus-of-annotated-coperformances/67B6A53D2F8A30064203A0E2EF5E4FDA), publisher-indexed abstract only: reports tailoring system behaviour to musicians' objectives and a five-musician study. A substantial alternative to arbitrary hand-written aesthetic critics. No extrapolation of its reported findings to this model.

All source reading by one ChatGPT agent in this run. No third-party prose reproduced; no license or permissions asserted. The sources are not canonical evidence records.

## Interpretation: style is not a voice preset

A heteronym is interesting here not because its utterance sounds different, but because it has different commitments about what ought to happen next. One could implement a synthesizer with twenty timbres and only one compositional judgment, or a synthesizer with one timbre and several incompatible aesthetic practices. The latter is the more interesting experiment.

Pessoa's invented retrospective Opiary also suggests the possibility of editing the fictional history of an instrument: write an earlier patch for a character before its supposed encounter with another. This need not be a claim about actual software history. Preserve separate fictional chronology and execution provenance. An influence can be authored as fiction; a causal dependency in a real run requires evidence.

Schumann's critical fiction offers another distinction: the mechanism that frames a discussion need not be the speaker that decides it. A future interface might make the editorial layer explicitly manipulable, and the reader/performer could choose which disagreement to develop. It should never imply that three rule sets implemented by the same author amount to three independently verified external opinions.

## Executed construction

Run python laboratory.py using Python 3.11+ with the standard library. The only source material is a six-token multiset 0,0,1,2,3,3. A draft is an ordering of that material. Critics inspect it through deliberately crude integer objectives, all minimized:
- Surveyor: total absolute difference between adjacent pitch indices (not semitones or a perceptual distance).
- Spark: number of identical adjacent pitch indices (not general repetition).
- Archivist: positional Hamming distance from the original seed (not fidelity in a historical or ethical sense).

Each turn selects the adjacent swap strictly improving the active critic's cost most, ties broken lexicographically; otherwise passes. Round-robin order is part of state. The second policy additionally requires every other cost to be non-increasing. We distinguish an unchanged score with cycling turn labels from a genuinely changing cycle.

Witness seed 003123, order Surveyor/Spark/Archivist:

| Turn | Editor | Draft | Cost vector (distance, adjacency repeats, seed deviation) |
|---|---|---|---|
| 0 | original | 003123 | 7,1,0 |
| 1 | Surveyor | 001323 | 5,1,2 |
| 2 | Spark | 010323 | 7,0,3 |
| 3 | Archivist | 001323 | 5,1,2 |
| 4 | Surveyor | 001233 | 3,2,3 |
| 5 | Spark | 001323 | 5,1,2 |
| 6 | Archivist | 003123 | 7,1,0 |

All six edits strictly improve their author's cost; the full state returns after six turns. A single scalar potential strictly decreasing on every such transition cannot exist, since following the cycle would imply it strictly decreases to its own initial value. This does not refute scalar optimization generally; it refutes that particular representation of these edits.

The unanimous guard cannot sustain a changing cycle: the integer sum of costs strictly decreases on every accepted move. In this census the guard is actually much more restrictive: every trial starts at the Archivist's exact seed, so no distinct draft can pass its no-worse requirement. The result is paralysis, not evidence of consensus. A non-seed initial draft or relaxed archival criterion is a valuable next experiment.

## Native finite census and artistic render

180 distinct permutations of the multiset, six turn orders each, 1,080 trials per policy. Ordinary: 66 fixed-draft cases (three-turn phase cycles), 942 changing period-three, 69 changing period-six, three changing period-nine. Guarded: 1,080 fixed-draft cases, all phase period three. Counts are exhaustive over this stated population, not rates for real music or critics. Local improvement is not convergence, and stasis is not endorsement.

Native Python 3.13.5 executed twice. Assertions check immutable inventory, legal moves, active objective strict improvement, guarded monotonicity, bounded augmented state and exact witness; WAV metadata and complete PCM readback checked. Same-runtime SHA-256 receipts and files identical across executions. Local source git blob 732f5103b9e9645ff768db4d691dbbbfb2813b5c. Full repo CI not locally run.

Four original mono 16 kHz PCM recordings generated offline (not committed binaries): salon-cycle.wav (seven successive drafts including the return, 8.4 s), unanimous-refusal.wav (seven copies of the seed, 8.4 s), surveyor.wav and spark.wav (one draft each, 1.2 s each). Same immutable 200 ms oscillator tiles at 220, 261.626, 329.628, 440 Hz. No human audition experiment. Execute the script to regenerate audio and receipt. The musical piece is the sequence of reviews rather than a single supposedly improved result.

## Further artistic work: the editorial surface

Proposed Heteronym Salon VSTi: each critic owns a candidate generator and a declared objective, an immutable branch history, and a voice to audition its preferred alternative. A performer can grant editing turns, retain parallel drafts, swap evaluators, change constraints, and play a cycle as a phrase. Independent preview avoids destructive overwrite. VSTfx: edit annotated segments only with explicit boundaries and dry preservation. CYD: an XY interface selecting critic and draft lineage, with a visible vector of costs and a cycle marker; no claim of physical implementation. FM-1: small fixed-memory permutation of FM gesture tiles. Hardware needs bounded queues, storage and audio-callback costs, none qualified here.

A more ambitious design would give fictional critics influences and biographies, so that their own criteria evolve through encounters. Preserve versioned criterion definitions; otherwise apparent improvement may merely reflect a changed evaluator. A branch graph need not be an optimizing machine: one may perform the incompatible versions in counterpoint. The guard is useful as a warning, not as an artistic mandate.

## Operational distinction and counterargument

For MHAC, a claim of improvement must include its criterion, baseline, scope, and evaluator. A shared implementation can produce several disagreeing evaluations without independent evidence. The strongest conventional comparator is a typed review ledger retaining per-criterion deltas, underlying test evidence and acceptance conditions. Future synthetic tasks could compare that ledger with a scalar score and optionally acoustic disagreement cues, measuring correct rejection of false convergence, abstention, workload and decision latency separately. No acoustic benefit or participant response demonstrated.

A critic is not merely an objective function. A person's taste can change, be inconsistent or be irreducible to a metric. The model deliberately makes those complications absent. Nor is disagreement valuable by itself; an operational safety gate cannot be made an aesthetic preference. For real-world tasks, acceptance criteria and evidence authority remain separate from optional artistic play. The point is not to recreate Pessoa in software but to make differing compositional commitments explicit and performable.

## Reconciliation and scope

Read current main AGENTS.md, README, research README, RAG, programme, runbook, research integrity and validation. Live recent 35 PR titles and 25 open issue titles reviewed; targeted searches for heteronym, Pessoa, Schumann, critics, Pareto, editorial cycle and adjacent swap. No direct heteronym overlap returned; search not exhaustive. Adjacent existing #228 scalar ranking/cycle compression, #471 open form and #692 scordatura differ in scope; this contribution is a revision dynamical system with explicit fictional critics and branch preservation. No claim of research priority. Earlier search directions anamorphosis, hysteresis, hocket, anagram and prosopopoeia have existing expeditions and were not duplicated. New branch from main; disjoint additive files only; no frozen protocol, registry, shared manifest, external outreach or merge. Integrator owns acceptance and landing.
