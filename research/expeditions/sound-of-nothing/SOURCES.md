# MHAC-X005 — source ledger

Checked 23 November 2026 through public publisher, institutional and project pages. The entries below are comparison lenses, not automatically admitted MHAC empirical evidence.

## X005-S01 — Fischer, Lynch & Paterson (1985)

Michael J. Fischer, Nancy A. Lynch and Michael S. Paterson, “Impossibility of Distributed Consensus with One Faulty Process,” Journal of the ACM 32(2):374–382. DOI 10.1145/3149.214121.

Accessible metadata/abstract: ACM and MIT repository. A public HTML transcription of the JACM paper was also inspected for the system-model passage.

Actually inspected:
- abstract;
- opening model discussion stating that the system is completely asynchronous;
- explicit statement that no assumptions are made about process speeds or message-delivery delay;
- statement that no failure detector is postulated, so another process cannot tell whether a process has stopped or is merely very slow.

Use here: motivates the narrow indistinguishability construction.

Limit: FLP proves a consensus nontermination result. X005 does **not** claim that an auditory interface is a consensus protocol or that our theorem is FLP.

## X005-S02 — Chandra & Toueg (1996)

Tushar D. Chandra and Sam Toueg, “Unreliable Failure Detectors for Reliable Distributed Systems,” Journal of the ACM 43(2):225–267. DOI 10.1145/226643.226647.

Actually inspected: Cornell/IBM public abstract and bibliographic record.

Source-reported contribution: failure detectors are characterized by completeness and accuracy properties; consensus can be solved with certain unreliable detectors even when they can make mistakes.

Use here: a warning that “suspected failed” is an abstract property with accuracy/completeness tradeoffs, not identical to observed silence.

Limit: full body/theorems were not rederived or comprehensively read in this execution.

## X005-S03 — Aguilera, Chen & Toueg (1997)

Marcos Kawazoe Aguilera, Wei Chen and Sam Toueg, “Heartbeat: A Timeout-Free Failure Detector for Quiescent Reliable Communication,” WDAG 1997, LNCS 1320:126–140.

Actually inspected: Cornell/Microsoft abstract and publicly accessible opening text.

Source-reported contribution: quiescent reliable communication in asynchronous crash/lossy-link systems cannot be achieved in the stated setting without failure-detector machinery; the paper proposes a heartbeat detector whose implementation does not use timeouts.

Use here: direct counterexample to the lazy equation “failure detector = timeout after silence.”

Limit: the paper's heartbeat abstraction is not an auditory heartbeat and no transfer to human alarms is established.

## X005-S04 — Hayashibara et al. (2004), phi accrual failure detector

Naohiro Hayashibara, Xavier Défago, Rami Yared and Takuya Katayama, “The Phi Accrual Failure Detector,” SRDS 2004.

Actually inspected: publicly accessible paper excerpt describing periodic heartbeat messages, timeout tradeoffs, asynchronous-system definition, and the accrual approach; Akka documentation was also inspected as an implementation reference.

Use here: shows a practical alternative where elapsed silence increases a graded suspicion score relative to observed timing rather than magically revealing a crash.

Limit: no claim that phi values are probabilities of death or suitable human urgency mappings.

## X005-S05 — Binary erasure channel

Cambridge University Press, Richardson & Urbanke, Modern Coding Theory, binary-erasure-channel chapter summary; plus public information-theory lecture material.

Actually inspected: publisher summary and lecture-note descriptions.

The useful structural fact: the BEC output alphabet contains the valid symbols and a **separate erasure symbol**. When erasure occurs, the receiver knows that the transmission was erased but not the lost bit value.

Use here: an epistemic foil. An explicit erasure marker says “unknown due to loss”; receiving a legitimate zero says something else.

Limit: literal non-arrival of a packet or acoustic silence is not automatically a BEC erasure symbol. The channel model makes erasure observable by assumption.

## X005-S06 — Ephratt (2008)

Michal Ephratt, “The functions of silence,” Journal of Pragmatics 40(11):1909–1938. DOI 10.1016/j.pragma.2008.03.009.

Actually inspected: publisher abstract.

The abstract distinguishes pause from chosen “eloquent silence” and argues that communicative silence can perform referential, emotive, conative, poetic, phatic and metalinguistic functions.

Use here: strong counterexample to “silence contains no information.”

Limit: deliberate human communicative silence depends on a linguistic/social context; it does not show that technical channel silence is meaningful.

## X005-S07 — Ephratt (2011)

Michal Ephratt, “Linguistic, paralinguistic and extralinguistic speech and silence,” Journal of Pragmatics 43(9):2286–2307. DOI 10.1016/j.pragma.2011.03.006.

Actually inspected: publisher abstract.

Use here: reinforces that “silence” is not one homogeneous category and that communicative analyses distinguish multiple mappings/roles.

Limit: body not read; no numerical listener effect is imported.

## X005-S08 — Kurzon (2007)

Dennis Kurzon, “Towards a typology of silence,” Journal of Pragmatics 39(10):1673–1688. DOI 10.1016/j.pragma.2007.07.003.

Actually inspected: publisher abstract.

Source-reported contribution: proposes conversation, thematic, textual and situational silence, with examples from libraries, classrooms, political speech, remembrance, theatre and music.

Use here: another reason not to flatten all silence into “absence of data.”

