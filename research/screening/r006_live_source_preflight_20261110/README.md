# R006 live canonical admission/source-manifest preflight — 10 November 2026

**Refs #6. Source- and issue-scoped engineering qualification, not a new screening decision.** This tranche replaces the unsafe practice of reading the original 4-TA/0-FT *dated* source audit as if its counters reflected today's accepted registry. It does not modify R004 source records, R005 searches, canonical records, frozen protocol, generated exports, or other workers' branches. The source of truth is the current accepted main plus the canonical records loaded by `audit.py`; the full validator remains authoritative.

## Live measurable gate (base main `94c4a9d224e5667e57758810adea372176d58396`)

| Exact source | Canonical TA | Canonical FT | Verified next admission dependency |
|---|---|---|---|
| Becker et al. 2025, DOI `10.1145/3706066`, ACM THRI 14(2), Art. 29 | include to FT | **no FT record** | R004-owned `SRC-REL-BECKER-2025@1` contains **zero** PDF manifestations. Original author-hosted publisher-layout PDF is readable, but the original bytes/SHA-256 were not obtained in this pass. Source owner/Integration must register an actually hashed version/revision before a performed reading AID and canonical FT inclusion. Main Battleship advice phase E2=yes is *provisional*, not a registered sample. |
| Romeo et al. 2025, DOI `10.1145/3711938`, ACM THRI 14(2), Art. 33 | include to FT | **no FT record** | R004-owned `SRC-REL-ROMEO-2025@1` contains **zero** PDF manifestations. Chalmers-hosted published-layout PDF is now accessible by a *second* institutional route (accepted R005 #120), but remains unhashed. Registrar must distinguish the 2025 online video pilot from the physical spoken navigation experiment; 2023 stimulus/sample overlap remains unknown. |
| Kühne et al. 2020, DOI `10.3389/fnbot.2020.593732` | uncertain | **exclude** (E2) | Canonical `FRONTIERS-PDF` manifestation, source-located AID and FT exclusion landed in #114. No new source/decision or human assessment needed merely to rerun the gate. |
| Romeo et al. 2023, DOI `10.1109/RO-MAN57019.2023.10309631` | uncertain | **awaiting_text** | Original IEEE full text and versioned Zenodo scripts inaccessible/unverified. No E2 or participant-overlap verdict; no denial solely for access. |

**Generated accepted-main snapshot:** 4 canonical TA decisions (2 include-to-FT, 2 uncertain); 2 canonical FT dispositions (1 exclusion, 1 `awaiting_text`); 2 FT decisions absent; 0 FT inclusions; 0 STUDY, EXP, SAMPLE or selected Track E/G corpus. Prepared noncanonical opinions are not eligible records.

## Actual primary-source checks in this pass

- [Becker 2025, Hamburg author-hosted public article](https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf): title/DOI/header at PDF page index 0, original published Methods §§3.3–3.7 and Appendix E; *rendered* PDF index 7 = printed 29:8 and PDF index 23 = 29:24. The latter explicitly shows operational status/advice utterances with gesture and facial expression. Printed 29:8 shows repeated advice, measured responses and the author-reported pre-study/main participant separation. It is not proof of independently verified participants or a pure audio-only effect.
- [Romeo 2025, Chalmers University publicly hosted published-layout PDF](https://research.chalmers.se/publication/546010/file/546010_Fulltext.pdf): 23 PDF pages (cover + 22 article pages); PDF index 5 = printed 33:5 (§2.1 pilot) and index 8 = 33:8 (§2.2 main recruitment, §2.3 voice). Those page images independently corroborate the online video repair-rating pilot and physical maze recommendation task as distinct *procedures*, not independent admitted samples. Main report also describes subtitle/headphone, other visual information and Wizard-of-Oz controls; prospective extraction must capture these multimodal factors. Do not claim the Chalmers file equals the previously attempted Heriot-Watt PDF byte-for-byte.
- The original URLs were accessed via a web PDF text and page-image tool on **2026-11-10**, with a publicly accessible institutional/author route and article-header CC declarations (Becker CC BY 4.0; Romeo CC BY-NC-SA 4.0). Tool-visible document headers are evidence of the declared version and licence, not permission to invent source-byte hashes. No independently saved PDF bytes, file SHA-256 or exact HTTP-receipt timestamps were obtained. No audio/video was heard/watched and no complete-paper reading or human assessor is claimed.

Source credentials required for the next canonical step are **actual original file SHA-256, extent and coordinate**, plus an R004-owned source *revision* that records the manifestation. The frozen `schemas/v1.py` requires these fields for a legitimate source manifestation; `tools/record_graph.py` refuses FT `include`/`exclude` without a performed AID that points to such a registered manifestation. A hash guessed from metadata or from a separately hosted file is invalid.

## What the executable audit establishes

`audit.py` follows the **current** canonical source, TA, FT and reading records in the checkout, verifies verified DOI/source identity, correct decision actor IDs/timestamps and the immutable PR #109 first-pass agent registration (`gpt6-r006-integration-registrar-20261110`, `2026-11-10T08:11:16Z`), while permitting separately dated later revisions, checks that an FT decision's reading AID has a real matching source manifestation and bounded page ranges, and rejects discrepancy with the generated empirical evidence flow. It correctly allows an older TA pin after a later source revision: historical decisions must not be rewritten. It compares all four source-specific statuses against the generated `screening_coverage.decision_scopes`, with global screening totals checked only for undercount. Additional legitimately admitted sources, later FT decisions and nonzero STUDY/EXP/SAMPLE counts **must not fail this dated four-source preflight**. Global arithmetic, admission eligibility and sample independence are enforced separately by the full repository graph/history validator; this scoped audit never certifies them.

Tests cover DOI/TA drift, false FT inclusion without reading, nonexistent manifestations, out-of-bounds reading ranges, missing attribution, attempted human-registrar impersonation/timestamp rewriting, per-source stale exports, invalid counters, historical TA pin validity and **synthetic forward transitions** (existing registered reading AID and hypothetical included FT plus nonzero global counts). The positive FT counterfactual deliberately alters a historical exclusion only inside a test fixture: it is not a real Kühne eligibility reversal, no new sample is demonstrated, and full `tools/validate.py` remains mandatory. **It does not reproduce scientific correctness, independence or original source hashes.** The common repository validator, fixture checks and history checks are separately required for admission/merge.

```sh
python research/screening/r006_live_source_preflight_20261110/audit.py
python -m unittest tests.test_r006_live_source_preflight_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

## Narrow Integration/R006 handoff

**Integration review repair (10 Nov 2026):** [review on PR #121](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/121#pullrequestreview-5840788758) correctly found that the original permanent test forced exactly two FT decisions and zero included studies. This revised implementation uses the four-source scoped generated flow and never treats the historical zero-admission snapshot as an eternal invariant. Revalidate the *new* final PR head before merge; earlier green #42800165712 applied to the uncorrected head.

1. **R004 source authority + Integration:** lawfully retrieve each exact original Becker/Hamburg and Romeo/Chalmers PDF in a trusted checkout, calculate SHA-256 from the *obtained* bytes and actual PDF page extent/offset, and append versioned source manifestations to the two R004-owned `SRC` records. The current worker cannot read file bytes from the PDF-rendering interface and must not forge hashes or edit R004 paths. R005 [PR #120](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/120) is already merged on main `7fdf1c718270691f8991a82d1a1124df7112c888` with independently reviewed selected Methods pages and verified [merged-main CI](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42803919647). Its rendered pages do not establish a reproducible original file hash.
2. **R006 alone:** using the resulting exact source revisions, perform truthfully dated, source-pinned AID readings and independent-by-time **AI** source rechecks as required, adjudicate E1–E6 for each 2025 publication and its distinct procedures; document confidence and unknown study/sample overlap; register canonical FT SCR only when qualified. The frozen protocol does **not mandate a human second screener**. R006 never interprets separate online/main procedures as two independent samples by default.
3. **Integration alone:** serialize the canonical changes and the full records index/evidence-flow rebuild, run history/full suite/fixture validator on exact final head and merged main, guarded merge with reviewer and CI evidence. Do not merge this issue-scoped preliminary engineering PR merely as a substitute for source eligibility.
4. **Downstream:** R007/R008 have no selected Track G corpus; neither R005 #5 nor R006 #6 is accepted. Maintain Draft/HOLD on scientific acceptance until source and corpus gates are genuinely met.

No recruitment, purchases, external contact, reviewer impersonation, new effect extraction, or protocol amendment.

## Historical FT decision provenance and event ordering — 10 November 2026

Additional source-scoped safeguards preserve the **real initial AI actors and
timestamps** of the Kühne 2020 full-text E2 exclusion and Romeo 2023
`awaiting_text` decision, plus Kühne's accepted source-located reading AID.
A full-text `include`/`exclude` must cite a known performed reading event
whose timestamp **and registered revision** are not later than the actual
screening decision. RFC3339 times are compared as offset-aware instants,
not strings. Six negative tests exercise a later appended reading revision,
an impossibly late reading event, an unknown event time, and three attempts
to relabel historical AI screeners/readers as humans.

The checks target preserved first revisions without freezing legitimate later
append-only source, reading or screening changes. They do not claim scientific
agreement between agents or verify new source bytes. The common repository
graph/history validator and deterministic export checks remain mandatory;
this preflight cannot admit new studies or independent samples.

**Current admission status remains unchanged:** four previously accepted
title/abstract decisions, one full-text exclusion, one full-text access
checkpoint, two lacking a full-text decision, zero full-text inclusions,
zero admitted studies/experiments/samples and zero selected Track E/G corpus.
[R005 #124](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/124)
qualifies the original four-page Romeo 2023 *supplement*, **not** the missing
six-page original IEEE report; do not alter Romeo 2023 `awaiting_text`.
The diagnostic [R004/Integration original-file receipt](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/6#issuecomment-6766953989)
identifies recovered but **ephemeral** Becker 2025 bytes and a mutable Romeo
2025 PDF wrapper. R004/Integration must register lawfully retained, exact-byte
source manifestations before R006 performs and records any further FT decision.
Integration owns the shared manifest/export rebuild and guarded merge.
