# The Chiastic Trap
## Audible symmetry, non-invertible action and the seduction of formal closure

**MHAC-X006 · 23 November 2026 · independent humanities/technical-aesthetic expedition · Refs #188**

**Status:** original conceptual argument plus a deterministic finite-state counterexample and original PCM generator. Not a canonical Track E/G synthesis, a validated auditory design rule, a listening study or a reconstruction of Brier.

> A sentence can turn round without retracting itself. A tune can return to its first motif without returning the machine to its first state.

## Contents

1. **The tempting error** — separate audible return from operational restitution.
2. **A small history of crossings** — situate chiasmus and antimetabole without anachronism.
3. **The mathematical trap** — finite-state counterexamples and qualifiers.
4. **Four different mirrors** — clarify language, token sound, music and state.
5. **The instrument** — reproduce twin soundtracks and compare hidden histories.
6. **Pragmatics and dramaturgy** — use form as a question, not an all-clear certificate.
7. **Adversarial cases** — negative controls and attempted falsification.
8. **Transfer and further tests** — what might be done next without inventing results.

### 1. The tempting error

A four-event phrase **A B B A** has a visible axis of symmetry. If A and B are distinct, the sequence is identical to its reversal at the **token** level. The last occurrence of A can feel like a return because an earlier sign has reappeared at the outer boundary. The two B tokens are folded together at the centre. A designer may be tempted to use the form as an audible confirmation that a system has recovered, undone an intervention or closed the loop.

That temptation crosses several unlicensed inferential steps:

- The event-symbol sequence is palindromic.
- The rendered audio presents a perceptually legible symmetry.
- The events have meanings that retain identity across their occurrences.
- The operations denoted by those events are reversible.
- Their successive execution restores the relevant world state.
- Restoration, if true, is authorised and informative enough to announce to a human at the relevant time.

These propositions are not interchangeable. Only the first is a property of the bare token list. The second would require listening evidence. The third requires a typed interpretation contract. The fourth and fifth need a state-transition model and, in practice, trustworthy observation of its execution. The sixth adds recipient, timing and authority.

This report studies the narrow gap between **surface mirror** and **operational return**. It neither assumes that all chiastic expressions imply restitution nor attributes such a belief to all listeners. The *chiastic trap* names a design and interpretive hazard: a seductive form can make an unsupported inference seem settled.

### 2. A small history of crossings

**Terminological constraint.** Gideon O. Burton's *Silva Rhetoricae* chiasmus entry distinguishes reversal of ideas or grammatical arrangement from the more restrictive antimetabole, in which the same lexical material reverses order. Burton's antimetabole entry names *commutatio* and relates it to counterchange. These are pedagogical, modern taxonomic statements, not a guarantee that all eras used the terms identically [S1–S2].

The online *Rhetorica ad Herennium* Book IV **outline** locates *commutatio* as the 29th listed figure of diction [S3]. This establishes only a location in a modern outline. The original Latin text at IV.28.39 was **not** read or translated for this expedition. The text's position in the list cannot establish how an ancient rhetor would evaluate machine-generated ABBA sound.

Harris and Di Marco's 2017 editorial on rhetorical figures and computational argumentation [S4] distinguishes a formal figure's occurrence from its rhetorical functioning. The presence of crossed constituents is not all that makes an utterance do persuasive, deliberative or aesthetic work. Their glossary and footnote 4 acknowledge that different research programmes use *chiasmus* with different breadth. X006 does not settle that taxonomy: it preserves the distinction before importing formal rhetoric into machine sound.

A sharper empirical warning comes from Dubremetz and Nivre's 2018 **original computational study** [S5]. In Table 1 and §§2.4, 3.1, a shallow extraction of crossed lemma patterns from a parliamentary corpus generated **2,097,583 candidates**. In a **random sample of 100 candidates, zero were annotated as true chiasmi**. This is emphatically **not** a finding that the corpus had no true chiasmi; the article proceeds with annotated positives and trained classifiers. It shows why a permissive formal detector may be overwhelmed by accidental repetition, not why rhetoric cannot be computationally studied.

