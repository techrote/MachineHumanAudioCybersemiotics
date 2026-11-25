# The Note That Amends Its Own Score
*Metalepsis, constitutional music and the distinction between a performance and its laws.*

Exploratory humanities/art research, 2026-11-25; issue #594. Synthetic formal apparatus, not Track E/G evidence, an operational authorization system or a finding about listeners.

## A theatre with two clocks

A conductor raises a baton. A note sounds. According to the score, that note appoints a different conductor. The new conductor declares that the note which appointed her was forbidden. Has a forbidden note occurred, or has a lawful note produced a different law?

The question is not whether a sound can be undone. It is whether the *description* of its status can be changed without confusing the time of an event with the time of a judgment. A musical work could cultivate precisely this disturbance, in much the way a fictional character might step out of a book and address its author. But an interface that presents an actual machine action must not silently revise the authority under which it was performed.

Consider three clocks: the sound clock (what happened), the constitutional clock (which rule was in force), and the editorial clock (when a subsequent interpretation was written). A recording freezes only the first of these, and only the acoustic aspects of it. A later edition can annotate the event, disagree with it or replay it; it cannot turn that edition into the original performance.

## Source encounters and dissent

All passages below were checked by one ChatGPT agent on 2026-11-25 through publicly readable web text. These are passage-level reading notes, not a systematic search, complete book readings, human review or a claim of intellectual priority. No source text or third-party recordings are redistributed.

