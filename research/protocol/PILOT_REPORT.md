# Pilot, exposure and access report — MHAC-R002

[Protocol](PROTOCOL-v1.md) · [Pilot search log](../searches/pilot/README.md) · [Raw search export](../searches/pilot/exports/PILOT-WEBSEARCH-2026-10-13.json) · [Access ledger](../searches/pilot/exports/ACCESS-LEDGER-2026-10-13.csv) · [Concept register](CONCEPT_REGISTER.md)

**Clearly labelled pilot.** Nothing here is a production search, an inclusion decision, an extracted result or a finding. The pilot ran on 2026-10-13 between 00:50 and 01:20 UTC in one claude.ai cloud session.

## Contents

| § | Section | One-line summary |
|---|---|---|
| 1 | [Who ran it and with what](#1-who-ran-it-and-with-what) | Actor, tools and their limits. |
| 2 | [Prior exposure](#prior-exposure) | What was known before the rules were frozen, and the mitigations. |
| 3 | [Pilot searches](#3-pilot-searches) | 31 web-search runs in four labelled batches. |
| 4 | [Known-item recall check](#4-known-item-recall-check) | How few known eligible reports the only reachable channel returned. |
| 5 | [Query revisions and the C8 query set](#query-revisions-and-the-c8-query-set) | What changed and why; the frozen W1–W9 strings. |
| 6 | [Eligibility calibration](#eligibility-calibration) | Sixteen heterogeneous and negative cases run through E1–E6. |
| 7 | [Extraction calibration](#7-extraction-calibration) | What tool-mediated reading can and cannot supply. |
| 8 | [Concept revisions](#8-concept-revisions) | Pre-freeze revisions logged in the concept register. |
| 9 | [Access gaps](#access-gaps) | Every channel or source that could not be reached. |
| 10 | [Unresolved after the pilot](#10-unresolved-after-the-pilot) | What the freeze does not settle. |

## 1. Who ran it and with what

| Item | Record |
|---|---|
| Actor | Claude (Anthropic), executing agent in a claude.ai cloud session; model reported by the session as Claude Opus 5.5. No human took part in any pilot decision. |
| Search tool | WebSearch: general web search engine, US-only, up to about ten titles and URLs per call, no counts, no abstracts, no pagination. |
| Reading tool | WebFetch: fetches a URL found in search results and returns an **unidentified intermediary model's paraphrase**; verbatim quotation is restricted; no bytes are returned. URLs not surfaced by a search require an owner permission prompt, which went unanswered. |
| Workspace network | Shell access limited to package registries and GitHub. All publisher, repository and bibliographic-API hosts were refused by the session proxy. |
| Owner's linked computer | The desktop app's built-in browser refused `api.openalex.org` and `mdpi.com` under the owner's site permissions. No access request was pursued and no other browser was used as a workaround. |

## Prior exposure

Before this freeze the executing agent had read, and the rules may therefore reflect:

- the project's stated direction (README, AGENTS, research integrity, project foundations) favouring intelligible, perceptually non-human audio without performed emotion;
- the seed reading list and the archived R001, R002 1A/1B/1C1 and quantitative prepasses, including their candidate questions;
- **the Nees–Liebman preprint's methods, results, rankings and conclusions** (speech, spearcons and hybrids ahead of icons, icons ahead of earcons, for accuracy, speed and preference; inconclusive workload and dual-task evidence);
- the titles returned by 31 web searches;
- tool-mediated summaries of Vriend et al. (2025) results, Brier (2010, 2015) argument structure and the abstracts of Nam (2010), Thomsen & Brier (2014), Cobley (2010) and Valente, de Souza & Feijó (2009);
- the methodological guidance listed in [reporting applicability](REPORTING_APPLICABILITY.md).

Earlier project conversations that preceded the repository were not available to this agent; their content is known only through the repository's own summaries.

**Mitigations built into v1:** no rule refers to the relative performance of any cue family; the project preference is excluded from eligibility and weighting; the evidence map is organised by semantics and outcome, not by the families Nees–Liebman ranked; synthesis cells are fixed from study characteristics before effects are extracted (analysis plan §3); outcome families and pooling rules are frozen now; negative-case searches are mandatory (protocol §7.3). These reduce but do not remove the risk that exposure shaped the questions.

## 3. Pilot searches

All runs are in the [raw export](../searches/pilot/exports/PILOT-WEBSEARCH-2026-10-13.json) with returned titles and URLs exactly as received. Search-run records are in [`research/searches/pilot/records/`](../searches/pilot/records/).

| Batch | Runs | Purpose | Window (UTC) |
|---|---|---|---|
| N | N1–N4 | Locate a readable Nees–Liebman version | 00:50:16–01:06:04 |
| M | M1–M6 | Locate methodological guidance deferred by 1B | 01:06:04–01:14:08 |
| P1 | P-B1–P-B4, P-R1–P-R4, P-A1–P-A9, P-A1X | Lane pilots: Brier (4), related theory (4), auditory (10) | 01:14:08–01:14:31 |
| P2 | P-R5, P-R6, P-B5 | Follow-ups for the overlap audit | 01:14:31–01:17:51 |

Window bounds are shell-clock readings around each batch, not per-query times.

## 4. Known-item recall check

The comparator's included-study list (68 entries visible through tool-mediated reading; identities unverified) served as a known-item set. Across the ten auditory-lane runs (about 95 result slots), five distinct known items appeared, all unverified title-level matches:

| Known item (as listed via the tool) | Returned by |
|---|---|
| Graham (1999), auditory icons as emergency warnings in a vehicle collision-avoidance application | P-A7 (three URLs), P-A8 |
| Perry et al. (2007), icons versus abstract warnings ("Cough once for danger") | P-A5 |
| Garzonis et al. (2009), auditory icon and earcon mobile service notifications | P-A5 |
| McGee-Lennon et al. (2011), musicons as reminders (probable match to a CHI 2011 PDF) | P-A5 |
| Tislar et al. (2018), learnability of music, earcons, spearcons and lyricons | P-A1X |

That is about 7% of the visible known set. The Walker et al. (2013) spearcon article also appeared, but only in comparator-access run N3. Conversely, Dingler et al. (2008), an ICAD paper comparing all four cue families on learnability, appeared in P-A1, P-A5 and P-A1X but is **not** in the comparator's visible included list; why is unknown (eligibility difference, coverage, or tool error).

**Interpretation.** Top-ten web search is a discovery aid, not a retrieval channel for systematic work. This result, not a preference, is why protocol §5 requires bibliographic databases (gated) and backward chaining, and why the fallback in §5.3 forces a coverage-limited claim.

## Query revisions and the C8 query set

| Pilot observation | Revision |
|---|---|
| P-B4 found no cybersemiotic treatment of interface sound; it surfaced a Peircean analysis of PC sounds and modes-of-listening work. | Added Track G tier T5 (semiotics of auditory display) with its own sampling; recorded as overlap leads N08/N10. |
| P-A2 (urgency) returned mostly tactile-urgency items. | EQ2 requires an audio block; tactile-only studies are an explicit negative case (`E-NOT-AUDIO`). |
| P-A3 and P-A9 (voice, emotion) returned HRI trust studies, emotional TTS work and a patent. | EQ3 requires both a warning/alert block and a human-likeness/affect block; patents are `E-NOT-PRIMARY`. |
| P-A7 (null-oriented phrasing) returned two Korean ship-bridge alarm studies and Graham (1999). | A null-oriented web query (W9) is kept as a negative-case probe; non-English translations added to C8. |
| P-A8 (German) returned mostly English items. | Non-English web discovery is kept but its yield is recorded and no coverage is claimed from it. |
| P-A1 standard vs P-A1X extended: extended returned more scholarly PDFs and repository records. | W1 runs in both modes. |
| P-R3 (grounding) returned LLM-dialogue items rather than primary grounding theory. | Track G samples grounding through citation chains from primary sources, not web search. |
| P-B5 surfaced cybersemiotic communication theory (Thomsen & Brier 2014; a USP article). | Added to T4/T5 reception leads for #4; recorded as N10 evidence. |

**Frozen C8 English strings (W1–W9):**

```text
W1 earcons auditory icons spearcons speech comparison experiment
W2 auditory warning perceived urgency mapping experiment
W3 voice warning synthetic speech human-likeness trust experiment
W4 sonification uncertainty listeners experiment
W5 auditory alerts learning retention training experiment
W6 sonification patient monitoring anesthesia experiment
W7 auditory notification interruption dual task workload experiment
W8 systematic review auditory alarms warnings auditory displays
W9 auditory alerts no significant difference speech nonspeech
```

## Eligibility calibration

Sixteen heterogeneous pilot items were run through E1–E6 using only the information actually available (title, abstract or tool-mediated text). These are calibration examples, not screening decisions.

| # | Item | Information | Pilot decision | What it calibrated |
|---|---|---|---|---|
| 1 | Nees & Liebman (2023) review | Tool-mediated preprint | `E-NOT-PRIMARY`; chaining source | Reviews feed discovery only |
| 2 | Vriend, Hägele & Weiskopf (2025), audiovisual uncertainty mappings | Tool-mediated text | Include | Multimodal clause of E2; O10 certainty interpretation and O12 preference; crowd-sourced sample |
| 3 | Dingler et al. (2008), learnability of four cue types (ICAD) | Title | Include at title stage | CT1 with O5 training; absent from comparator list |
| 4 | "The impact of different types of auditory warnings on working memory" (Frontiers in Psychology, 2022) | Title | Include at title stage | Led to the O6/O8 memory-outcome mapping rule; post-2021 update window |
| 5 | Time-compressed speech for monitoring vital signs | Title | `uncertain` | MED task class; comparison not visible in title |
| 6 | Graham (1999), auditory icons in collision avoidance | Title | Include at title stage | VEH; CT1 |
| 7 | Urgency mapping with psychophysical techniques (Plymouth record) | Title | Include at title stage | CT2 within-family parameter manipulation; O9 mapping fidelity (excluded by the comparator) |
| 8 | Tactile warning design based on perceived urgency (Waterloo thesis) | Title | `E-NOT-AUDIO` | Negative case for E2 |
| 9 | Voice and repair strategy effects on trust in HRI | Title | `uncertain` | Conversational robot speech may qualify under G01; CT3; O12 trust |
| 10 | "Emotive advisory system and method" (US patent) | Title | `E-NOT-PRIMARY` | Patents and system descriptions |
| 11 | "Design guidelines for the use of audio cues in computer interfaces" (TRID) | Title | `uncertain` | Guidance documents may contain experiments; never excluded on title alone |
| 12 | KRISO study of alarm-sound types on response speed and accuracy on a ship bridge (Korean) | Title | Include at title stage | Non-English inclusion; translation required at full text |
| 13 | "Sounds Uncertain" (arXiv 2608.18680) | Title; no text layer | `awaiting_text` at full text | Access is not exclusion |
| 14 | Nam (2010), semiotic analysis of PC sounds | Abstract | `uncertain` (possible empirical component); Track G T5 regardless | Dual-track items |
| 15 | "Grounding in multi-modal task-oriented collaboration" | Title | `E-NOT-MACHINE-MESSAGE`; Track G candidate | Human–human communication |
| 16 | WSCoach: wearable real-time auditory feedback | Title | `uncertain` | System feedback about the user's own behaviour may qualify under G01 |

Calibration outcomes adopted into v1: the `E-NOT-AUDIO` reason code; the multimodal clause; the explicit place of within-family parameter manipulation (CT2); conversational machine speech judged under G01 at full text; and the O2/O6/O8 memory mapping rule.

## 7. Extraction calibration

Pass-1 characteristic fields were attempted for item 2 (Vriend et al. 2025) and the review-level fields for item 1.

| Field group | Item 2 via tool-mediated reading | Consequence |
|---|---|---|
| Identity, design, population | Obtainable: two experiments, N = 170 and 185 after exclusions from 217 recruited (crowd platform), 48 trials each, factor structure | Pass 1 is feasible from tool-mediated reading for screening and cell assignment, labelled as such |
| Stimuli and mapping | Obtainable in outline (loudness, tempo, pitch; 3 s sine tones; four visual channels) | Sufficient for coding CT2 and O10 |
| Effect estimates | Only polarity agreement proportions and test outcomes as paraphrased; no locator-verifiable values | **Numeric pass-2 extraction is blocked** without a hashed manifestation (protocol §10) |
| Overlap of the two experiments | 217 recruited in total; whether the same people contributed to both experiments is unclear from the tool-mediated reading | Identity rule: `unknown` overlap, treated as one component until resolved |

For item 1, review-level fields (sources, dates, eligibility, counts, models) were obtainable, but the included-study list's identifiers were not verifiable, so R005 must re-derive it.

## 8. Concept revisions

Nine pre-freeze revisions are logged in the [concept register](CONCEPT_REGISTER.md#pre-freeze-revisions): urgency split; identification versus action; three senses of certainty; sign relations as use-dependent; sonification scope; memory-outcome mapping; human likeness versus attributed emotion versus listener affect; and two Track G sensitizing concepts (Luhmannian communication; senses of information). Six of them changed Track E rules before the freeze; none occurred after it.

## Access gaps

| Gap | Attempts (ledger rows) | Impact | Handling |
|---|---|---|---|
| Nees–Liebman VoR | Publisher client error; institutional PDF robots exclusion and proxy denial (1–5) | Comparator facts bounded to preprint 9.8.22 | Version limit carried forward; not gated |
| PsyArXiv landing page and later versions | Permission prompt unanswered (8) | Later preprint versions unknown | Limitation |
| Bibliographic APIs (OpenAlex, Crossref, arXiv export, Semantic Scholar) | Proxy denial (9); owner browser site permissions (10) | No executable database search in the pilot or, without change, in R005 | `HG-R002-DATABASE-ACCESS`; fallback §5.3 |
| Subscription databases (Web of Science, Scopus, PsycINFO, ACM DL, IEEE Xplore search) | Not attempted: no lawful access available to the agent | Coverage limits | Owner exports optional under the same gate |
| Source bytes for any web text | Proxy denial; owner browser site permissions (2, 11) | No hashed manifestations; no locator-bound extraction | Separate full-text gate to be raised by #3/#5 with an exact list |
| Specific overlap comparators | Abstract-only or redirect (20, 21, 23–27) | Bounded cells in the overlap matrix | Re-audit after R004/R005 |

## 10. Unresolved after the pilot

The freeze does not settle: whether any bibliographic database will be available for R005; whether lawful PDFs can be obtained for locator-bound extraction; the content of de Souza's core chapters and of urgency-mapping and voice-anthropomorphism reviews (overlap cells N04, N07, N09); Brier's edition history; and whether any human will screen or check anything. Each is either a recorded gate or a limitation that downstream claims must carry.