For X006 the further, distinct warning is that even an **intentional** chiasmus does not prove the events represented by it are reciprocal or reversible. A rhetor crosses clauses to emphasise contrast; a composer retrogrades a musical line for formal interest; a machine emits an ABBA motif because the designer programmed one. Their purposes do not become identical through shared geometry.

The ancient index, modern taxonomy and computational study offer a methodological caution, not a new empirical effect: **figure recognition, interpretation and state claims require different evidence**.

### 3. The mathematical trap

The model is small and exhaustively enumerable. Let the state space be S = {0,1,2}. Each token A and B names an **explicit permutation** of these states. With events executed left to right, the total transformation of the sequence A B B A is:

\[
F_{ABBA}=A\circ B\circ B\circ A.
\]

Function composition is conventionally read right to left. Here the event list happens to be symmetric, so this notational choice does not obscure an event-order reversal.

**Case 1: return despite noncommutation.** Let A exchange 0 and 1, and B exchange 1 and 2. Both are **involutions**, meaning A² = B² = I. They do **not** commute: AB and BA have different effects on a state. Nonetheless ABBA = A(B²)A = A² = I. This holds for **every** state. The palindrome corresponds to restitution because both the inner operation and the outer operation cancel themselves. Commutativity is not required.

**Case 2: departure under exactly the same sound.** Keep B as the swap of 1 and 2, but let A be the three-cycle 0→1→2→0. Now B² = I but A² ≠ I. Consequently ABBA = A² ≠ I. For starting state 0, the final state is 2, not 0. Exhaustively, the effects on starting states 0,1,2 are (2,0,1); Case 1 gives (0,1,2).

**Logical qualifications.**

- Both A and B being involutive is **sufficient**, not **necessary**, for this ABBA cancellation. For example, two inverse three-cycles can also give an identity composite.
- A palindrome is **not necessary** for state return: A A B B returns every state when both operations are involutions, though its token order is not a palindrome.
- A palindrome is **not sufficient**: the three-cycle case refutes the implication.
- A B A B need not return even when its two component actions are involutions. In the two-swap case they are noncommuting, so changing sequence order changes the effect.
- Operational invertibility is not identical to **repeating the same token**. In a real instruction language a separate inverse command could be needed. Inverse transformation, event replay, compensation and physical reversal are different.

These results concern precisely specified **finite-state mathematics**, not human semantic processing, real industrial safety or the ontology of time.

### 4. Four different mirrors

**Graphic/linguistic order.** ABBA is a palindrome in a two-symbol alphabet. A human sentence may be an antimetabole if lexical constituents recur in reverse and serve an expressive purpose, but this toy has no grammar or addressee. A structural property does not fully determine a rhetorical act.

**Event-level sound.** The synthesizer assigns two newly computed frequency pairs to A and B. The rendered four-motif sequence has symmetric **motif identities**. This does not mean its PCM samples are invariant under literal time reversal: oscillator phase, fades and gap boundaries defeat such a simple assertion. The instrument checks *same bytes across interpretations*, not sample-level reversal symmetry.

**Musical retrograde.** Compositional retrograde means arranging a line in reverse order; a **crab canon** brings original and reversed voices together, creating further contrapuntal conditions. X006 does not claim to implement a historical crab canon or score-reversed version of a copyrighted work. The comparison is to arrangement, not a demonstrated listener's experience.

**Causal/operational restitution.** Returning to a previous state depends on functions represented by signs, their execution and the completeness of the state description. Even identity on the toy three-element set does not include elapsed time, audit logs, wear, delayed commands, human action or side effects. A formal mirror is not a reversed physical process.

This is the central asymmetry: the artwork may be formally self-returning while the world to which it refers is not. Conversely, a nonpalindromic score can faithfully narrate restoration.

### 5. The instrument

The original [chiastic_lab.py](chiastic_lab.py) is deliberately austere: 16 kHz, 16-bit, stereo WAV; four 200-ms pitched segments and 50-ms gaps; two distinct frequency pairs for A and B; linear fade envelopes; Python 3.11+ standard library. No voice samples or borrowed melody are used. **Audio depends only on token labels**, not on the hidden permutations they denote.

Reproduce from the repo root:

    python3 research/expeditions/chiastic-trap/chiastic_lab.py --out build/mhac-x006
    python3 -m unittest discover -s tests -p 'test_x006_chiastic_trap.py' -v

