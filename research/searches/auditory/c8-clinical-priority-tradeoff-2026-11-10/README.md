# R005 C8: clinical alarm priority and pleasantness trade-off — 10 November 2026

[Issue #5](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/5) · [Source observation ledger](OBSERVATIONS.json) · [Frozen protocol §5](../../../protocol/PROTOCOL-v1.md#5-track-e-sources-and-searches)

## Purpose and selection of feasible work

The highest-value unfilled systematic retrieval is C1/EQ1. Its retained, date-sorted **4,200 of 9,368** items are a prefix, not a random sample, and the available URL-opening interface again rejected an OpenAlex probe before returning an HTTP response. It revealed **neither** quota availability **nor** a new production result. This pass therefore pursued a different permitted route: targeted C8 primary-source navigation on a clinically consequential contrary case, checked against a separate current laboratory article. This is an additive supplement, **not** C1/C6 search completion, a formal systematic C9 review chain, or a substitute for the missing EQ1 items.

Both identified articles precede the frozen **2026-10-04** publication cutoff. They are navigational candidates, not new independently verified search hits or included studies. The GitHub code search did not find Hunn's DOI or author name in indexed repository text, but the compressed OpenAlex inventory was **not** exhaustively examined, so absence of prior hits is **not** established.

Exact indexed queries, source links, locators, reading limits and a truthful no-response API probe are in [OBSERVATIONS.json](OBSERVATIONS.json). The query interface does not expose a lossless ordered search-result export, source HTTP bytes or per-request timestamps. No source-file SHA-256, original PDF, supplemental sound, or figure-image verification was obtained.

## Two distinct designs; no pooled result

| Source and reading extent | Design and key boundary | R006/R009 consequence |
|---|---|---|
| [Hunn et al. (2025)](https://doi.org/10.3390/healthcare13233033), *Healthcare* 13(23):3033; [public article HTML](https://pmc.ncbi.nlm.nih.gov/articles/PMC12692177/) | Single-centre clinical implementation; **same** clinicians tested before and after; web-rendered Methods §§2.1–2.8, Results §§3.1–3.6, Discussion and Conclusions consulted | Do **not** interpret phases as independent participants, preference as comprehension, or controlled test outcomes as clinical safety events |
| [Shin et al. (2025)](https://doi.org/10.1016/j.bjao.2025.100379), *BJA Open* 14:100379; [PubMed record](https://pubmed.ncbi.nlm.nih.gov/40161967/) | Laboratory design comparing conventional and acoustically altered 'pointer' signals; PubMed abstract and **only selected** indexed PMC excerpts consulted, not the full article | Cannot be described as a direct replication or matched comparator to Hunn; prior-paper/sample connections unverified |

### Observed trade-off in a real implementation

Hunn et al. describe a redesign of medical monitor alarms to be less harsh, rolled out in April 2024. **Ninety** clinicians participated before implementation and **77 of those same people** returned later. In Methods **§2.5** and Results **§§3.1–3.4**, recognition was tested on a laptop in a controlled setting with simulated operating-room noise, **not while making actual clinical responses**. There was no formal speaker sound-pressure-level or frequency-response calibration.

The authors report a mean **+0.51** improvement in sound-appeal rating (95% CI 0.37–0.64) and **−0.15** in perceived functionality (95% CI −0.27 to −0.03). For all-priority recognition, the rate ratio is **0.93** (95% CI 0.83–1.04): the interval includes no difference. Disaggregated recognition changes direction by alarm priority:

| Priority | Before / 231 sound trials | After / 231 sound trials | Interpretation at this level |
|---|---:|---:|---|
| Low | 220 correctly classified (95.2%) | 202 (87.5%) | Lower recognition of refined alarms |
| Medium | 187 (81.1%) | 143 (62.0%) | Markedly lower recognition of refined alarms |
| High | 188 (81.4%) | 205 (89.0%) | Higher recognition of refined alarms |

**231 is three sounds per priority × 77 participants, not 231 people.** The paper reports mixed logistic contrasts in Results **§3.4**, but these here are transcribed descriptive results, **not** verified estimates from a hashed source or accepted R009 extraction. Results **§3.6** further report 55/77 preferring refined alarms; that preference does not establish safe or accurate interpretation. The sound-appeal scale has relatively low author-reported internal consistency (omega 0.489, **§3.2**).

A major limitation is temporal confounding: old sounds were presented before the implementation, new sounds after months of exposure and possible training, with no concurrent randomized old/new allocation. Training attendance was reported by 34/77. The study's own Discussion acknowledges time trends, selection/attrition, single-centre transport and controlled recognition-test limitations. Neither a causal sound-quality mechanism nor real-world patient benefit can be inferred from this design alone.

### Separate laboratory pointer result

Shin et al. (2025), *PubMed abstract*, report **26 clinician and 19 non-clinician participants**, with higher mean alarm identification accuracy for a modified pointer than a conventional pointer (**0.90 vs 0.80**). This is a distinct manipulated cue, task and setting. Search-indexed article text suggests a **smaller response-time-analysis subset** (22 clinicians, 16 non-clinicians), but this has not been checked against a full source copy; it is a *verification prompt*, not a qualified extracted result.

The point is **not** that one study refutes the other. Together they warn that greater pleasantness, better detection, alarm-priority discrimination and overall action safety are different constructs. They provide an adverse case to simplistic "less harsh always better" as well as "maximal salience always better" design preferences. Neither evaluates whether an allegedly emotion-free machine voice communicates meaning more effectively.

## Source integrity and frozen gates

This was **AI-assisted web/publisher text reading**, with no independent human research review. Hunn's article was read in selected continuous HTML sections, including numeric HTML table text; its figures, supplemental audio, original PDF bytes and raw data were not image/file verified. Shin was consulted through PubMed abstract and search-indexed excerpts; publisher full text returned a web-interface HTTP 403. No full-text claim is made for that second source.

Formal **C9** backward chaining is owed for R006-included studies and each relevant EQ8 review. Neither paper is currently R006-selected, so references encountered here are preparatory C8 navigation only. No eligibility exclusion, full-text-screening decision, independent sample count, quantitative meta-analysis, or human verification is recorded.

Historic R005 **150 search records / 21,483 occurrences** and the old 69-item **38 located / 10 possible / 21 not located** benchmark remain dated, unchanged checkpoints; no new database record, search-hit or canonical source was appended. There are still seven complete OpenAlex family runs and an incomplete EQ1, missing ACM/IEEE/publisher/subscription exports, ICAD venue gaps and unfinished review/included-report chains. The baseline search cutoff remains **4 October 2026**.

## Reproduction and next actions

From a normal cloned repository:

```sh
python -m unittest discover -s tests -p 'test_r005_c8_clinical_priority_tradeoff.py' -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The tests reject semantic promotions (fake human verification, invented source hashes, duplicate sample inflation, false C1/C9 success, invalid trial denominators, cutoff drift and unearned extraction). They do **not** check the scientific accuracy of the published estimates.

**R006:** check both DOIs against all retained occurrences and predecessor publications, reconcile Hunn 90→77 repeated measurements and Shin study/sample identity, then screen as appropriate under E1–E6. **R009, if selected:** obtain exact primary manifestations, inspect figures/supplements and acoustic designs, reconcile statistical analysis and threats to validity. **Integration:** decide whether to reflect this dated limited C8 note in the shared coverage index; do not change canonical totals.

**Next R005 priority:** continue immutable EQ1 pages from the exact original sorted checkpoint once a raw-response-authorized API is available; otherwise advance an **actual complete source-bound EQ8 reference chain** or unresolved ICAD year. No researcher or owner access action is assumed, and **issue #5 remains open**. This shard is **Refs #5**.
