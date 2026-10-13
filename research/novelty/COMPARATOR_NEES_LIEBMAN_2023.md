# Nees–Liebman comparator: version, reading extent and overlap facts

[Novelty index](README.md) · [Overlap matrix](OVERLAP_MATRIX.md) · [Access ledger](../searches/pilot/exports/ACCESS-LEDGER-2026-10-13.csv) · [Protocol](../protocol/PROTOCOL-v1.md)

**Status: version-limited, tool-mediated reading of the author preprint.** The Version of Record (VoR) was not read. Everything below is a paraphrased reading record for the overlap audit, not an empirical extraction, not an inclusion decision and not a finding about audio alerts.

## Identity and version

| Item | Record |
|---|---|
| Published article (VoR) | Nees, M. A., & Liebman, E. (2023). *Auditory Icons, Earcons, Spearcons, and Speech: A Systematic Review and Meta-Analysis of Brief Audio Alerts in Human–Machine Interfaces.* Auditory Perception & Cognition, 6(3–4), 300–329. DOI `10.1080/25742442.2023.2219201`. Identity previously verified in the 1C1 packet and again on the Lafayette institutional record on 2026-10-13. |
| Version actually read | PsyArXiv preprint DOI `10.31234/osf.io/g68f5`, labelled "Preprint version 9.8.22", submitted for journal publication and not peer reviewed, 47 pages, data and syntax at the OSF project `cvk5h`. Read through an author-hosted copy on the co-author's academia.edu profile. |
| VoR routes attempted | Publisher abstract page: client error. Institutional PDF: robots exclusion (WebFetch) and session-proxy denial (shell). The preprint landing page could not be opened, so later preprint versions are unknown. See ledger rows 1–8. |
| Correspondence | Unknown. Peer review may have changed counts, analyses, wording and recommendations. Journal pages 300–329 are bibliographic locators only. Every fact below is bounded to the 9.8.22 preprint. |

## How it was read

Seven WebFetch calls on 2026-10-13 between 00:51 and 01:06 UTC passed the preprint text to the tool's intermediary model, which returned paraphrased answers to targeted questions about methods, counts, coding, analysis, results, discussion, limitations, introduction and the included-study list. Characters 0–100,000 of 102,096 were covered; the final 2,096 characters, at the end of the included-study list, were unreachable. No source bytes, hash, page images, figures or supplementary appendices were obtained. Page numbers below are the preprint page markers as reported by the tool and are approximate. The intermediary model can misreport; nothing here may be used as a numeric extraction or quotation without rereading a hashed manifestation.

## Scope and method as reported

