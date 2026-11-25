# The Metaphor That Becomes a Socket
*An expedition on catachresis, executable affordances and the right to specify what a metaphor does not carry.*

2026-11-25 · [Issue #422](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/422) · Exploratory AI-assisted humanities/art research, not Track E/G evidence, protocol amendment, or production implementation.

## 1. The wineless cup

A musician asks a programmer for a freeze control. The programmer makes the output remain at its current value while its generator continues to advance. Another programmer stops the generator's clock. A third preserves the currently loaded sequence while allowing the clock to advance through it. The three machines agree at the instant the button is pressed. They disagree about what can happen next.

The disagreement is not necessarily a failure of English. A transferred word has offered several useful directions for construction, and no specification has selected among them.

Aristotle's *Poetics*, chapter 21, offers two provocative possibilities: analogy may supply a name where a corresponding term is missing, and an alien name may be qualified by expressly denying one of its usual properties. The shield named as a cup without wine is the second kind. Quintilian, *Institutio Oratoria* VIII.6.34–36, draws a distinction between catachresis as use of a neighbouring term where a proper term is lacking and metaphor as transfer where another term already exists. His account also allows poetic departures from that distinction. These are not identical taxonomies.

**Interpretation:** the negative qualification is an unusually productive design operation. Instead of asking only which characteristics of a garden, river, loom, room or freezer to import into a digital instrument, ask which characteristics to expressly leave behind. A garden without compulsory growth, a door without enclosure, a freeze without stopping time. The latter is not just a picturesque name; it might be a specification for a particular output latch.

Calling modern synthesizer terminology catachresis is not a settled historical classification. The relevant technical vocabulary already exists. What is borrowed here is a method of making a missing distinction articulate, not a claim about the origin of the word freeze.

## 2. Source-located encounters and resistance

| Source and access | Source claim or argument | Expedition interpretation / limitation |
| --- | --- | --- |
| Aristotle, *Poetics* 21.11–14, Theodore Alois Buckley English translation, Perseus represented 1857 printing ([passage](https://beta.perseus.tufts.edu/urn:cts:greekLit:tlg0086.tlg034.buckley1850-eng1:21/)). Read relevant rendered English passage; edition marked provisional OCR; not Greek close reading. | Analogy may supply a missing name; one can import a name while denying a property. | Explicit exceptions can generate an interface affordance, rather than merely qualify an ornamental description. |
| Quintilian, *Institutio Oratoria* VIII.6.34–36 ([online English text](https://kairos.technorhetoric.net/stasis/2017/honeycutt/quintilian/8/chapter6.html)). Read numbered passage in English, not Latin. | Catachresis responds to a lexical lack, contrasted with metaphor where a term exists, with qualifications for poetic usage. | Borrowed technical language can make distinctions possible, but a poetic label alone does not implement them. |
| Stanford Encyclopedia of Philosophy, *Metaphor*, revision 12 August 2022, [§4.4](https://plato.stanford.edu/entries/metaphor/#BruForAcc). Read selected secondary exposition. Donald Davidson, *What Metaphors Mean* (1978), pp. 46–47 as cited therein; primary article not read. | Davidson's account, as expounded there, does not posit a determinate secondary message encoded in a metaphor; the framing it occasions can exceed paraphrase. | An executable contract cannot exhaust a metaphor. It selects an operational interpretation; artists need not surrender the remainder. |
| Alan F. Blackwell, *The Reification of Metaphor as a Design Tool*, ACM TOCHI 13(4), 490–530 (2006), [DOI](https://doi.org/10.1145/1188816.1188820), [HTML preview](https://paperity.org/p/376754876/the-reification-of-metaphor-as-a-design-tool). Read abstract and introduction pp. 490–491 only. | Blackwell distinguishes the concretization of a design idea as a general technique from its realization in a product; he notes criticism of overreliance on interface metaphor. | Prior art for the reification question. The present work narrows it to explicitly selectable consequences and exclusions at the level of a musical module. No claim that Blackwell endorses this construction. |
| Olivier Bau, Atau Tanaka, Wendy E. Mackay, *The A20: Musical Metaphors for Interface Design*, NIME 2008, 91–96, [proceedings abstract](https://nime.org/proc/nime2008_bau/index.html), [DOI](https://doi.org/10.5281/zenodo.1179489). Abstract only. | The authors describe a tangible multichannel audio probe using musical-instrument metaphors to generate interface-design ideas through participatory work. | Metaphor-driven instrument/interface design already exists. This is not a reproduction of their device or an appraisal of their empirical results. |

Accessed through web retrieval on 2026-11-25; no retained source files or source hashes; passages above were checked by the same AI assistant, not independently reviewed. No systematic search, empirical extraction, comprehensive theory reconstruction, or claim of novelty. The negative case was actively sought through searches for criticism of interface metaphor and Davidson's contrary approach.

There is a tension between making a metaphor operational and making it exhausted. If the metaphor is treated as a cryptic requirements document, the engineer becomes an examiner looking for the single correct translation. A musician might instead want to explore the surplus: the resemblance that does not fit, the image that prompts another gesture, the object that cannot be specified without ceasing to be interesting. A rule for a synthesizer can be precise while the reason for choosing it remains open.

A distinction worth retaining is between a metaphor used to describe an existing operation, a metaphor used to invent an operation, and a metaphor used to criticize a previously invented operation. They may all employ the same word. Only the middle case necessarily changes the instrument; only a concrete implementation warrants claims about its actual behavior.

## 3. A finite workshop: three freezes

**Synthetic construction.** Four pitch tokens 0–3 form a live four-slot bank, with transport initially at slot 0. HOLD is idempotent while held. TICK advances the transport by one modulo four unless transport is frozen. EDIT increments live bank slot 1 modulo four. RELEASE removes the hold without resetting the bank or phase. No clock exists between explicit events.

| Interpretation | While held | After release |
| --- | --- | --- |
| Output latch | Output repeats captured token; live bank and phase keep evolving | Current live bank at current phase |
| Transport pause | Phase stays fixed; bank remains editable | Phase resumes from where it stopped |
| Bank snapshot | Reads captured bank; phase advances; live bank remains editable | Current live bank at current phase |

All three labels may be rendered as FREEZE, but they implement distinct contracts. For bank [0,1,2,3], HOLD, TICK, RELEASE produces these traces (including the initial token):

| Mode | Initial | HOLD | TICK | RELEASE |
| --- | ---: | ---: | ---: | ---: |
| Output latch | 0 | 0 | 0 | 1 |
| Transport pause | 0 | 0 | 0 | 0 |
| Bank snapshot | 0 | 0 | 1 | 1 |

With HOLD, EDIT, TICK, RELEASE, output latch yields 0,0,0,0,2; transport pause 0,0,0,0,0; bank snapshot 0,0,0,1,2. The snapshot continues reading the old bank while edits accumulate in the live bank. Release reveals that work rather than rolling it back.

The model is deliberately not a waveform freeze, time-stretch algorithm, granular processor, spectral freeze or real DSP system. Tokens stand for an abstract control output. The three contracts do not exhaust possible implementations or predict the meaning a user assigns to the term.

### Executed finite census

Run the [dependency-free laboratory](laboratory.cjs) with Node: `node laboratory.cjs`.

The same function was executed in the JavaScript tool environment before serialization. The fetched repository file exactly matched that serialization. Across all 256 four-slot banks and 341 action sequences of length zero through four, all 87,296 bank/sequence cases were examined. Checks include 256 HOLD-only agreement cases, 30,976 cases without HOLD (all implementations agree), 256 adaptive discrimination cases, and shortest-horizon assertions for each bank. The principal and edit witnesses were checked against literal expected traces.

For 192 banks, a length-three sequence suffices to distinguish all three output histories; for the remaining 64, four events are necessary. The simple constructive test is HOLD, TICK, RELEASE when bank[0] differs from bank[1]; otherwise first EDIT slot 1 once, making the two tokens differ, and then run the same test.

Why three is the lower bound in the first case: a discriminating sequence needs HOLD and a TICK while held. These two actions cannot separate the latch and pause, which both remain on the original token in this model. RELEASE after the tick can separate them. For a three-action sequence to distinguish all modes, that arrangement is the only candidate: two held ticks cannot separate latch and pause; a single held edit cannot expose the edited slot (slot 1, not slot 0) without movement; and re-holding or releasing too early gives no divergent transport. When bank[0] equals bank[1], HOLD–TICK–RELEASE cannot separate any modes. The extra preparatory edit is sufficient. Exhaustive enumeration checks the argument across the defined finite family; there is no claim of a new general automata theorem.

**Counterexample:** the uniform bank [0,0,0,0] can conceal differences indefinitely if one only repeats HOLD, TICK and RELEASE. A conventional audition containing no changing data is therefore inadequate to qualify the freeze semantics. The adaptive test uses an authorized synthetic edit; it is not a recommendation to perturb a live system to test a label.

The relevant engineering analogy is to stateful API contracts and distinguishing sequences, not proof of a rhetorical or cognitive theory.

## 4. The instrument made from exceptions

**Design construction.** A metaphor module has a literary label, an explicit selection of state transitions, exclusions, a version and a literal explanation. The module does not compile arbitrary poetry into commands. A human author selects typed operations and can attach a poetic rationale.

The interesting performance parameter is which component the metaphor affects. Choose separately: transport, stored values, observation, edit admission, delay buffer, and downstream modulation. For each, choose continue, latch, pause or reject when appropriate to that component. Do not pretend every combination is coherent: incompatible choices must be rejected or resolved explicitly before execution. Exclusions should be executable checks when practical, not a decorative tooltip. The literal route remains accessible and the artistic label is not an authorization token.

Consider three hypothetical new sockets:

- **A mirror that does not follow:** snapshot a modulation value rather than binding to it continuously. The label is an invitation to investigate why a mirror would have memory.
- **A garden without inheritance:** local oscillator agents can proliferate but do not copy their parents' parameter values. This is one authored policy, not a law of botany or a claim of autonomous life.
- **A tide without return:** a periodic modulation bank passes its accumulated state forward instead of restoring it when the phase wraps. Specify bounds and explicit reset; the artist has borrowed periodic arrival while refusing periodic state recurrence.

There is a fourth possibility, deliberately contrary to the system: a poet writes a metaphor for which no executable socket should be manufactured. The instrument stores the text as a score instruction or annotation, not as an unimplemented control. This protects the imaginative act from being evaluated as an incomplete software ticket.

**Practical prototype:** connect a four-step modulation source to a second source through the three freeze modules. Route one to FM index, another to grain selection, another to filter cutoff. Let a single HOLD chord act on all three; let a second player perform clock and bank edits. Under RELEASE, three synchronized gestures unfold into different musical histories. Smooth actual signal transitions and bound gains; this proposal is not implementation.

**MHAC design hypothesis:** familiar transferred verbs such as freeze, clear, hold, dismiss or release may hide operational distinctions. In an entirely fictional task, compare an unqualified label, a literal scope statement, and a metaphor with a concise explicit exclusion. Randomize contract and prompt ordering; collect predictions of what continues during the hold and what state appears after release, then action errors and reading burden. Include users who find the metaphor unnecessary, and test unfamiliar contracts rather than only memorized labels. A result showing no incremental benefit from metaphor over literal scope would count against deploying it in an operational interface. Required warnings and actual device controls remain outside this experiment. No participants or outcome data exist.

## 5. The unbuilt fourth socket

*Original speculative fiction.*

The maker had three drawers of winter. In the first drawer a singer could sustain a vowel while her mouth wandered among other syllables. In the second the mouth could not move. In the third the words could not change, although she could continue to read them.

The maker called all three drawers FREEZE. She had bought the labels in bulk.

A poet came in and asked for a winter without cold. The maker began to calculate the required temperature. The poet took out a piece of paper and said she had already written it.

Years later the instrument's manual described exactly which parts of the mechanism would stop at the touch of a button. At the end was a fourth drawer which contained neither a circuit nor a switch.

It contained the paper. It was not a missing feature.

---

[Performance score](SCORE.md) · [Executable laboratory](laboratory.cjs)

**Checkpoint.** Reconciled live main at 495a98ca12bae467a507031f04931aa4254b1866; read AGENTS, RAG, programme, runbook, integrity, validation, README and research layout, target issue and empty comments. Inspected 100 recent PR titles, 70 open issue titles, main expedition directory and targeted metaphor/freeze searches. Adjacent issues [#326](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/326) (silent duration as control), [#262](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/262) (rule amendment) and [#334](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/334) (perceptual framing) were read at issue-description level and distinguished: here the object is selective transfer of metaphorical consequences into explicitly testable operation contracts. No attempt to establish global novelty from title searches. Canonical programme remains in progress; this owner-authorized parallel lane has no dependency on empirical corpus acceptance. AI author and single-agent software check, no human verification. No shared manifests or protocol edits. Full repository offline validation not performed in this environment; draft pending required exact-head repository checks and review.