| File in build/mhac-x006/ | Type | Meaning |
| --- | --- | --- |
| closed_involutions.wav | original PCM | A B B A motifs, reversible-state interpretation |
| open_rotation.wav | original PCM | **byte-identical** A B B A motifs, nonreturning interpretation |
| closed_involutions.json | machine-readable | permutations, state path, SHA-256 |
| open_rotation.json | machine-readable | different effects, identical WAV digest |
| comparative-report.json | comparison | invariants, countercontrols, precise nonclaims |

Byte identity is a **constructed result** of the renderer's deliberate independence from semantic actions. It is verifiable by hashing or binary comparison. The toy does not discover unknown auditory behaviour; it exposes how an unannounced mapping difference can alter an event phrase's semantics without affecting its sound.

The instrument is **anti-certification**. It stages a formal duet between a finished story and an unfinished one. A listener may enjoy the chiasmus, but an audit cannot infer restoration from that beauty.

### 6. Pragmatics, authority and dramaturgy

A machine designer might choose a mirrored sonic phrase to organize expectation, mark a boundary, signal hierarchy or create rhythmic closure. Those remain **design possibilities**. The broader rhetorical literature treats form as capable of communicative function [S4], but this expedition has **not shown** that four synthetic tones achieve any particular perceptual effect.

A careful designer would separate three propositions:

1. **Form:** the event motif returns to its first token.
2. **Model:** named transition rules formally restore an explicitly chosen state.
3. **World:** independent evidence confirms that the consequential system is back in an authorised, acceptable condition.

A system can assert the first, prove the second in a restricted model, and lack grounds for the third. Another system can complete a real rollback without a chiastic motif. Letting the sound's formal structure stand in for the world claim would be an **aesthetic substitution**—shape replacing evidence.

This matters to MHAC even if machine speech is deliberately non-human in timbre. Avoiding impersonated human emotion does not forbid rhetoric, punctuation, play, repetition or meaningful prosody. The problem is not rhetoric but an **unmarked jump** from an artful structure to operational authority.

A strong opposing interpretation is that nobody would treat these four beeps as any claim at all. That may be correct; no hearing experiment here establishes an error's prevalence. The model proves a narrower result: **token symmetry alone cannot certify state restoration**.

### 7. Adversarial cases

**Sufficiency fails:** ABBA with a three-cycle A moves every state. Formal palindrome is not enough.

**Necessity fails:** AABB, with A and B involutive, restores every state despite not being a token palindrome.

**Order matters:** ABAB and ABBA have the same multiset of tokens. Under two noncommuting swaps only the latter is identity. Histogram equality is not sequence equivalence.

**Non-involutive success:** make A and B inverse three-cycles. ABBA can return all states even though neither token is itself a self-inverse operation. The sufficient condition in Case 1 is not a universal characterisation.

**Rhetorical overrecognition:** a raw ABBA detector can return chance repetitions, analogous to the overwhelming negative candidate sample reported in [S5, Table 1/§3.1]. The lab's ABBA is *designed*, but that does not independently establish its aesthetic force.

**Closure is not safety:** a tiny state tuple omits side effects. The model cannot replace MHAC's separate instructions, mode, timeliness, authority, field-binding or retraction questions.

**Detectability is open:** no masks, device transfer functions, listening outcomes or population data are involved. It is quite possible that the mirror is aurally weak. CI cannot determine otherwise.

### 8. Transfer and further tests

**The Palindromic Liar (art proposal).** A deliberately playful synthesizer assigns a symmetrical motif to two hidden machine histories. Only after playback does its interface disclose the state paths. The user has encountered the same auditory phrase yet two different endings. *Liar* is a dramaturgical metaphor; the four beeps assert nothing in natural language.

**Non-Closure Inspector (developer toy).** Let a user enter event permutations and token strings, and see the actual state transition function alongside a generated motif. The lab supplies an initial noninteractive API for such a tool.

**Symmetry-as-Assertion Lint (research suggestion).** A design reviewer might flag a UI that labels its return motif *all clear* without an evidence path. This is a critique of a possible rationale, not a validated automated rule.

