# Novelty and overlap matrix — MHAC-R002

[Novelty index](README.md) · [Nees–Liebman record](COMPARATOR_NEES_LIEBMAN_2023.md) · [CSV](OVERLAP_MATRIX.csv) · [Protocol](../protocol/PROTOCOL-v1.md)

**Novelty is treated as an open question.** Each cell states what an inspected comparator appears to cover, how much of it was actually read, and what would overturn the judgement. "Not found" always means *not found in the material inspected here*; it never asserts a literature-wide gap. The audit is bounded to comparators reachable on 2026-10-13 without paid access, new accounts or contact. Source records: [`research/novelty/records/`](records/).

## Overlap status vocabulary

| Status | Meaning |
|---|---|
| `covered` | An inspected comparator addresses this question with comparable scope; MHAC work would be replication or update. |
| `partly_covered` | Components are addressed somewhere, but the MHAC question's combination or unit of analysis was not found. |
| `not_found_inspected` | No inspected comparator addresses it. Inspection extent is stated; wider searches may find it. |
| `unknown` | The relevant comparator was identified only by title/metadata or not identified; no judgement possible. |

## Comparators and actual reading extent

| ID | Comparator | Record | Reading extent |
|---|---|---|---|
| C1 | Nees & Liebman, brief audio alert SR/MA (preprint 9.8.22 of the 2023 article) | `SRC-NOV-NEES-LIEBMAN-2023-PREPRINT` | Tool-mediated full-text paraphrase of preprint; VoR, figures and appendices unread |
| C2 | Jeon, Lautala, Nadri & Nelson (2022), FRA *In-Vehicle Auditory Alerts Literature Review*, DOT/FRA/ORD-22/05 | `SRC-NOV-FRA-IVAA-2022` | Repository landing page summary only |
| C3 | *Design Considerations for Auditory Alarms in the Process Industry: A Systematic Literature Review* (USN open archive) | — (search title only) | Title only; authors/date unverified; no record created |
| C4 | Nam (2010), *A semiotic analysis of sounds in personal computers* (de Gruyter) | `SRC-NOV-NAM-2010` | Abstract only |
| C5 | Vriend, Hägele & Weiskopf (2025), *Two Empirical Studies on Audiovisual Semiotics of Uncertainty* (Audio Mostly 2025; arXiv 2505.14379) | `SRC-NOV-VRIEND-2025` | Tool-mediated full text (first 100,000 of 105,254 characters) |
| C6 | de Souza (2005), *The Semiotic Engineering of Human-Computer Interaction*; Valente, de Souza & Feijó (2009), non-visual mobile game interfaces | `SRC-NOV-DESOUZA-2005`, `SRC-NOV-VALENTE-2009` | Book: retail/catalogue metadata only. 2009 article: abstract only |
| C7 | Brier (2010) *Entropy* 12(8); Brier (2015) *Studia kulturoznawcze* 1(7) | `SRC-NOV-BRIER-2010`, `SRC-NOV-BRIER-2015` | Tool-mediated paraphrase of 2010 (first 100,000 of 110,193 characters) and of the 2015 publisher version |
| C8 | Thomsen & Brier (2014), cybersemiotic discourse pragmatics, *Public Journal of Semiotics* 6(1) | `SRC-NOV-THOMSEN-BRIER-2014` | Abstract only |
| C9 | Cobley (2010), *Cybersemiotics and Human Modelling*, *Entropy* 12(9) | `SRC-NOV-COBLEY-2010` | DOAJ record abstract only |
| C10 | Urgency-mapping literature, e.g. the Plymouth record "On using psychophysical techniques to achieve urgency mapping" | — | Search title only; not read |

## Matrix

