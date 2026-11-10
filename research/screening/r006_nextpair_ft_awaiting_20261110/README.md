# R006 — Edworthy 2014 / Arrabito 2004 full-text access dispositions

Refs #6. Frozen protocol v1 §§4, 6.2(3), 6.3, 6.4 and 10; baseline cutoff 2026-10-04 unchanged. **No empirical inclusion, full-paper reading, new hit, human second assessor or sample registration is claimed.**

## Canonical basis and boundary

| Source → prior canonical TA | Verified DOI and edition | Actually accessed 10 Nov 2026 | New FT decision |
|---|---|---|---|
| `SRC-R006-EDWORTHY-2014-LEARNING@1` → `SCR-R006-EDWORTHY-2014-LEARNING-TA@1` (include to FT) | `10.1016/j.apergo.2013.10.003`, *Applied Ergonomics* 45(5):1291–1296 (2014; 2013 online-first) | [Plymouth institution record](https://researchportal.plymouth.ac.uk/en/publications/learning-three-sets-of-alarms-for-the-same-medical-functions-a-pe/) **Abstract/citation** only; Elsevier full article not obtained (browser route disabled) | **awaiting_text** |
| `SRC-R006-F-ARRABITO-URGENCY@1` → `SCR-R006-ARRABITO-2004-URGENCY-TA@1` (include to FT) | `10.1080/0014013042000193282`, *Ergonomics* 47(8):821–840 (2004; publisher HTML posted 2007) | [PubMed PMID 15204277](https://pubmed.ncbi.nlm.nih.gov/15204277/) original-paper **Abstract**, [T&F publisher indexed abstract](https://www.tandfonline.com/doi/abs/10.1080/0014013042000193282); direct [full article](https://www.tandfonline.com/doi/full/10.1080/0014013042000193282) returned 403 | **awaiting_text** |

Original current source records were verified at exact revision 1 through DOI/Crossref provenance and remain `metadata_only`, `manifestations=[]`. Current access was public, uncredentialed and tool-mediated. The decision revision timestamps are *registrar* times, **not source HTTP receipt times**. No original article-body pages, audio, publisher PDF bytes, HTTP Date, file SHA-256, authorized retention, redistribution grant or human independent check were established. Distinct journal issue versus early-online publisher date does not create a second publication. Neither alarm-set condition nor rating population is an independent admitted sample.

R005 [Draft #148](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/148) documents related legal access attempts. R005 owns the original search receipts and source recovery; this R006 branch does **not** edit, adopt as canonical or overwrite that draft. If R005 or R004 subsequently obtains a lawful article manifestation, append a new R006 full-text screening revision grounded in actual reading, and resolve publication–experiment–sample identity without silently rewriting this access history.

## Measurable gate delta (relative to accepted main 60fb38423dc9e7438fcfbf03d622c2a5f46a948b)

| Metric | Accepted | Proposed after Integration serialization |
|---|---:|---:|
| TA stage decisions | 8 | 8 |
| FT exclusion | 1 | 1 |
| FT pending source/identity | 4 | 4 |
| FT awaiting original text | 1 | **3** |
| FT required but absent | 2 | **0** |
| FT included | 0 | **0** |
| Admitted empirical publications / studies / experiments / independent samples | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Selected Track E / G publications | 0 / 0 | 0 / 0 |

All eight current TA-scoped items will have an FT disposition if serialized, but **only one item is excluded**, four remain pending on source/identity and three await original text; there is no selected evidence map or permission to close #6. This closes a *missing-decision bookkeeping gap*, not the source-access or scientific-admission gap.

## Tests and Integration custody

The new issue-scoped unit tests use the real SRC/TA/FT source pins and in-memory negative controls: forbidden FT promotion without performed reading, wrong source revisions, TA exclusion, duplicate FT, cross-publication identity swaps, human-review conflation and future-version-safe historical assertions. Their isolated projection omits external R005/AID discovery basis solely for test-local graph construction, not from canonical records.

Integration alone regenerates `research/registry/generated/records-index.json` and `evidence-flow.json` and runs source-exact:
```sh
python -m unittest discover -s tests -v
python tools/validate.py --write-exports
python tools/validate.py --previous-ref <accepted-main-sha>
python -m tools.build_record_fixtures --check
git diff --check
```
A source-only Draft is expected to fail the full validator with stale exports, and is **not merge-qualified** until Integration's own branch has regenerated them, passed actual exact-head CI, obtained the required review and reverified merged-main push CI.

**External gate:** Lawful original Edworthy 2014 and Arrabito 2004 full article instances, with checked edition, actual acquisition/rights, exact bytes/hash/extent and Methods/Results readable by R006. A second human screener is not required by frozen §6.2; no independent human assessment occurred.

R007/R008 remain **not selected-corpus-ready**. The next genuinely suitable R006 source after this precise access checkpoint is R005's [Atyeo–Sanderson 2015 original publisher article](https://doi.org/10.1111/anae.13020), but it must be registered by its source owner and pass its own TA/FT/identity gates; R006 does not create false canonical SRC/HIT records from a draft.
