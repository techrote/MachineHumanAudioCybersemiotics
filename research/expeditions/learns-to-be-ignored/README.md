# The Instrument That Learns to Be Ignored
## Estrangement, calm attention and change-budget counterpoint

**Expedition #430 | 2026-11-25 | Exploratory / noncanonical.** AI-assisted writing, source checking and synthetic analysis by GPT-6.2; no independent human review. Base main: 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, integrity and validation; reconciled 100 recent PR titles, 70 open issue results, new issue and comments. Targeted searches for defamiliarization, habituation, calm technology, estrangement and oddball returned no issue matches (not proof of absence). Nearby #303 treats exhaustion of novel sequences, #335 perceptual framing, #343 acoustic withdrawal, #407 directional difficulty. Here the unit is a change in a message's surface versus a change in what it denotes, and the central question is whether art and interface design should seek opposite relationships with attention. No protocol, shared manifest, evidence registry or production behaviour changed.

## Essay: two factories of perception

A conservatory commissions a bell that becomes more interesting every time it is rung. A workshop commissions a bell whose meaning becomes easier to recognize every time it is rung. Both makers are asked to improve their instruments. Their reports might record opposite changes in the time required to understand the bell.

This is not a distinction between boring engineering and interesting art. A musician can compose the gradual disappearance of a sound into habitual experience. An interface can productively unsettle a settled understanding of a system. Neither activity, however, is served by assuming that increased attention is an unconditional benefit.

Consider a machine with a thousand expressive variants of a routine statement. It may have learned an extensive vocabulary of surfaces while having only one thing to say. Another machine says two radically different things in almost indistinguishable voices. The first produces changes that may be meaningless to an operator; the second produces meanings that may escape notice. The designer's problem is not simply the amount of variety. It is the alignment between kinds of variety.

Shklovsky provides a particularly awkward interlocutor for a designer of explicit machine speech. If the purpose of an instruction is to communicate an unambiguous next action, prolonged perception can be a cost. If the purpose of a composition is to question what it means to have understood a sound, rapid recognition can be a cost. A synthesizer might deliberately move between these regimes, not as a crude switch between efficient and inefficient perception, but as a change in the purpose for which perceptual effort is invited.

### Source encounters (claims and access)