## X005-S09 — philosophy of absence

Stanford Encyclopedia of Philosophy, “The Metaphysics of Causation,” current online entry; Stephen Mumford, Absence and Nothing (OUP 2021), chapter “Causation by Absence”; Phillip Meadows (2024), “Error Theories of Absence Causation Are Not (Yet) Adequately Motivated.”

Actually inspected:
- SEP section discussing the argument from absences and competing responses;
- Mumford chapter abstract arguing that absences may explain without themselves being causal;
- Meadows open-access abstract arguing that eliminativist/error-theory motivations remain inadequate.

Use here: preserve the distinction between **citing an absence in an explanation** and settling what metaphysical entity, if any, does causal work.

Limit: X005 is not a contribution to the metaphysics of causation.

## X005-S10 — Cage's 4′33″ as an artistic counterpoint

Museum of Modern Art collection/exhibition materials on John Cage's *4′33″* and the John Cage Trust's 4′33″ project were inspected.

Actually inspected: MoMA's description of the work as three timed movements in which the performer intentionally produces no sound, redirecting attention toward ambient/environmental sound; John Cage Trust project description identifying the work and recordings of environmental performances.

Use here: a useful artistic correction to the phrase “pure silence.” Cage's work structures an interval of **no intentional performer sound** while making surrounding sound newly salient. That is different from X005's deliberately manufactured PCM-zero window.

Limit: no musicological claim about Cage's complete aesthetics is made, and no score/manuscript copyright material is reproduced. The connection is conceptual/artistic, not empirical evidence about machine interfaces.

## X005-S11 — internal MHAC comparators

- T005 #36: persistent-state audio, discrete events, change deafness and all-clear failure; specifically warns against inferring cleared state merely from sound cessation.
- T010 #47: freshness/deferral versus durable action obligations.
- T003 #33: repair, acknowledgement, understanding, resolution and deadlines.

Use here: keep ownership boundaries explicit.

## X005-S12 — internal exaptation source: MHAC-X001

MHAC-X001, *The Observer's Solecism*, `research/expeditions/observers-solecism/MATHEMATICS.md`, provides the already-authored observation-factorisation theorem used by X005.

Actually reused: only the abstract criterion that a hidden-state verdict is recoverable from an observation exactly when it is constant on each observation fibre.

Not reused: the grammatical, circle-harmonic, Kaluza–Klein or moving-probe scenery.

Use here: documented internal exaptation rather than pretending X005 independently invented the same theorem.


## X005-S13 — Alpern & Schneider (1985), liveness

Bowen Alpern and Fred B. Schneider, “Defining Liveness,” Information Processing Letters 21(4):181–185; Cornell TR 85-650.

Actually inspected: Cornell technical-report text, especially the abstract and sections 2–3. The paper formalises liveness so that every partial execution can be extended to satisfy the property; guaranteed service (“every request is eventually satisfied”) is given as an example.

Use here: a clean formal reason that an unbounded “eventually delivered” obligation cannot be refuted merely by observing a finite quiet prefix.

Limit: X005's finite three-valued monitor is an original didactic simplification, not the paper's full topology or proof framework.

## X005-S14 — Reiter (1977/1978), open and closed worlds

Raymond Reiter, “On Closed World Data Bases,” UBC Technical Report 77-16 (October 1977), later in *Logic and Data Bases* (1978), DOI 10.1007/978-1-4684-3384-5_3.

Actually inspected: UBC public technical-report abstract/record and its statement of the two assumptions. Under the closed-world convention, failure to prove a positive ground literal licenses assuming its negation in the stated database setting; the report also discusses conditions and inconsistency risks.

Use here: makes explicit that “missing fact -> false” can be a **reasoning policy** rather than a discovery about reality.

Limit: X005's open_world_query helper is not a logic-programming/database implementation and does not inherit Reiter's Horn-database results.

## X005-S15 — W3C OWL 2 open-world example

W3C OWL 2 Structural Specification / archived Structural Reference Experiment.

Actually inspected: W3C text explaining the open-world assumption with an example in which the ontology says an individual is a dog but says nothing about whether it is a bird; lack of the bird assertion does not entail the complement because the ontology may simply lack that information.

Use here: an official knowledge-representation counterpoint to closed-world negation-from-failure.

Limit: no claim that MHAC semantic state should be encoded in OWL.

## X005-S16 — runtime-monitoring / finite-trace inconclusiveness

Alpern–Schneider supplies the historical liveness foundation; a modern runtime-verification discussion was also inspected for the familiar finite-prefix idea that a monitor can remain inconclusive when both satisfying and violating infinite continuations are still possible.

Use here: terminology support for X005's SATISFIED / VIOLATED / INCONCLUSIVE toy monitor.

Limit: X005 does not implement LTL, Büchi automata or predictive runtime verification.


## Source conclusion

The useful cross-domain pattern is not that all these literatures “say the same thing.” They do not.

Instead:

- distributed systems expose limits of inference under weak timing/failure assumptions;
- coding theory can **make loss explicit** as a symbol;
- pragmatics shows that intentional silence can be communicative;
- philosophy asks whether absences themselves cause or merely explain;
- MHAC asks what a machine should communicate so a listener does not silently promote UNKNOWN to RESOLVED.

That separation is the actual research result.
