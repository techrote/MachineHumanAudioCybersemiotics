# Concept register

[Protocol §7](PROTOCOL-v1.md#7-track-g-theoretical-sampling-and-concept-revision) · [Glossary](GLOSSARY-v1.md) · [Amendments](amendments/README.md)

Versioned **sensitizing concepts** for Track G. They guide sampling and reading; they are not findings and not claims about what Brier or any comparator means. Concepts evolve here under protocol §7.2. Any revision that changes a Track E eligibility rule, coding field or outcome family requires a protocol amendment before it takes effect.

**Current version: v1.1 (2026-10-13).** v1 was frozen with the protocol; v1.1 adds the MHAC-R004 post-freeze revisions R1–R5, all nonmaterial to Track E. This file is a living register, not a frozen artifact; its history is the Git history plus the revision log below.

## Sensitizing concepts (current: v1.1)

| ID | Concept cluster | Working formulation | Rival or contrasting formulations to test | RQ |
|---|---|---|---|---|
| K01 | Information | Kept plural: Shannon's quantity of selective information for a channel; Bateson's "difference that makes a difference"; semantic information as information an agent uses to maintain itself (Kolchinsky and Wolpert); Brier's claim that information is an aspect of semiosis. | Formal accounts that need no observer; deflationary engineering usage | RQ1, RQ2 |
| K02 | Meaning and interpretation | Peircean triadic sign relation (representamen, object, interpretant) as Brier uses it, versus pragmatic accounts of meaning as use and coordination. | Common-ground accounts; ecological affordance accounts; semiotic engineering's designer-to-user message; Peirce's interpretant divisions (immediate/dynamic/final and emotional/energetic/logical), whose mutual relation is contested (R1) | RQ1, RQ2 |
| K03 | Observer and system boundary | Second-order cybernetics and autopoiesis: what counts as a system, who observes, what is inside the communication. | Critiques of transferring autopoiesis to social or technical systems | RQ1, RQ2 |
| K04 | Communication | At least two senses: Luhmannian social-system communication (Brier's integration) and interface message passing between a machine and a person. | Clark's joint activity and interactional grounding, kept distinct from symbol grounding (R2); the objection that the contribution model cannot track a contribution's state on-line (R5); Shannon's channel; semiotic engineering's metacommunication | RQ1, RQ2, RQ6 |
| K05 | Embodiment and perspective | First-person experience, intersubjective meaning and third-person description, as Brier's four-world "cybersemiotic star" arranges them. | Cognitive and human-factors accounts that model only third-person performance | RQ1, RQ5 |
| K06 | Situated understanding | Project framing (glossary G25): adequate interpretation for appropriate action, counting total interpretive effort. | Recognition-only success; preference or acceptance as success | RQ3, RQ6 |
| K07 | Sign relations of sounds | Resemblance, causal connection and convention as relation-dependent, use-specific hypotheses (G14). | Fixed classifications (e.g. Peircean classes assigned to sound types in prior HCI semiotics) | RQ2, RQ4 |
| K08 | Affect and anthropomorphism | Separate prosody for intelligibility, perceived human likeness, attributed machine emotion and listener affect (G23). | Arguments that human-like or emotive voices improve trust, compliance or urgency perception, including reports that human-like synthetic voices are rated less eerie and more likable and that a natural voice raises reliance on advice (R4); depiction accounts of social agents (R4) | RQ5 |
| K09 | Urgency, hazard and action | Designed, perceived and time-to-action urgency; hazard and consequence; requested action; lifecycle (G11–G15). | Single "priority" scales in alarm standards; urgency-mapping traditions; chains from event criticality to alarm informativeness and required response time (R3) | RQ4 |

Glosses of other authors' concepts in this table are working orientations drawn from titles, abstracts, tool-mediated summaries or general background knowledge. They must be source-checked against primary text before they support any extraction or claim.

## Pre-freeze revisions

Logged during the R002 pilot on 2026-10-13. "Track E impact" records whether the revision changed an empirical rule **before** the freeze; all such changes are already part of v1.

| Rev | Concept | Change | Trigger | Track E impact |
|---|---|---|---|---|
| P1 | K09 | Urgency split into designed, perceived and time-to-action; perceived urgency analysed as mapping fidelity. | Comparator excluded urgency ratings as polarity-ambiguous; pilot urgency query | Yes: O9 definition |
| P2 | K06 | Identification separated from correct action within a deadline. | Prepass D01/D02; FRA review's delivery-versus-content observation | Yes: O2/O3 |
| P3 | K09 | Three senses of certainty: message certainty, certainty of evidence, listener confidence. | Vriend et al. operationalise uncertainty as probability | Yes: O10, G10/G24 |
| P4 | K07 | Sign relations treated as use-dependent hypotheses, not properties of sound types. | Nam (2010) assigns Peircean classes that differ from the project's earlier informal assignments | No (coding note only) |
| P5 | K06 | Sonification scope: state-coupled communication for monitoring or action is in scope; exploratory data sonification is not. | Comparator excluded continuous sonification; project includes state-coupled sound | Yes: E2, G07 |
| P6 | K06 | Memory outcomes mapped: delayed memory for message content → O6; concurrent-task memory → O8; immediate recall → O2. | Pilot title on auditory warnings and working memory; comparator's memory-for-alerted-events item | Yes: analysis plan §2 |
| P7 | K08 | Three affect constructs kept apart; conversational machine speech assessed under G01 at full text. | Pilot voice/emotion queries returned HRI trust and emotional TTS work | Yes: O12, calibration item 9 |
| P8 | K04 | "Communication" kept in two senses (Luhmannian and interface). | Brier 2010/2015 integrate Luhmann's communication theory; Thomsen and Brier 2014 build a pragmatics on it | No |
| P9 | K01 | Information kept plural with named sources for each sense. | Brier 2015's use of Bateson; Kolchinsky–Wolpert pilot query | No |

## Post-freeze revision log

| Rev | Date | Concept | Old → new | Source and passage | Track E impact check | Amendment |
|---|---|---|---|---|---|---|
| R1 | 2026-10-13 | K02 | Rival formulations: Peirce's interpretant divisions added, with their relation marked as contested | `SRC-REL-ATKIN-SEP` §§4.2–4.3 (paragraphs 43–67), including the EP2:409 quotation that every interpretant includes feeling | Nonmaterial: no eligibility rule, coding field or outcome family changes; G23 and O12 unchanged. Flagged for #8 (concept map CM07) | None |
| R2 | 2026-10-13 | K04 | "Clark's joint activity and grounding" → interactional grounding kept distinct from symbol grounding | `SRC-REL-CLARK-BRENNAN-1991` PDF p. 2 (grounding criterion); `SRC-REL-HARNAD-1990` abstract | Nonmaterial: terminology only | None |
| R3 | 2026-10-13 | K09 | Rival formulations: criticality → informativeness → compliance chain with response-time bands added | `SRC-REL-SANZSEGURA-2022` PDF p. 14 | Nonmaterial: the time-to-action outcome family already exists; no rule changes | None |
| R4 | 2026-10-13 | K08 | Rival formulations: contrary findings on human-like and natural voices, and the depiction account, added | `SRC-REL-KUHNE-2020` PDF p. 1; `SRC-REL-BECKER-2025` and `SRC-REL-CLARK-FISCHER-2022` abstracts | Nonmaterial: the empirical studies go to #6 for screening under the unchanged eligibility rules | None |
| R5 | 2026-10-13 | K04 | Rival formulations: the on-line state objection to the contribution model added | `SRC-REL-TRAUM-CONTRIB` PDF p. 3 | Nonmaterial to Track E; bears on the #12 state model | None |
