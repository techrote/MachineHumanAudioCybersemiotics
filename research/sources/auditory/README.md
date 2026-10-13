# Auditory evidence search — MHAC-R005 coverage memo

[Search log](../../searches/auditory/README.md) · [Export](../../searches/auditory/exports/AUDITORY-WEBSEARCH-2026-10-13.json) · [Access ledger](../../searches/auditory/exports/ACCESS-LEDGER-R005-2026-10-13.csv) · [Known-item table](../../searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv) · [Build script](scripts/build_r005_records.py) · [Protocol §5](../../protocol/PROTOCOL-v1.md#5-track-e-sources-and-searches)

> **Coverage-limited search. No bibliographic database was searched.** Discovery relied on web search (C8), ICAD-host and grey-literature routes through the same engine (C5, C10) and two review reference lists (C9). This is the protocol's predeclared fallback (§5.3), not a silent narrowing, and it limits every completeness claim. Nothing here is a screening decision: every occurrence is still unscreened.

## Contents

| # | Section | Summary |
|---|---|---|
| 1 | [Status and scope](#1-status-and-scope) | What ran on 13 October 2026 and under which rule. |
| 2 | [Channel outcomes](#2-channel-outcomes) | C1–C10 with status, yield and impact. |
| 3 | [What ran](#3-what-ran) | Batches, counts and record identifiers. |
| 4 | [Known-item check](#4-known-item-check) | How many of 68 known eligible-type reports the web routes could find. |
| 5 | [Targeted, negative, non-English, grey and contrary probes](#5-targeted-negative-non-english-grey-and-contrary-probes) | Yield of W2–W9, translations and grey routes. |
| 6 | [Review and primary-study overlap](#6-review-and-primary-study-overlap) | Reviews located, items both reviews cite, leads for #4. |
| 7 | [Possible duplicate publications](#7-possible-duplicate-publications) | Conference/journal, thesis/article and repository duplicates to resolve in #6. |
| 8 | [Access is not an exclusion criterion](#8-access-is-not-an-exclusion-criterion) | How restrictions are recorded. |
| 9 | [Unresolved gaps and stopping](#9-unresolved-gaps-and-stopping) | What is missing and why the search stops here. |
| 10 | [Handoffs](#10-handoffs) | What #6, #4, #9 and #17 receive. |
| 11 | [Reproduction and limits](#11-reproduction-and-limits) | How to rebuild the records and what the agent could not do. |

## 1. Status and scope

| Item | Record |
|---|---|
| Protocol | [v1](../../protocol/PROTOCOL-v1.md), frozen 2026-10-13; search cut-off 2026-10-04 |
| Gate check (batch A0) | 02:05–02:16 UTC: OpenAlex refused in the owner's built-in browser and by the workspace proxy; Crossref refused by the proxy; no owner exports. [HG-R002-DATABASE-ACCESS](../../protocol/gates/HG-R002-DATABASE-ACCESS.md) is still `waiting`, so §5.3 applies. |
| Executing agent | Claude in a claude.ai cloud session (configured model `claude-opus-5-5`); WebSearch, WebFetch, shell. No human took part. |
| Assistance record | `AID-R005-AUDITORY-SEARCH` |
| Lane outputs | 124 `search_run` and 1,271 `search_hit` records under [`research/searches/auditory/records/`](../../searches/auditory/records/) |

## 2. Channel outcomes

| Channel | Outcome | Records | Impact on coverage |
|---|---|---|---|
| C1 OpenAlex | `failed`: availability probes refused | `SRCH-R005-C1` | No reproducible database counts, no field-scoped EQ1–EQ8 search and no forward citation chaining. The largest single loss. |
| C2 Crossref | `failed`: probe refused (proxy 403) | `SRCH-R005-C2` | No DOI-level metadata sweep or resolution. |
| C3 ACM DL | `planned`: owner-run export only | `SRCH-R005-C3` | CHI, AutoUI, ASSETS and ICMI coverage depends on the web index: 8 of 18 ACM items in the known-item list were not found by title or only by a file name (§4). |
| C4 IEEE Xplore | `planned`: owner-run export only | `SRCH-R005-C4` | The one IEEE item in the known-item list was not found. |
| C5 ICAD | `partial`: nine W strings restricted to ICAD hosts (90 occurrences); year-by-year browse `failed` | `SRCH-R005-IW1`–`IW9`, `IIDX`, `C5BROWSE` | ICAD remains the best-covered venue (12 of 16 known ICAD items found), but no proceedings year was browsed, so per-year coverage is **unknown for every year 1992–2026**. |
| C6 SAGE / T&F | `planned`: publisher search gated | `SRCH-R005-C6` | Human-factors venues are the weakest point: 8 of 13 SAGE items (*Human Factors*, HFES proceedings) were not found by exact-title lookup. |
| C7 PsycINFO, WoS, Scopus | `planned`: subscription | `SRCH-R005-C7` | No psychology-database or citation-index coverage; non-English journal coverage unknown. |
| C8 web search | `partial` (no pagination): W1–W9, W1 extended, seven translations | `SRCH-R005-AW1`… (17 runs) | Supplementary discovery only; cannot establish coverage. |
| C9 backward chaining | `partial`: two review lists read (183 entries), 68 known-item lookups; process-industry review list `failed` | `SRCH-R005-RLNL`, `RLFRA`, `K01`–`K68`, `RLPSLR` | Chaining from included reports waits for screening (#6); forward chaining needs C1. |
| C10 grey literature | `partial`: W1–W9 on ROSA P, NASA NTRS and DTIC hosts; W1–W9 on OATD and three purposive repositories | `SRCH-R005-GW1`–`GW9`, `TW1`–`TW9` | Transport and defence reports are reasonably represented; thesis coverage is purposive (OATD returned nothing through the engine). |

## 3. What ran

All times UTC, 13 October 2026. Each run's exact string, mode, domain restriction and call time is in the [export](../../searches/auditory/exports/AUDITORY-WEBSEARCH-2026-10-13.json).

| Batch | Window | Content | Runs | Occurrences | Distinct URLs |
|---|---|---|---|---|---|
| A1 | 02:05:19–02:05:41 | C8: W1–W9 standard, W1 extended, W1 in DE, FR, ES, PT, ZH, JA, KO | 17 | 160 | 132 |
| A2 | 02:05:41–02:12:25 | C9: quoted-title lookup for each of 68 RL-NL entries | 68 | 640 | 510 |
| A3 | 02:12:25–02:15:21 | C5 route (9 + archive lookup), C10 reports (9), C10 theses (9), process-industry review lookup (1) | 29 | 288 | — |
| RL-NL | 00:59 (fetched in R002, reused) | Nees & Liebman preprint, "References Used in Meta-analyses" | 1 | 68 | — |
| RL-FRA | 02:13–02:15 | FRA in-vehicle auditory alerts review (DOT/FRA/ORD-22/05), full reference list | 1 | 115 | — |
| Gated | 02:05–02:16 | C1, C2 probes; C3, C4, C6, C7 planned; C5 browse and process-industry list failed | 8 | 0 | — |

Topic runs (A1 and A3) returned 355 distinct URLs; known-item runs 510; 35 URLs overlap; 830 in all. Nine occurrences match existing source records by identical identifier (the Nees–Liebman article, the FRA review, Vriend et al. 2025, Nam 2010); all others stay `unresolved` for #6.

## 4. Known-item check

The 68 reports Nees and Liebman list as entering their meta-analyses are the closest available set of known eligible-type studies. Each was looked up by its quoted title phrase and author (A2). Outcomes are title-level only ([table](../../searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv)):

| Outcome | Count | Meaning |
|---|---|---|
| `located` | 38 | A result title, or a DOI inside a result URL, matches the entry |
| `possible` | 9 | Only a file name, record key or institutional record suggests it |
| `not_located` | 21 | Neither (one of these, Suh et al. 2012, was found by a topic run instead) |

Two further results bound what the fallback can do:

- **Topical recall is low.** Only 11 of the 68 titles (12 if the 2006 conference version of Walker et al. is counted) appeared anywhere in the 46 topic and navigational runs (A1 + A3), about one in six. Exact-title lookups are not a discovery strategy for unknown studies, so this is the better indicator of what C8/C5/C10 find unaided.
- **Losses concentrate in human-factors and HCI venues.** Not located or only `possible`: 8 of 13 SAGE items, 8 of 18 ACM items, 4 of 16 ICAD items, the single IEEE and Wiley items. These are exactly the venues C3, C4, C6 and C7 would cover.

Consequence: web-route discovery cannot support any statement that a type of study is absent. The Track E map must carry the coverage-limited label until the database gate is satisfied.

## 5. Targeted, negative, non-English, grey and contrary probes

Protocol §12 batches A3–A8 were run as the single frozen web string per cluster. Characterisation below is from result titles only; nothing was read.

| Probe | Run(s) | What came back (titles) |
|---|---|---|
| Urgency, hazard (EQ2) | A-W2, I-W2, G-W2, T-W2 | Urgency-coding and urgency-mapping items, transport crash-warning reports, alarm-categorisation thesis |
| Voice, human likeness, affect (EQ3) | A-W3, I-W3, G-W3, T-W3 | Mostly off-target: voice trust in deepfake and dialogue settings, trust-in-automation theses. **A gap**: the contrary-evidence question (do human-like voices help?) is not served by web search. |
| Uncertainty (EQ4) | A-W4, I-W4, G-W4, T-W4 | Uncertainty-sonification studies, including the already recorded Vriend et al. (2025) and an affect-focused uncertainty study |
| Learning, retention (EQ5) | A-W5, I-W5, G-W5, T-W5 | Learning and retention of auditory warnings; learned alarm sounds and working memory; habituation to alerts in locomotive cabs |
| Monitoring sonification (EQ6) | A-W6, I-W6, G-W6, T-W6 | Pulse-oximetry sonification laboratory studies; patents; the grey routes returned off-target clinical items |
| Interruption, workload (EQ7) | A-W7, I-W7, G-W7, T-W7 | Dual-task and distraction reports, including a Traditional Chinese-language item on dual-task distraction and warning-sound feedback |
| Null-oriented probe | A-W9, I-W9, G-W9, T-W9 | A speech versus non-speech warning comparison, alarm literature reviews; mostly unrelated speech-perception items |
| Non-English (W1 translations) | A-W1-DE … A-W1-KO | DE, FR, ES, PT, ZH and JA runs returned almost only English items. KO returned Korean-language items (mobile auditory icons, ship-bridge alarm experiments). Non-English coverage is therefore minimal. |
| Grey: reports | G-W1–G-W9 | DOT/NHTSA/FAA/FRA, NASA and DTIC reports on crash-avoidance alerts, aviation non-speech audio, spacecraft caution-and-warning design and alarm literature reviews |
| Grey: theses | T-W1–T-W9 | Theses and papers from Virginia Tech, Michigan Tech and Glasgow repositories; OATD contributed nothing |

The update window for the cue-family comparison (§12 A7, 2021-04-01 to 2026-10-04) could not be run as a separate search because the web tool has no date filter; post-2021 reports must be identified at screening from these runs, and their recall is unknown.

## 6. Review and primary-study overlap

Reviews are discovery and coverage aids; under protocol §6.4 a review never contributes primary observations.

**Reviews and frameworks located**

| Item | Where found | Status |
|---|---|---|
| Nees & Liebman (2023), cue-family SR/MA | A-W1X:2, A-W8:2, A-W1-PT:5 | Comparator C1 in the overlap matrix; its list chained (RL-NL) |
| Jeon et al. (2022), FRA in-vehicle auditory alerts review | A-W8:9, G-W8:1, K30:3/5 | List chained (RL-FRA); search method printed: Google Scholar, TRID, Scopus, agency interviews |
| Process-industry auditory alarm SLR | A-W8:3/7 | Not reachable (archive moved); chaining `failed` |
| Systematic review of auditory countermeasures for sleep inertia | A-W8:1 | Relevance to alerts to be judged in #6 |
| "A Review of the Literature on Alarms, Alerts, and Warnings" (ROSA P) | G-W1:2, G-W9:1 | Chaining candidate for #6 |
| "Visual and auditory symbols: A literature review" (ROSA P) | G-W1:6 | Chaining candidate for #6 |
| "Non-Speech Audio-Semiotics: A Review and Revision of Auditory Icon and Earcon Theory" (ICAD) | A-W1-FR:4 | **Overlap lead for N08** (semiotic classification of interface sounds) → #4 |
| "Design Framework for Audible Alarms: A Multidisciplinary and Integrated Approach" (IJDesign) | R-PSLR:4/6 | **Overlap lead for N06** (integrated alarm dimensions) → #4 |
| Hermann (2008), sonification taxonomy and definitions (ICAD) | I-W6:7 | Concept source for #4/#8 |
| Wickens et al. (2009), meta-analysis of off-nominal pilot performance | RL-FRA 109 | Chaining candidate |

**Primary reports both reviews cite** (RL-NL entry / RL-FRA entry): Graham 1999 (19/37), Haas 1998 (20/40), Jeon 2019 (24/50), Jeon & Sun 2014 (26/51), Jeon et al. 2015 (25/53), Jeon et al. 2012 (28/54), Landry et al. 2019 (30/61), McKeown 2005 (37/76), Nees et al. 2016 (44/86), Perry et al. 2007 (47/87), Vargas & Anderson 2003 (61/101), Walker et al. 2013 (64/103). These twelve need one publication record each, with both discovery paths kept.

**Further overlap leads from RL-FRA for #4** (titles only): urgency-mapping work by Hellier (2002, speech-warning urgency; 1999 psychophysical urgency mapping) and Baldwin (2011–2012, loudness × semantics, multimodal urgency coding); Marshall et al. (2007, annoyance and urgency); voice and social-response studies by Arrabito (2009, talker sex and voice style), Moran (2018, accent and gender bias), Dahlbäck et al. (2007) and Jonsson et al. (2013, personality matching). These bear on overlap rows N04 and N07, which are still `unknown`.

## 7. Possible duplicate publications

Flags only; §6.4 decides in #6 (a conference paper and its journal extension share a study unless the extension reports a new sample).

| # | Items | Evidence | Flag |
|---|---|---|---|
| D1 | Walker et al. 2006 ICAD "Spearcons: speech-based earcons improve navigation performance in auditory menus" / Walker et al. 2013 *Human Factors* "Spearcons (Speech-Based Earcons) Improve Navigation Performance in Advanced Auditory Menus" | A-W1:1, A-W1X:5, K64:3; RL-FRA 103–104; RL-NL 64 | Conference/journal pair |
| D2 | Jeon & Sun 2014 ICAD (Lyricons design) / Sun & Jeon 2015 (Lyricon identification) / "Lyricons: Designing a new auditory cue combining speech and sounds" | K26:1–4, K57:1–2; RL-NL 26, 57 | Nees & Liebman count two reports; sample overlap unknown |
| D3 | Garzonis et al. 2008 / 2009 / first author's thesis "Mobile service awareness via auditory notifications" | K16:4–5, K17:2; RL-NL 16, 17 | Thesis–article and article–article overlap |
| D4 | Jeon & Walker 2011 Spindex / earlier "'Spindex': Accelerated Initial Speech Sounds Improve Navigation Performance in Auditory Menus" | K27:5; RL-NL 27 | Precursor paper |
| D5 | Jeon et al. 2012 "Spindex Enhances Menus on Touch Screen Devices" / "… with Tapping, Wheeling, and Flicking" | K28:2–3; RL-NL 28 | Title variants: conference and extended version |
| D6 | Jeon et al. 2009 "Enhanced Auditory Menu Cues Improve Dual Task Performance…" / Moskovitch et al. 2010 "Enhanced auditory menu cues on a mobile phone improve time-shared performance…" | RL-FRA 52; K25:5; RL-NL 39 | Same group and paradigm |
| D7 | Gable et al. 2013 AutoUI / "Applying spindex auditory cues while driving and performing a secondary task" | K14:3; RL-NL 14 | Possible thesis or precursor |
| D8 | Landry et al. 2019 / "Subjective assessment of in-vehicle auditory warnings for rail grade crossings" / Landry et al. 2016 "Getting Active with Passive Crossings" | K30:1, K30:6, T-W8:1; RL-FRA 60–61 | Possible shared samples |
| D9 | Nadri et al. 2021 / ICAD 2021 "Investigating the effect of earcon and speech variables on hybrid auditory alerts at rail crossings" | K41:1, K41:8–9; RL-NL 41 | Conference/journal candidate |
| D10 | Nees & Best 2013 / 2014 (ICAD verification tasks) | RL-NL 42, 43 | Same paradigm; overlap unknown |
| D11 | Warnock et al. 2011 ICMI / 2013 CHI / Warnock 2014 PhD thesis | K65:3, K66:1/3; RL-NL 65, 66 | Thesis–article overlap |
| D12 | McGee-Lennon et al. 2011 "Name That Tune" / "Audio reminders in the home environment" (ICAD 2007) | K36:2/5, K68:6; RL-NL 36 | Same project |
| D13 | Palladino 2008: two repository records with the same title | K46:1–2 | Repository duplicate |
| D14 | Hofmann et al.: list year 2016; record key of the located result implies 2014 | K21:4; RL-NL 21 | Metadata conflict |
| D15 | Richie et al. 2018 / Kutchek & Jeon 2019 "Takeover and handover requests using non-speech auditory displays…" | K49:1–3; RL-FRA 59 | Same group; overlap unknown |
| D16 | Bonebright & Nees 2007 ICAD / 2009 *Applied Cognitive Psychology* | RL-NL 6, 7 | Same authors; low prior of shared sample |

## 8. Access is not an exclusion criterion

Nothing was excluded in R005. Paywalled, unreachable, untitled and non-English occurrences keep `unresolved` status with their access facts in the [ledger](../../searches/auditory/exports/ACCESS-LEDGER-R005-2026-10-13.csv). Two result types were deliberately not opened as access routes (a third-party proxy URL, document-sharing sites); that is an access decision, not an eligibility one. Under protocol §6.2–6.3, an item whose text cannot be obtained becomes `awaiting_text`, never `exclude`.

## 9. Unresolved gaps and stopping

The search stops here because every §5.1 channel now has a recorded outcome (§11), not because a number of papers was reached. Open gaps:

1. **Databases** (C1–C4, C6, C7): not searched. Owner action is already prepared in HG-R002-DATABASE-ACCESS; #17 must rerun executed channels and, if the gate is satisfied, run EQ1–EQ8.
2. **ICAD per-year coverage**: unknown for all years; a SMARTech collection listing was not reachable.
3. **Backward chaining** is complete only for RL-NL and RL-FRA. Chaining from included reports and from reviews confirmed in #6 remains; forward chaining needs C1.
4. **Voice/human-likeness and contrary evidence** (EQ3): web search returned little that is on-target.
5. **Non-English evidence**: only Korean items and one Chinese-language item surfaced; no regional databases (e.g., KCI, CNKI, J-STAGE) were searched.
6. **Update window 2021–2026** (N13): not separately searchable; recall unknown.
7. **Full texts and supplements**: none retrieved. The workspace cannot download and WebFetch returns paraphrase, so retrieval needs lawful files from the owner. Per protocol §6.3 and §13, the full-text request list follows title/abstract screening in #6, which will raise the source-access gate with a concrete list; the [known-item table](../../searches/auditory/exports/KNOWN-ITEM-CHECK-R005.csv) and hits already show where open repository copies appear.
8. **Reference-list fidelity**: RL-NL and RL-FRA entries are tool-rendered abbreviations; the last RL-NL entry is truncated. Each entry must be checked against a manifestation before it supports a decision.

Track E search completion as defined in protocol §11 also requires deduplication and resolved screening; those belong to #6.

## 10. Handoffs

| To | What |
|---|---|
| #6 screening and ledger | 1,271 occurrences (830 distinct URLs plus 183 reference entries) to deduplicate and screen; known-item table; duplicate flags D1–D16; review list in §6; the full-text request list and source-access gate |
| #4 related theory | Overlap leads for N04, N06, N07 and N08 (§6) |
| #9 extraction | No numeric extraction is possible from tool-mediated reading (protocol §10) |
| #17 refresh | Rerun C5, C8, C9 and C10 from 2026-10-04; run C1–C7 if HG-R002-DATABASE-ACCESS is satisfied; report the known-item check again as a recall benchmark |

## 11. Reproduction and limits

`python3 research/sources/auditory/scripts/build_r005_records.py` regenerates the records and the known-item table from the export; `python3 tools/validate.py --write-exports` then rebuilds the registry aggregates. The export was copied programmatically from the session's tool-call log. Four earlier hand transcriptions (K01–K24) were compared with it and matched exactly.

Limits: one agent did all the work, with no librarian (PRESS) review and no independent human check. Web results are unpaginated, US-region and possibly personalised; the engine's ranking and index dates are unknown. Known-item outcomes are the agent's title-level judgements. No source bytes are held.