**Possible participant experiment (not conducted).** Teach listeners two semantic maps for the same audible token system, then test recognition of order, inference about state, mapping memory, and confidence separately. Control for hearing conditions, presentation semantics, timing and task stakes. Human recruitment, ethics and authorization are absent and would be required.

**Critical humanities question.** When does a balanced phrase make an argument feel inevitable without adding a premise? Study actual text corpora and rival readings before asserting that chiasmus intrinsically persuades anyone.

No transfer has been accepted as a production requirement. This is a research seed, a finite formal counterexample and an artistic score, not a premature final synthesis.

---

## Claim register

| ID | Class | Claim | Basis | Revision test |
| --- | --- | --- | --- | --- |
| C1 | source-description | Burton distinguishes chiasmus and antimetabole | [S1–S2] | historically situated contrary taxonomy |
| C2 | source-description | an online outline places commutatio in Book IV | [S3], item 29 | full primary reading required for ancient-theory claim |
| C3 | source-description | sampled unfiltered chiasmus candidates had 0/100 true | [S5], Table 1 §3.1 | actual paper correction or changed retrieval |
| C4 | finite theorem | noncommuting involutions can make ABBA identity | explicit algebra, exhaustive 3-state enumeration | contradictory state in declared permutation |
| C5 | finite counterexample | ABBA is not always identity | three-cycle witness | contradictory state in declared permutation |
| C6 | synthetic witness | distinct event semantics can have identical WAV bytes | source and generated SHA-256 comparisons | unequal output bytes |
| C7 | interpretation | symmetric closure may suggest false operational closure | argument, with explicit opposition | contrary conceptual critique or human evidence |
| C8 | design hypothesis | closure inspector may aid review | proposal only | independent implementation and evaluation |

## Sources, precise access and reading scope

[S1] Gideon O. Burton, [Silva Rhetoricae: chiasmus](https://rhetoric.byu.edu/Figures/C/chiasmus.htm), visible complete online definition and examples, accessed 2026-11-23. Modern secondary scholarly reference.

[S2] Burton, [Silva Rhetoricae: antimetabole](https://rhetoric.byu.edu/Figures/A/antimetabole.htm), visible complete definition and examples, accessed 2026-11-23. Modern secondary reference.

[S3] Burton's [Rhetorica ad Herennium Book IV outline](https://rhetoric.byu.edu/Primary%20Texts/Ad%20Herennium-Book4.htm), figures of diction item 29, accessed 2026-11-23. **Outline only**, not Latin/translation close reading.

[S4] Randy Allen Harris and Chrysanne Di Marco, [Rhetorical figures, arguments, computation](https://journals.sagepub.com/doi/full/10.3233/AAC-170030), *Argument & Computation* 8(3), 2017, §3, §4, glossary and footnote 4. DOI 10.3233/AAC-170030. Open-access HTML sections inspected; not independently empirical verification of their broader claims.

[S5] Marie Dubremetz and Joakim Nivre, [Rhetorical Figure Detection: Chiasmus, Epanaphora, Epiphora](https://www.frontiersin.org/journals/digital-humanities/articles/10.3389/fdigh.2018.00010/full), *Frontiers in Digital Humanities* 5:10, 17 May 2018, DOI 10.3389/fdigh.2018.00010. HTML abstract, §§2.4, 3.1–3.3, Table 1 checked. **Primary research on figure detection**, not auditory perception.

[S6] Paul Fry, [Yale ENGL 300, Lecture 9 transcript](https://openmedia.yale.edu/projects/iphone/departments/engl/engl300/transcript09.html), discussion of Roman Jakobson's equivalence principle, accessed 2026-11-23. **Secondary teaching source**, not original Jakobson 1960. It is a contextual lead only; no principal finding here rests on the lecture.

**Provenance:** ChatGPT GPT-6 assisted research and source reading, 2026-11-23. No human peer review or empirical participants. Original code and original formula-based audio only. Actual CI status and final commit evidence must be recorded separately once observed. Source rights are not transferred to MHAC; third-party article text is paraphrased, not republished.

**Anti-conclusion:** The most useful result may be not a new acoustic code but a precisely testable refusal to mistake elegance for explanation.