| ID | MHAC question or candidate contribution | Comparator evidence | Status | Consequence for MHAC scope | Revision trigger |
|---|---|---|---|---|---|
| N01 | Rank auditory icons, earcons, spearcons and speech on identification accuracy, response time, preference, workload and dual-task cost (RQ3) | C1 does exactly this with searches to mid-2021, k = 11–50 per outcome and an NMA ranking | `covered` | MHAC will **not** produce another cue-family ranking. Any such comparison is an explicitly labelled update or sensitivity check against C1, never a novelty claim. | VoR shows materially different scope; or a later review already updates C1 |
| N02 | Separate recognition/identification from correct task action within a deadline (RQ3, RQ6) | C1 codes accuracy as % correct and describes tasks descriptively; no action-versus-identification distinction found. C2 summary says research has focused on how messages are delivered rather than their content (rail-crossing domain). | `not_found_inspected` | Retained as an evidence-map axis and estimand family (O1 vs O2). Value claimed only if primary studies with action outcomes exist and the separation changes conclusions. | A review or standard already separating identification from action is found in R004/R005 |
| N03 | Training dose, learning burden and delayed retention as distinct outcomes (RQ3) | C1 did not code training, practice or retention (tool-mediated reading). Pilot found primary learnability/retention reports (titles only). | `not_found_inspected` | Retained as outcome families O4/O5 with explicit dose and delay windows. | A review of auditory-cue learning/retention is located |
| N04 | Perceived urgency and its mapping to hazard, severity and time-to-action (RQ3, RQ4) | C1 excluded urgency ratings as polarity-ambiguous. A substantial urgency-mapping literature exists (C10, unread). | `unknown` | MHAC must not claim novelty here. R004/R005 must locate urgency-mapping reviews and standards before any synthesis proposition is drafted. Urgency is analysed as mapping fidelity, not "higher is better". | Urgency-mapping reviews read; overlap re-judged |
| N05 | Message certainty/uncertainty conveyed by sound (RQ4) | C5 tests audiovisual mappings for probability (loudness, pitch, tempo with visual channels; N = 170/185 crowd-sourced) without alerts, urgency or action; reports that preferred pairings are not necessarily good probability mappings. "Sounds Uncertain" (arXiv 2608.18680) is affect-focused but unread. | `partly_covered` | Uncertainty sonification is an existing line; MHAC's possible contribution is only its integration with urgency, hazard and requested action in alerts. | Evidence that integrated uncertainty-plus-action alerts were already studied |
| N06 | Keep source, certainty, hazard, consequence, urgency, persistence and action distinct in one model (RQ4) | No inspected comparator integrates these dimensions. Pieces exist: urgency mapping (C10), uncertainty mapping (C5), delivery/content distinction (C2). | `partly_covered` | Candidate integrative contribution, conditional on R004 finding no equivalent human-factors or alarm-standard model and on the remove-Brier test. | A human-factors alarm taxonomy or standard already encoding these dimensions |
| N07 | Retaining functions without performed human emotion; distinguishing prosody, human likeness, attributed emotion and listener affect (RQ5) | C1 does not address human likeness or affect. Pilot queries surfaced HRI voice/trust and synthetic-emotion work (titles only). | `unknown` | Open RQ; no contribution claimed. R005 cluster A4 must search this specifically, including contrary evidence favouring human-like voices. | Reviews of voice anthropomorphism/emotion in alerts located |
| N08 | Peircean sign-type classification of interface sounds (icon/index/symbol) | C4 already classifies verbal messages, earcons and auditory icons with Peircean sign classes and links interpretation effort to communicability. Its classes differ from the project's earlier informal assignments. | `partly_covered` | MHAC cannot present Peircean classification of alert sounds as new. Sign relations are treated as relation-dependent hypotheses (glossary G14). | Full C4 reading or further semiotics-of-sound literature |
| N09 | Communication-centred evaluation of interfaces via designer-to-user messages (RQ6) | C6 semiotic engineering provides metacommunication and communicability evaluation and has been applied to aural/tactile mobile interfaces (2009 abstract). | `partly_covered` | Strong redundancy risk: any MHAC evaluation contract must state what it adds beyond semiotic engineering. R004/R008 must read de Souza's core chapters. | Close reading shows semiotic engineering lacks or already supplies the RQ4 distinctions |
| N10 | Apply cybersemiotics to machine–human audio communication (RQ1–RQ6) | Inspected Brier texts (C7) do not address HCI, interfaces or sound; they mention robots/machines only in passing. C8 applies cybersemiotics to discourse pragmatics; C9 critiques its constructivism. **Updated in R003:** Jacques (2021), chapter 10 of the Vidales and Brier volume, applies Brier's framework to user-interface design and interactive environments; its abstract and visible notes show no sound, alerts or user evaluation (abstract only, `SRC-BRIER-REC-JACQUES-2021-CH10`). | `partly_covered` | A cybersemiotic HCI application already exists, so MHAC cannot claim to be the first; an audio-message application was still not found. Only the remove-Brier test (R011) can show whether anything substantive changes. | Reading Jacques (2021) in full; any located cybersemiotic audio work; or the subtraction test showing no change |
| N11 | Critical reconstruction of Brier's programme (RQ1) | Brier's own expositions (C7) and an edited introductory volume exist; reception includes Cobley (C9). | `partly_covered` | Reconstruction is a dependency for the applied question, not a claimed contribution. Value lies in locator-bound fidelity and critique. | — |
| N12 | Comparison of cybersemiotics with alternatives and a subtraction test (RQ2) | No inspected source compares cybersemiotics with human-factors or semiotic-engineering accounts for interface communication. | `not_found_inspected` | Retained as the decisive applied test; outcome may be that the contribution is organisational only or redundant. | R004 reception search finds such a comparison |
| N13 | Update of the brief-alert evidence after C1's 2021 search | C1 searched April–June 2021. Pilot surfaced at least one later relevant report (2022 working-memory study). | `not_found_inspected` | A dated update window (2021-04-01 to 2026-10-04) is a legitimate, modest aim, reported as an update rather than novelty. | Another update review located |

## Conditional conclusion

Read together, the inspected comparators make a broad cue-family empirical review redundant (N01) and leave open, at most, (a) an evidence map organised by message semantics, action, training and retention rather than by cue family (N02, N03, N06), (b) an honest update window (N13), and (c) a critical test of whether cybersemiotics changes anything relative to human-factors and semiotic-engineering accounts (N09, N10, N12). Each remains a question. N04, N07 and N09 carry the highest risk of hidden redundancy because the relevant comparator literatures were identified but not read. The [protocol](../protocol/PROTOCOL-v1.md#novelty-and-scope-consequences) converts these consequences into scope rules.

## Revision log

| Date | Row | Change | Trigger |
|---|---|---|---|
| 2026-10-13 | N10 | `not_found_inspected` → `partly_covered` | MHAC-R003 found an HCI chapter applying cybersemiotics (Jacques 2021) in the Vidales and Brier table of contents |

## Limits

One agent performed this audit with web search and a summarising fetch tool. There was no independent human check, no subscription database search and no VoR for C1. Abstract-only comparators (C4, C8, C9, part of C6) support only the cell statements above. The matrix must be rerun after R004/R005 locate urgency-mapping, voice-anthropomorphism and semiotic-engineering sources.