- Viktor Shklovsky, *Art, as Device*, translated and introduced by Alexandra Berlina, Poetics Today 36(3), 2015, DOI [10.1215/03335372-3160709](https://doi.org/10.1215/03335372-3160709). [Public text rendering](https://www.academia.edu/74019015/Art_as_Device), printed pp. 161–162 (habit and perceptual prolongation), 171–172 (poetic language and the reversal by which ordinary diction becomes unusual). Read those rendered passages and translator's introductory discussion of articles; publisher redirect inaccessible, no Russian original consulted. The reversal is crucial: once elaborate language becomes conventional, simplicity can estrange. Novelty is relational, not a property that can be measured by counting syllables. The latter sentence is our interpretation.
- Asiya Bulatova, *Estranging Objects and Complicating Form: Viktor Shklovsky and the Labour of Perception*, Transcultural Studies 13(2), 160–176, DOI [10.1163/23751606-01302004](https://doi.org/10.1163/23751606-01302004). [Author-uploaded rendering](https://www.researchgate.net/publication/322968211_Estranging_Objects_and_Complicating_Form_Viktor_Shklovsky_and_the_Labour_of_Perception), abstract, pp. 160–161; abstract read, not full article. Bulatova follows the historical development of estrangement toward practices of making objects and social formations, rather than treating it solely as a perceptual trick. This suggests a compositional intervention in the conditions of listening, not simply adding ornament.
- Mark Weiser and John Seely Brown, [*Designing Calm Technology*](https://calmtech.com/papers/designing-calm-technology), Xerox PARC, 21 December 1995, Introduction and The Periphery. Read these sections in the web transcription. Their account values movement between peripheral awareness and focal attention; they explicitly exempt some experiences such as games from the demand for calm. Natalie's Jeremijenko's Dangling String illustrates their argument through a material representation of network traffic (their description, not an independently inspected installation). Calmness is therefore not equivalent to either silence or lack of information.
- Rankin et al., *Habituation Revisited*, Neurobiology of Learning and Memory 92(2), 135–138 (2009), DOI [10.1016/j.nlm.2008.09.012](https://doi.org/10.1016/j.nlm.2008.09.012), [PMC author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC2754195/), characteristics 7–9. Read the selected passages, not all cited experiments. Stimulus specificity and recovery of response to the original stimulus are distinct; reduced effect of repeated dishabituating stimuli is also reported as a characteristic. Thus reaction to a new sound is not by itself evidence of dishabituation. These are behavioural research concepts, not synonyms for Shklovsky's literary account.
- Foley, Schlesinger and Schutz, *Improving detectability of auditory interfaces for medical alarms through temporal variation in amplitude envelope*, British Journal of Anaesthesia 130(3), 351–359 (2023), DOI [10.1016/j.bja.2022.10.045](https://doi.org/10.1016/j.bja.2022.10.045), [PubMed](https://pubmed.ncbi.nlm.nih.gov/36658020/). Publisher text surfaced in search; read abstract, Methods Experiment 1 Stimuli, Results and Discussion passages; direct publisher open failed, no independent reanalysis. Percussive tones were reported more detectable and less annoying than flat ones in the studied tasks; tones differed in duration and were RMS matched. This is within-token envelope design, NOT a finding that changing alarm vocabulary between successive presentations prevents habituation or that it improves action comprehension. It is a counterexample to an intuition that less annoying must mean less detectable.

All access/reading above on 2026-11-25 by the same AI agent. Neither independent replication nor formal Track E inclusion is implied. These accounts disagree in objectives and explanatory levels. The mathematical construction below is deliberately independent of them.

## Construction: a budget for changing things

Define n transitions between successive two-bit tokens (state, ornament). Start at (0,0). At each transition either bit can flip independently. Let S and O be the sets of state and ornament flips, with cardinalities s and k. This is an arbitrary symbolic instrument, not an auditory or neural model. A deliberately lossy observer detects only whether the token changed, yielding U = S union O. It neither decodes the state nor measures subjective novelty.

The observer raises a change flag on every element of U. With state changes as targets, there are s true flags, f = |O minus S| extra flags, and no missed target flags. No-change slots are negative. The flag is a bookkeeping convention, not a proposed warning policy.

For fixed n,s,k the exact feasible range is

    max(0,k-s) <= f <= min(k,n-s).

Proof: at most s of the k ornaments can coincide with state changes; at most n-s can occur elsewhere. Conversely for any integer f in the interval, choose f non-state transitions and k-f state transitions for ornament flips. Each mask defines a realizable binary path by cumulative XOR. The number of surface-change flags is h=s+f. If h>0 the precision of this deliberately lossy flag against the stipulated state-change target is s/h. If h=0, precision is undefined, not zero or one.

Example n=8, S={2,6}, k=4. Coincident schedule O={2,4,6,8} yields f=2 (best), disjoint O={1,3,5,7} gives f=4 (worst). Both retain the same two state changes and four ornament changes. The best count is not necessarily an optimal artistic choice: it privileges changes to state over independent ornamental evolution. This is the composer's decision in an artwork and requires a separate task analysis in an interface.

The result does not require an assumption about cognitive attention. It concerns a particular change-only projection.

### Second construction: identical surface-change trace

Now hold the whole observed mask U fixed, not merely its size. If h=|U|, a compatible schedule exists precisely when max(s,k)<=h<=min(n,s+k). For a feasible trace, choose s of its h positions to be S. The ornament must include all h-s remaining positions and choose s+k-h of the s state positions to overlap. Hence

    distinct state masks = binomial(h,s)
    distinct joint histories = binomial(h,s) * binomial(s,s+k-h).

For n=8, U={1,2,4,6,8}, s=2 and k=4, ten state masks and twenty joint histories remain. If the initial state is known, those ten state masks give ten distinct state trajectories. Knowing how many meaningful events and ornaments happened, and exactly when the surface changed, is insufficient to identify when the meaningful events happened.

This is not a result about a receiver that can decode the two-bit token. Such a receiver distinguishes both kinds of change immediately. The distinction between the full signal and a limited observer is the entire point.

### Executable check

Run `node oracle.cjs` from this directory. The same JS function was executed in an isolated JavaScript runtime before publication, then serialized as the source file; fetched source matched the authored bytes as text. It enumerated 87,381 pairs of binary transition masks over n=0..8, 6,912 nonempty trace/budget fibers, 285 budget configurations and passed 224,400 assertions. It tests exact accounting, every possible frontier value, both fiber counts and absent-trace feasibility. No statistical inference, perceptual data or full repository offline test is claimed. The finite check is a cross-check of the algebra, not its proof.

## Design hypothesis: the Estrangement Fader

A composition environment may expose a separate state lane, surface lane, and optional focal-attention score. A scope lock prevents ornamental changes from modifying the authored state. A scheduling control moves a fixed number of ornaments toward or away from state transitions. A monitoring view distinguishes state changes, ornament changes, overlap, and extra surface flags; it labels the last as a count in the model rather than a measure of distraction.

The unusual instrument here is one with an editable relationship between two musical grammars: what counts as a new gesture and what counts as a new message. An artist might keep a simple alternating state code while its realization evolves into a complex timbre cloud, or move all its ornaments onto the same boundaries to produce severe, monumental punctuation. A fourth mode could remove the state lane completely and compose nothing but changes without referents. That is a valid work, not a defective interface.

An alternative to automatic novelty generation is an explicit invitation to hear the ordinary sound differently: isolate its partials, expand its envelope, or reveal its synthesis graph on demand. The listener chooses when to foreground the object. Silence, familiarity and withdrawal are also artistically available. No attention telemetry, compelled engagement or fabricated listener-state estimate is needed.

For MHAC, the narrower question is whether learned invariant meanings survive variation in their acoustic realizations, and whether variation produces mistaken state transitions or distracts from a concurrent task. Compare stable tokens, state-aligned variants and independent variants; keep message sequence, number of presentations, overall variant counts and nominal levels controlled, counterbalance token mappings, order and acoustic rendering. Include separate outcomes for correct state/action decoding, transition false alarms and misses, response latency, concurrent task performance, annoyance, retention and voluntary preference. Separate first exposure from repeated training; test transfer to unheard variants. If investigating dishabituation, return to the original stimulus and measure response rather than substituting a response to novelty. No claims about operational safety from this model, no actual alarm substitution, no recruitment or experiment authorization.

A competing hypothesis is that familiar surface variation may eventually become a recognizable part of the code and produce no extra subjective flags. Another is that stable sounds become easier to recognize without becoming harder to detect; familiarity need not be fatigue. A further possibility is that aligned ornaments obscure precisely the transitions they were intended to emphasize. All would defeat a simple mapping from the toy frontier to human performance. Standard signal detection and task analysis may suffice; do not invoke cybersemiotics as a necessary explanation without a distinct testable contribution.

## Artistic consequence: the right not to be interesting

There is a political distinction between being allowed to ignore an object and being unable to ignore it. The maker of an instrument can ethically invite attention without being entitled to possess it. An artwork may demand intense voluntary attention; an always-present workplace tool does not thereby acquire a licence to be an artwork at the operator's expense. But designing for background use can also conceal inconvenient information and the labour that sustains a system. Peripherality is a relationship of access, not permission to hide state.

The proposed aesthetic is not an attention-maximizing engine. It is an instrument in which the negotiation of attention is itself composable, with a genuine off switch. In the concert hall, one might perform an hour-long arc from complex surfaces to a single repeated tone, then find the repeated tone strange precisely because it refuses to develop. In an interface, one might instead preserve a stable explicit meaning and offer inspection on request. These are different success criteria.

See [original score](SCORE.md) for a performable text work. The score is not an experiment and its artistic effect has not been tested.
