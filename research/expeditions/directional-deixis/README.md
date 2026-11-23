# MHAC-X002 — When "left" has no agreed origin

**Status (23 November 2026):** an original, source-bounded interdisciplinary expedition and **exhaustive fictional C4 coordinate-frame oracle**. This is neither an acoustic intelligibility experiment, a human-action safety finding, a completed R008 comparison, nor a new result in physics. Refs [issue #181](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/181).

## Contents

| Section | What it contributes |
| --- | --- |
| [1. A perfectly pronounced but ungrounded instruction](#1-a-perfectly-pronounced-but-ungrounded-instruction) | Distinguishes a semantic reference error from sound distortion |
| [2. Three different frame languages](#2-three-different-frame-languages) | Connects spatial deixis to typed robotics transforms |
| [3. The small impossibility theorem](#3-the-small-impossibility-theorem) | Gives a formal counterexample and exact boundary |
| [4. Gauge change: equivariance, not invariance](#4-gauge-change-equivariance-not-invariance) | Derives which rotations alter action |
| [5. The finite oracle and its uncomfortable negative controls](#5-the-finite-oracle-and-its-uncomfortable-negative-controls) | Enumerates action ambiguity, false certainty and abstention |
| [6. Repairs, costs and alternate explanations](#6-repairs-costs-and-alternate-explanations) | Contrasts explicit tagging, common conventions and absolute directions |
| [7. Source / rights / evidence ledger](#7-source--rights--evidence-ledger) | Exact consulted passage limits and source classes |
| [8. Non-duplication and conditional research transfer](#8-non-duplication-and-conditional-research-transfer) | Keeps the expedition outside canonical evidence gates |

## 1. A perfectly pronounced but ungrounded instruction

Imagine three physical orientations in a control room: the **recipient** faces north, the **machine emitter** faces east, and the **panel** faces south. A device says "turn left." The sound is distinct, the imperative is grammatical and the directions are all perfectly known. Yet its missing reference frame is consequential:

| Intended meaning of "left" | Required world action |
| --- | --- |
| Left of **recipient**'s facing direction (north) | West |
| Left of **machine**'s facing direction (east) | North |
| Left of **panel**'s facing direction (south) | East |

Those are different actions for *the same acoustic token in the same visible geometry*. The problem is not signal bandwidth, phoneme confusion, emotion or synonym choice. A referential index—*whose left?*—is absent.

This is an invented example, **not** a claim that English-speaking humans actually distribute these three readings equally, or that any machine should issue hazardous directional commands. Ordinary conversational convention often resolves such reference without overt tags. The point is to prove the conditional ambiguity and determine what would have to be observed or agreed for an action to be warranted.

This example also illustrates why *semantically ambiguous* is not synonymous with *action-ambiguous*. If all three objects face the same way, the referent is still unspecified, but all three interpretations demand the same movement. The action is invariant **in that scene** despite incomplete semantics.

## 2. Three different frame languages

Stephen C. Levinson's *Space in Language and Cognition* (Cambridge University Press, 2003) distinguishes spatial frame strategies and cautions against treating a familiar viewpoint convention as universal. The [publisher's preface summary, printed xvii–xx](https://www.cambridge.org/core/books/abs/space-in-language-and-cognition/preface/B19CACC31FE57EAABC96ABA4A11494BC) gives a simple double reading of "behind the truck": the truck's physical rear versus a location opposite the observer. The [publisher excerpt for chapter 2, printed pp. 24–61](https://www.cambridge.org/core/books/abs/space-in-language-and-cognition/frames-of-reference/41A4C90489EC9DA34C5D05974C437907) explicitly treats coordinate frames as a problem of spatial cognition. The [chapter 4 publisher extract, pp. 112–169](https://www.cambridge.org/core/books/abs/space-in-language-and-cognition/absolute-minds-glimpses-into-two-cultures/A9A39CEF4582A73B29156D09079852D9) discusses relative and absolute representations. **Access limitation:** these public extracts/summary, not the full book or a verified chapter close reading, informed this tangent; no cross-cultural effect size is asserted.

The engineering seam is less metaphorical. In [ROS REP 103, "Coordinate Frame Conventions" and "Axis Orientation"](https://reps.openrobotics.org/rep-0103/), Foote and Purvis prescribe typed conventions for bodies (x forward, y left, z up) and local geographic coordinates (east, north, up), plus an optical-frame convention that intentionally differs. Published October 7, 2010; the official page records an update on January 30, 2026. In [REP 105, "Specification / Coordinate Frames"](https://reps.openrobotics.org/rep-0105/), Meeussen defines frame names and semantics, distinguishing body-attached, drifting-continuous odometry and world-map coordinates that may jump with localisation updates (created October 27, 2010). These are **software engineering standards**, not communication psychology studies. They establish that a measurement or command without its reference frame can be materially underspecified *within certain formal systems*. They do not establish how people hear "left."

**Exaptation:** treat the frame of an audible action claim as a typed reference, much as robotics treats a pose. Unlike mere speaker/recipient addressing, "frame" refers to the coordinate system *used to compute the action*. One may know precisely who the listener is and still lack that coordinate system. Unlike a cue dictionary version, the token's lexical meaning can remain unchanged while its evaluated world direction shifts.

## 3. The small impossibility theorem

Let C4 = {0,1,2,3}, with 0=N, 1=E, 2=S, 3=W and addition mod 4 (clockwise quarter-turns). A complete toy scene is a triple of observed headings

    s = (h_recipient, h_emitter, h_panel) in C4^3.

Let F = {recipient, emitter, panel} be the possible **intended** frames. Our deliberately simple invented lexical rule is

    L(s,f) = h_f - 1 mod 4.

An observer receives the single word "left" and knows s but does not know f. Its possible-action set is

    A(s) = {L(s,f) : f in F}.

**Proposition (local decidability).** A deterministic direction-only decoder D(s,"left") is correct for *every admissible intended frame* in scene s if and only if A(s) contains one element.

*Proof.* If a decoder is correct for each f, it has to equal each L(s,f), so these are all equal. Conversely, if all outputs equal one a, define D(s,"left")=a, and it is correct for every f. QED.

**Counterexample to a globally correct untagged decoder:** set s=(0,1,2). Then A(s)={3,0,1}={W,N,E}. No single direction is correct under all three intended frames. Even if each orientation is observed exactly, missing *which frame was intended* prevents guaranteed action. This is a specialisation of the elementary observation-fibre result already explored in [X001's mathematical note](../observers-solecism/MATHEMATICS.md); it is **not a claim of a new general theorem**.

**Counterexample to "every untagged left is unsafe":** set s=(0,0,0). Then A(s)={W}. The unknown semantic anchor remains, yet the immediate world action agrees. Therefore insisting on a frame tag for *every* directional utterance is stronger than this toy mathematics demands.

**Counterexample to "a frame tag is sufficient":** let the frame be known as "recipient" but its heading be stale or unavailable. A bare tag does not repair the missing physical transform, nor does it confer authority, device condition or the right to perform an action. The oracle explicitly abstains when its trusted-transform flag is false, even in an aligned scene. This conservative rule is an authored policy, not a theorem of human safety.

A conditional lower bound follows: if a sender knows which of m distinct candidate world actions is intended and the receiver is otherwise uncertain, an error-free fixed-length binary disambiguator requires at least ceil(log2 m) bits *in this artificial coding model*, assuming a shared codebook. Here m can be 1, 2 or 3; the corresponding bound is 0, 1 or 2 bits. This is **not** a measurement of speech duration, human cognition or acoustic channel capacity.

## 4. Gauge change: equivariance, not invariance

Rotate *all* orientations in s by k quarter-turns:

    T_k(s) = (h_recipient+k, h_emitter+k, h_panel+k) mod 4.

Then

    L(T_k(s),f) = L(s,f) + k mod 4,
    A(T_k(s)) = {a+k mod 4 : a in A(s)}.

This **equivariance** states that an action expressed in world bearings rotates when the whole scene rotates. It is **not** invariance: a recipient's world action cannot generally remain north when they turn east. By contrast, changing only recipient heading leaves *emitter-relative* and *panel-relative* actions unchanged. These identities are exhaustively tested for all 64 scenes and 4 rotations by [test_frame_oracle.py](test_frame_oracle.py).

Calling this a "gauge" analogy is *deliberately qualified*: in mathematical physics, a gauge transformation has formal structures and consequences absent from our tiny C4 reference-coordinate choice. The present derivation is group-action arithmetic; it makes **no physical gauge symmetry claim** about language, cognition or sound.

A potentially useful distinction falls out. A **relative instruction** can be equivariant under change of observer orientation, whereas an **absolute instruction** such as "go west" has a world-bearing action unchanged by rotating recipient, panel or emitter (assuming a genuinely shared north convention). Neither is universally safer: absolute directions require orientation knowledge and may impose extra cognitive burden.

## 5. The finite oracle and its uncomfortable negative controls

The implementation [frame_oracle.py](frame_oracle.py) is standard-library Python and declares **every scene fictional**. It enumerates 4^3 = 64 heading triples and evaluates three possible true frames per scene: 192 scene-frame cases. All headings are known exactly *within this synthetic model*. The following are **combinatorial identities for the chosen exhaustive grid, not performance rates**:

| Fictional comparator | Mechanically determined count |
| --- | ---: |
| Untagged action set contains a single world direction | 4 of 64 scenes |
| Untagged action set contains more than one direction | 60 of 64 scenes |
| Blind "recipient-left" default matches all three truth-labeled frame cases | 96 of 192 case pairs |
| Blind recipient default conflicts with labeled true action | 96 of 192 case pairs |
| Conservative untagged policy commits correctly | 12 of 192 case pairs |
| Conservative untagged policy abstains | 180 of 192 case pairs |
| Explicit, correct frame and current trusted heading | 192 of 192 case pairs |

The artificial distribution samples **three frames equally**, an assumption with no evidence for real communicative priors. The conservative oracle appears accurate because it declines nearly everything. This is **not a demonstrated optimal or desirable human interface**. It may refuse many perfectly actionable situations where a conversational convention already supplies the intended reference. A different, simpler shared rule ("directions always refer to the recipient's current orientation") eliminates this uncertainty **if faithfully implemented and understood**.

The syntactic tests cover a scene with three different outcomes; aligned-frame negative controls; invalid/out-of-range headings; unknown frame names; all rotations; changing one irrelevant frame; stale-transform rejection; and deterministic canonical JSON identity. They do not synthesise audio, estimate acoustic confusability, test accessibility, collect user traces, measure failure consequences or validate a real transform service.

### Reproduction

From repository root, using Python 3.11+ with only the standard library:

    python -m unittest discover -s research/expeditions/directional-deixis -p 'test_*.py' -v
    python research/expeditions/directional-deixis/frame_oracle.py --check
    python research/expeditions/directional-deixis/frame_oracle.py --out build/mhac-x002

The optional generated census/receipt under build/ is **disposable** and not a canonical record. Normal full-repository tests and validation are separate.

## 6. Repairs, costs and alternate explanations

| Strategy | What it can solve in the toy model | What it cannot establish |
| --- | --- | --- |
| **Explicit referent**: "left relative to the panel" | Identifies the transformation anchor | That the listener can compute/see the panel pose, or can act |
| **Shared convention**: all "left" means recipient-relative | Eliminates frame selection when all parties know/observe the rule | That a convention is known, retained, usable under noise or shared across populations |
| **Absolute utterance**: "west" | Eliminates the three-object frame choice | That listener knows north, that world/map orientation is current |
| **Conditional commitment**: act only if all plausible frames imply same action | Avoids a wrong direction in this fully enumerated, perfectly specified state set | Timely action; why frames were plausible; unknown unknowns |
| **Clarification / alternate channel** | Can theoretically reveal missing index or transform | That a response will arrive, be understood, or beat a deadline |

A strong counter-position is simply that an interface with one established direction convention needs no per-command frame metadata. That explanation is often cheaper than a new semiotic theory. Our toy does not refute it. Conversely, speaker-only or device-only directions can be actively deceptive in a multi-device environment if the recipient assumes a different convention. Which model better predicts real comprehension remains an open empirical question.

A further complication is **time of reference**. REP 105 distinguishes a continuous local odometry frame from a map frame where jumps may occur; a frame label without a timestamp / transform history is insufficient for some actions. We deliberately **do not** solve deadline scheduling, instruction retraction or multi-agent authorization here. Those are separate issues, though an eventual design might require their conjunction.

## 7. Source / rights / evidence ledger

All retrieval below was performed on **23 November 2026**. Citations link to the exact publicly visible publisher or official material. No restricted works were copied into this public repository.

| Source | Actually inspected | Supported use and limit |
| --- | --- | --- |
| Levinson, *Space in Language and Cognition* (2003), [publisher preface](https://www.cambridge.org/core/books/abs/space-in-language-and-cognition/preface/B19CACC31FE57EAABC96ABA4A11494BC), printed xvii–xx | Public publisher preface summary / excerpt | The example of spatial descriptions admitting alternate referent perspectives; **not** full text / chapter-level validation |
| Levinson, [chapter 2 publisher extract](https://www.cambridge.org/core/books/abs/space-in-language-and-cognition/frames-of-reference/41A4C90489EC9DA34C5D05974C437907), printed 24–61; [chapter 4 extract](https://www.cambridge.org/core/books/abs/space-in-language-and-cognition/absolute-minds-glimpses-into-two-cultures/A9A39CEF4582A73B29156D09079852D9), 112–169 | Public preview and visible summaries only | Identifying the spatial frame and relative/absolute distinction; not quoting unread research outcomes |
| Foote & Purvis, [REP 103](https://reps.openrobotics.org/rep-0103/), "Coordinate Frame Conventions", "Axis Orientation", "Suffix Frames" | Entire publicly accessible official HTML specification sections | Concrete body/ENU/optical axis conventions, not a human-audio experimental result |
| Meeussen, [REP 105](https://reps.openrobotics.org/rep-0105/), "Specification / Coordinate Frames": base_link / odom / map | Public official specification sections | Engineering distinction between body-relative, locally continuous, and map-fixed frames |
| Clark & Wilkes-Gibbs (1986), [*Referring as a collaborative process*](https://web.stanford.edu/~clark/1980s/Clark.Wilkes-Gibbs.86.pdf), *Cognition* 22, 1–39 | Bibliographic record and publicly exposed **abstract only**, no full-article extraction | Background lead that linguistic reference can be collaboratively repaired; **no** claim about alarm decoding or timing |

**Authorship/verification:** one GPT-6 assistant assembled the reasoning, original oracle and tests using public web and GitHub tooling. The code calculations, when run, provide synthetic machine checks. Source interpretations and tests are AI self-review, not independent scholarly critique. There were no participants, reviewers, engineering users, audio recordings, speech recognition tests, or physically controlled trials.

## 8. Non-duplication and conditional research transfer

- [X001 #178](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/178) formalised **projection/observational fibres and circle-harmonic aliasing**. This expedition does not repeat its alias theorem or compact-dimension metaphor: it studies **action equivariance under competing referential anchors**, and cites X001's general theorem as existing work.
- [T008 #43](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/43) governs **who is addressed and authorised**. A perfectly authorised addressee may still interpret a direction in the wrong reference frame.
- [T011 #49](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/49) governs **mode-dependent action validity**. This model holds mode/action permission constant and varies coordinate frame.
- [T012 #51](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/51) governs **versioned learned cue dictionaries**. The lexical token is not recoded.
- [T013 #54](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/54) studies **false historical presupposition**. This is a current referential anchor problem, not a claim about what happened previously.
- [R008 #8](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/8) may later compare this **hypothesis**, but corpus selection and actual close-reading gates remain unsatisfied; this document is not a scientific synthesis.

**Conditional transfer:** A future (separately authorised) experiment could cross frame-clarity (explicit/implicit) with orientation alignment (aligned/divergent), lexical framing (recipient / emitter / map), and verification freshness, while measuring correct action, dangerous confusions, delays, repetitions and subjective workload. Negative controls would include purely conventional single-frame tasks. Any real test must follow R014/R020 readiness and consent safeguards, match acoustic and instruction-length confounds, and admit that straightforward wording may outperform novel coding schemes.

**Decision:** Keep the reference-frame contract as useful interdisciplinary sediment and a falsifier of overly confident directional speech. Do **not** automatically add frame tags to every audio message, claim universal human error, or promote a mathematical toy to accepted empirical evidence.