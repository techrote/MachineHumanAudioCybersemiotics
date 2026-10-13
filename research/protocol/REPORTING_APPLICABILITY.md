# Reporting and conduct guidance: applicability record

[Protocol](PROTOCOL-v1.md) · [Analysis plan](ANALYSIS_PLAN-v1.md) · [Method sources](records/)

**An applicability map, not a compliance claim.** Reporting guidelines describe what to report; they are not quality certificates and were not validated for judging this protocol. Each row says where v1 addresses an item, or why it does not apply. Readings were by the executing agent only: the 1B prepass read PRISMA 2020, PRISMA-S and Dixon-Woods et al. (selected ranges with page images, 2026-10-04); this freeze added tool-mediated readings of PRISMA-P, SWiM, the EGM guidance, the 2025 AI position statement, PRESS 2015 and Cochrane Handbook chapter 11 (2026-10-13). Source records are in [`records/`](records/).

## PRISMA-P 2015 (Moher et al., Table 3)

PRISMA-P addresses protocols for reviews of aggregate data, chiefly interventions; its authors encourage use "as applicable" for other review types.

| Item | Topic | v1 location / status |
|---|---|---|
| 1a–1b | Identification; update | Title of PROTOCOL-v1; not an update protocol |
| 2 | Registration | Not registered; stated in §1 and FREEZE.md |
| 3a–3b | Authors and contributions | Executing agent and repository owner identified in FREEZE.md; no invented authorship or affiliations |
| 4 | Amendments | §14 and the amendment register |
| 5a–5c | Support and sponsor roles | No funding; recorded in FREEZE.md |
| 6–7 | Rationale; objectives | §2 and `docs/RESEARCH_PROTOCOL.md`; PICO elements are approximated by E1–E4, adapted because the review is not an intervention-effect review |
| 8 | Eligibility | §4 |
| 9 | Information sources with dates | §5.1 |
| 10 | Draft strategy for at least one database | §5.2 (EQ1–EQ8 and the OpenAlex reference form) |
| 11a–11c | Data management; selection; extraction | §6; contacting investigators is not authorized |
| 12 | Data items | Analysis plan §5 |
| 13 | Outcomes and prioritisation | Analysis plan §2, §6.2 |
| 14 | Risk of bias | §8 |
| 15a–15d | Synthesis criteria, methods, additional analyses, non-quantitative summary | Analysis plan §7–§10 |
| 16 | Meta-biases | Analysis plan §10 |
| 17 | Confidence in cumulative evidence | §8 body-of-evidence judgement |

## PRISMA-S (Rethlefsen et al. 2021), items 1–16

| Items | Topic | v1 status |
|---|---|---|
| 1–3 | Databases, multi-database searching, registers | §5.1 names platform and interface; registers not applicable (no trial registers for this field) |
| 4 | Online resources and browsing | C5 and C8, with the C8 limits stated |
| 5–7 | Citation searching; contacts; other methods | C9; contacts not authorized; C10 grey literature |
| 8 | Full search strategies | EQ1–EQ8 plus as-run strings in every search record |
| 9–11 | Limits; filters; prior work | Date limit only; no methodological filters; no strategy reused from prior reviews (the Nees–Liebman terms are a subset of EQ1) |
| 12–13 | Updates; dates | #17 refresh; actual run dates in search records |
| 14 | Search peer review | **Not available**; agent self-check below; disclosed limitation |
| 15–16 | Total records; deduplication | Search records and §6.2 |

## PRISMA 2020

Applies to the eventual report (#16–#18). v1 prepares the items whose content must be fixed in advance: eligibility (item 5), sources and strategy (6–7), selection and collection processes with automation disclosure (8–9), data items and outcomes (10), risk of bias (11), effect measures (12), synthesis methods including non-pooled routes (13a–f), reporting bias (14) and certainty (15). Item 24 (registration and protocol) will state that the protocol is internal and unregistered.

## SWiM (Campbell et al. 2020), items 1–9

All nine items are mapped in analysis plan §9. SWiM is used for reporting non-pooled syntheses; it does not prescribe conduct, which is governed by the analysis plan.

## Campbell evidence and gap map guidance (White et al. 2020)

Adopted elements: a two-dimensional framework (representation/manipulated property × outcome family) piloted before production; coding of both reviews and primary studies with reviews used for chaining rather than counted as studies; appraisal shown alongside the map. Not adopted: stakeholder co-design of the framework (no stakeholders are authorized for contact), and the guidance's preference for excluding effect direction from maps — Track E adds within-cell synthesis because RQ3 asks what is known, not only what exists.

## AI use (Flemyng et al. 2025 position statement; RAISE)

| Requirement | v1 location |
|---|---|
| Authors remain responsible for AI use and its impact | Owner and executing agent roles in FREEZE.md; §10 |
| Report AI that makes or suggests judgements: tool, version, dates, purpose, stages, justification and piloting, interests, limitations | §10 and `assistance` records for every stage |
| Human oversight | **No human oversight exists at freeze.** This departs from the position statement's expectation and is disclosed as a principal limitation; any owner check will be recorded with its scope |
| Pilot or calibrate tools within the synthesis | Pilot report §4, §6–§7 |
| Ethical and legal issues (copyright, provenance, licensing) | `docs/RESEARCH_INTEGRITY.md`; no restricted text committed |

RAISE documents were identified through the position statement only and were not read.

## PRESS 2015

PRESS describes review by a second librarian or information specialist. No such reviewer is available, so v1 has none. The executing agent checked EQ1–EQ8 against the six PRESS elements before freezing, which is a self-check and not a PRESS review:

| Element | Self-check result |
|---|---|
| Translation of the question | Concept blocks follow RQ3's message and outcome concepts. Risk: EQ1's study-type block may miss abstracts that never use those words; EQ5/EQ7 and chaining partly compensate. |
| Boolean and proximity operators | Parenthesized explicitly. No proximity operators: to the agent's general knowledge OpenAlex title/abstract search does not offer them (to be confirmed at execution). |
| Subject headings | None. OpenAlex's topic classifications are algorithmic rather than an indexing thesaurus, and thesaurus-based databases (e.g. PsycINFO) are not accessible. Disclosed limitation. |
| Text words | Added before freeze: `audio cue(s)`, `auditory menu(s)`, `lyricon(s)`, `spindex`, `musicon(s)`, `auditory/acoustic beacon(s)`, `sonified`. British and US spellings of anaesthesia included. No wildcards, because their OpenAlex support is unconfirmed; plural forms are listed explicitly. |
| Spelling and syntax | Checked by eye; platform acceptance is unknown until execution. |
| Limits and filters | Date only; no language, document-type or open-access filter. |

## Cochrane Handbook chapter 11

Used only to justify not planning network meta-analysis (analysis plan §8).