| Topic | Preprint content (paraphrase) | Approx. locator |
|---|---|---|
| Aim | Compare auditory icons, earcons, spearcons, speech and an "other" category on accuracy, reaction time, subjective ratings, perceived workload and dual-task interference, to give heuristic recommendations for brief alerts. | pp. 2, 5–6 |
| Claimed gap | States that the body of evidence had not previously been formally synthesized; cites no earlier meta-analysis of these alert types. | p. 6 |
| Registration | No protocol registration is stated. Figure 1 is a PRISMA flow chart citing Page et al. (2021). | pp. 7–8 |
| Sources | ACM Guide to Computing Literature; Georgia Tech SMARTech ICAD proceedings; SAGE journals including HFES proceedings; Taylor & Francis Online; Web of Science Core Collection (named only in the figure note). Google Scholar informed database selection. | Fig. 1 note |
| Search terms and dates | The four alert-type terms in pairwise combinations; exact strings, fields and Boolean syntax not reported. Searches run in April and June 2021. Language, date limits, grey literature and citation chasing not reported. Included studies span 1993–2021. | pp. 7–8 |
| Eligibility | An independent variable with at least two levels among earcons, auditory icons, spearcons, speech (natural or synthetic) or another audio comparison, initially as labelled by study authors and refined by definition at full text. Longer data representations (auditory graphs, continuous or full-dataset sonification) excluded. Unclear or incomplete reporting excluded. | pp. 7–10, 28 |
| Screening | Both authors independently screened all records in Zotero (96.7% agreement, consensus discussion). One author read each full text; the other cross-checked extraction and coding. | pp. 7–10 |
| Flow | 4,010 identified; 1,736 after exact-duplicate removal; 118 full texts; 55 excluded at full text; 80 studies analysed (22 independent-groups, 58 repeated-measures); N = 2,713. The tool reported no reconciliation of 118 − 55 = 63 with 80; the likeliest explanation is a report/study unit difference, but this is unverified. | pp. 7–10 |
| Outcomes | Accuracy (% correct), reaction time (ms), subjective ratings (aesthetic preference, perceived usability and preference rescaled so higher is better), perceived workload, dual-task performance. Ratings with ambiguous polarity were excluded; **perceived urgency** is the example given. | pp. 9–10 |
| Other coding | Design, population (mostly students), system domain, task type, dual-task status. Training, practice and the semantic content of messages are not described as coded variables. No formal risk-of-bias tool. | pp. 9–10 |
| Effect size | Hedges' g with independent and repeated-measures formulas; RT and workload signs reversed. | pp. 12–15, App. A |
| Missing data | SDs missing for 42% of means and imputed (method not in main text). | pp. 12–15 |
| Dependence | Repeated-measures correlation assumed r = .70 for all studies, based on the first author's earlier studies. Handling of several comparisons from one study is not described in the main text. | pp. 12–15 |
| Models | Unweighted random-effects (SPSS), weighted random effects (R `meta`), network meta-analysis (R `netmeta`) with treatment rankings; some studies dropped from NMA for negative variance estimates; direct–indirect inconsistency noted for RT and workload. | pp. 12–18, App. B–C |
| Per-outcome k | Accuracy k = 43; RT k = 50; subjective ratings k = 36; workload k = 13; dual-task k = 11 (with N and comparison counts reported). | pp. 15–18 |

## Reported conclusions and limitations

The preprint concludes that speech, spearcons and "other" (typically hybrid) alerts appear preferable to auditory icons, and icons preferable to earcons, for accuracy, speed and subjective ratings, while workload and dual-task evidence is inconclusive and moderators could qualify the recommendation. Its stated limitations are incomplete reporting, imputed SDs, the assumed correlation, high heterogeneity with wide prediction intervals, publication/reporting bias, and 15 studies with unusable nonsignificant results. Future directions call for moderator analyses and for separating aesthetic preference from perceived usability.

These are the authors' claims in an unreviewed version. MHAC does not adopt them as findings. Exposure to them before the MHAC freeze is disclosed in the [pilot report](../protocol/PILOT_REPORT.md#prior-exposure).

## Topics not found in the tool-mediated reading

The tool reported no substantive treatment of: training dose or retention over time; urgency (beyond excluding urgency ratings); message certainty or uncertainty as content; hazard, severity or consequence; correct task action as distinct from identification; human likeness, anthropomorphism or attributed emotion; and a formal semiotic framework. **This is "not found in a tool-mediated preprint reading", not "absent from the review".** The VoR, figures and supplements may differ.

## Included-study list as a known-item set

The tool listed 68 entries of the "References Used in Meta-analyses" section, alphabetical from Acker-Mills (2006) to Wolters et al. (2012), with outcome tags a–e; the final entry was truncated and later entries, if any, were unreachable. The list is retained only in this repository's working memory for the pilot recall check and for R005 backward chaining. It is **not** committed as a bibliography because titles and identifiers came through the intermediary model and are unverified. R005 must re-derive the list from an actual manifestation or verify each item independently.

## What this comparator supports

The overlap risk identified in 1C1 is now concrete: a broad cue-family comparison of identification accuracy, response time, preference, workload and dual-task cost across auditory icons, earcons, spearcons and speech already exists with searches to mid-2021. A further MHAC ranking of those families on those outcomes would be at most an update. The [overlap matrix](OVERLAP_MATRIX.md) records which MHAC questions this does and does not appear to address, with these limits carried forward.