- John Pier, “Metalepsis,” *the living handbook of narratology*, revision 1 July 2013, [Definition, first three paragraphs](https://www-archiv.fdm.uni-hamburg.de/lhn/node/51/revisions/51/view.html). Pier describes Genette's crossing of narrative levels, distinguishing syntactic embedding and referential disturbance, and reports the connection to strange loops. Genette's primary books were not consulted. Interpretation: the score/performance boundary can become a theatrical threshold. A real program dispatching events is not thereby an ontological paradox; it is the artist's staging of levels that supplies the analogy.
- Peter Suber, “Nomic: A Game of Self-Amendment,” appendix 3 to *The Paradox of Self-Amendment*, [Introduction and Initial Set, rules 103, 107–110, 111, 115–116](https://constitution.org/2-LawRev/psuber/nomic.htm). In this playable proposal, amendment is itself a rule-governed move. Rule 107 forbids retroactive effect; rule 115 expressly permits self-referential amendments. These provisions can coexist. The introduction distinguishes logical priority from amendment difficulty. Interpretation: a score can admit self-modification while preserving a temporal boundary for authority. This is a reading of a game, not a claim about current law or legal legitimacy. The rest of the book was not read.
- TOPLAP, [ManifestoDraft, original music-performance manifesto and Kate Sicchio's Hacking Choreography draft](https://toplap.org/wiki/ManifestoDraft.html). The first asks that algorithms be visible alongside outcomes and allows programs to change themselves. The second explicitly gives the dancer latitude to alter or disregard a program. These are practitioners' aspirations, not findings about audiences. Interpretation: an editing interface can itself be part of a performance, but compulsory visibility or a supposedly emancipatory rule system may become a spectacle of control.
- New Music New College, [Cornelius Cardew's The Great Learning, Paragraph 7, and Stephen Miles's accompanying notes](https://www.newmusicnewcollege.org/cardew). The performance account describes singers moving, listening and choosing a new pitch already being sung. This is a precedent for output feeding later musical choice while the higher-level instruction remains stable. The original score image was not inspected; rely on the ensemble's textual account, not an independent score analysis. Counterpoint: such feedback does not require constitutional amendment at all. Our instrument must not confuse altering a parameter with changing the interpreter.
- ISSUE Project Room, [Alvin Lucier: I am sitting in a room, event description, paragraph on the work](https://issueprojectroom.org/video/alvin-lucier-i-am-sitting-room). The account explains repeated playback and rerecording through a room, with resonances becoming prominent. This is a different feedback mechanism: an acoustic transformation acts on the material rather than a symbolic permission rule. No recording analysis performed. The physical room is not a legislature.

The contradiction worth keeping: Nomic offers a temporal rule to protect the intelligibility of amendments, while metaleptic fiction gains artistic force from unsettling such boundaries. The musical score may deliberately invite impossible self-certification. Its host must still have an unambiguous way to stop and report the result. None of the above authors is being credited with this specific construction.

## A finite constitutional score (stipulation and derivation)

Let the finite vocabulary Q have n distinguishable notes, each paired with a local score state. In state p the only prescribed note is p. The immutable meta-score is a complete deterministic table f: Q -> Q, interpreted as the amendment proposed by hearing note x. This is a change of the active prescription, not arbitrary code self-modification.

Prospective execution: emit x=p, record the rule/state p, then install f(x) for the next event. Every initial state has a unique infinite symbolic performance. For finite n it eventually repeats. There is no requirement that a note authorize itself under its successor prescription.

Retrospective audition: independently ask which hypothetical note x would be prescribed by the state it installs at the *same event*: x=f(x). This is a deliberately different constraint, not an alternate implementation of the prospective transition and not a history-rewriting algorithm. Its solution set may be empty, singular or plural. The retrospective mode ignores the original state; intersecting with an original prescription p instead yields either {p} or the empty set. Do not conflate these questions.

Example f=(1,2,3,0): prospective performance from 0 is 0,1,2,3,0,...; no note can satisfy the retrospective constraint. There is no contradiction in the prospective performance. Example identity f=(0,1,2,3): all four notes qualify for retrospective audition, while prospective execution remains on the chosen initial note. A solver that silently picks one answer introduces an extra artistic decision.

Exact census: for k fixed points among n states, select the k fixed states and assign each other state any of n-1 different destinations. Thus N(n,k)=choose(n,k)*(n-1)^(n-k). At n=4 the census for k=0..4 is 81,108,54,12,1, summing to 256. A uniformly sampled table has expected fixed-point count 1 (each state fixes with probability 1/n), but that does not establish existence in any particular table, nor a meaningful distribution over music. These are elementary finite functions, not a new fixed-point theorem.

## The second rabbit hole: an unperformed constitution

Suppose an observer knows the exact symbolic performance from one starting state up to and including its first repeated state. Let k be the number of distinct departing states observed. Those k table entries are fixed; each remaining entry may be any of n destinations. The number of compatible tables is n^(n-k). No further repetition along that orbit can reduce this count.

A stronger conditional census: let u=n-k, and let b be one if the repeated cycle has period one, zero otherwise. There are choose(u,j)*(n-1)^(u-j) compatible tables with exactly b+j fixed points, for 0<=j<=u. The known departures have exactly b fixed points, since no self-loop can be left once entered. This assumes exact labelled states and deterministic stationary tables, and does not imply a real listener could recover even those departures.

Example f_A=(1,0,2,3), f_B=(1,0,3,2): from 0 both play 0,1,0,1,... forever. The first admits two retrospective audition notes; the second admits none. Identical rendered waveforms follow if the renderer is a deterministic pure function of the same note slots, timing and starting state. No actual audio comparison is claimed by the symbolic oracle. Changing the start to 2 distinguishes the pair immediately at the second note. A performance is one itinerary through a constitution, not the entire constitution.

The missing part of the score may be far more interesting than the part heard. A musician could compose *unvisited laws* in anticipation of someone else's entrance. The dormant two states can be tuned, detuned or left inaccessible until the next participant arrives. An archive of the sounded material alone would omit this compositional domain.

## Executed qualification and limits

[Executable laboratory](laboratory.cjs) enumerates every function on 1–5 labelled states, every starting state, directly replays each orbit for twice its domain size, groups complete first-repeat trajectories, checks the closed-form unconditional and conditional censuses and checks the contrasting witnesses. The exact function body was run in the tool JavaScript execution environment before publication: 3,413 tables, 16,739 start/table combinations, 1,541 trajectory classes, 208,966 assertions passed. Domain-specific enumeration is independent of the counting formulas; no independent reviewer. Run locally with node laboratory.cjs. Native Node and full repository CI not run by this agent at this checkpoint.

The case n=1 uses the empty-product convention 0^0=1. The census includes identity, derangement, cycles, transient paths and singleton states. No missing fixed point is treated as a playback failure in the prospective model. This is not a theorem about legal systems, general recursion, cognitive agency or sound recognition.

## Exaptation: the Constitutional Organ

A prospective live sequencer whose voice has two surfaces: a sounding note and a proposed next prescription. An editor presents the currently effective table, a next-beat amendment lane and a separate speculative audit panel. The latter can sonify the fixed points as a chord, render an explicit silent/empty result with a visible explanation, or let a performer choose among the alternatives. No retroactive audition alters the past event log.

The first PoC needs only a four-state table, a start selector, next-step and reset, a bounded oscillator with an envelope, a fixed-point audition and a visual table. Render identical pitch slots from different tables as a control. Expose unvisited states and provide a separate intervention button. The table is authored, not inferred from PCM. The host's stop and amplitude boundaries are immutable; there is no eval or executable user text. For a later version, give each voice a finite transducer and let audible events propose versioned edits to another voice's table; use a two-phase commit with explicit effective tick and deterministic conflict handling. This extension is not covered by the proof.

The artistic design tension is between enacted rule, amendment, retrospective edition and an unvisited possibility. A fixed score can be astonishing; an editable score can be boring. A constitutional organ should not confuse the number of choices with artistic freedom. The performer may decline an amendment, preserve an old version as a second voice, or refuse an audition; those gestures exceed the present finite model.

## MHAC hypotheses, not findings

A machine-generated explanation can mention a proposed policy change without having permission to apply it. A later policy can classify an old event differently without being the authority that originally governed it. In a synthetic, non-actuating scenario, compare (A) latest-policy-only status, (B) explicit event-time policy version and separate later evaluation, and (C) a straightforward visual audit log. Hold event history and policy versions fixed. Score correct identification of governing rule, later evaluation, mistaken retroactive authority and time to inspect; counterbalance presentations. Include cases with no rule change and with a later rule that happens to agree. No participants or recruitment authorized. A conventional versioned event log may outperform every sound design. The proposed instrument is not an operational control or safety architecture; consequential actions need independent authorization.

## Speculative afterword: the second signature

The score appointed a conductor who was not yet in the room. She arrived just as the note ended and signed the score with a different ink. The archivist asked whether the note was now permitted. She drew a line under the note, wrote the date of her arrival, and left the previous signature untouched.

For the second performance, the archivist asked the singers to play only those notes whose amendments authorized their own arrival. The room was silent. He marked the performance as a failure.

The composer put a second label beneath his first: a successful performance of an impossible audition.

Neither label was the sound.

See the original [performance score](SCORE.md). No human performance or perceptual validation claimed.

## Reconciliation and custody

Live main AGENTS, README, RAG, Programme, Runbook, research integrity, validation, protocol overview and research workspace consulted; 65 recent PR titles and 50 open issue titles scanned, plus targeted searches. #224 covers finite decipherability (initial path abandoned); #191 concerns simultaneous signed-graph consistency; #207 concerns context-dependent commutation; #460 concerns quotation and compositional authority; #62 concerns authorized conformity decisions. The new scope is a prospective prescription transition versus a same-event fixed-point audition and conditional off-orbit law census, not a replacement for those projects. Current concurrent FX/INSTRUMENT work and newer queue/corridor research are separate. New issue #594 has no comments at inspection. Only this expedition directory is changed. No canonical evidence, frozen protocol, shared manifests or prior branches changed. AI assistance: one ChatGPT agent, web text retrieval, JavaScript tool execution and GitHub publication; no independent human review. Draft for integration; no license decision.
