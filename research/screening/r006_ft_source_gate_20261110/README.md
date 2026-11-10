# R006 — four-candidate full-text source/admission qualification (10 November 2026)

**Refs #6 — Draft/HOLD; not a canonical full-text screening decision or a selected corpus.** The underlying four source-pinned title/abstract decisions **are already canonically admitted** by merged [PR #109](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/109); this tranche must not recreate those records. Based on accepted main `0e7f9debc12e66fb75c132c6542b62041f67d53a`. All work is confined to R006 screening and issue tests; Integration retains `research/registry/state.json`, generated index/exports and guarded merge authority.

## Decisive admission distinction

The executable `check_gate.py` and four-case [QUALIFICATION.json](QUALIFICATION.json) check the *actual* canonical TA IDs, accepted source revision and DOI, frozen cutoff, manifest availability, separate later exclusion review and the limits of the consulted source material. This is a dated source/admission readiness check; its output is **not** an evidence-flow export and cannot replace the live validator or a source-reading event.

| Publication, DOI | Accepted TA | Present FT proposal | Present technical/scientific limit |
|---|---|---|---|
| Kühne 2020, `10.3389/fnbot.2020.593732` | uncertain → FT | Exclude on E2, source-located only | R004 already registers `FRONTIERS-PDF` (15 pages); two separate-in-time AI passes support E2=no. No canonical reading `AID` or FT `SCR`; a source-fidelity check, authentic reader attribution and serialized admission are still needed. |
| Becker 2025, `10.1145/3706066` | include → FT | Main robot Battleship phase provisionally E2-eligible | Full article publicly available from Hamburg (R005 #106; R006 #107), **but R004 source @1 has no registered manifestation**. Pre-study voice ratings and pilot cannot silently become independent eligible samples. |
| Romeo 2025, `10.1145/3711938` | include → FT | Provisional FT inclusion | Earlier web-parsed institutional article passages were read; **R004 source @1 has no manifestation** and the article PDF direct request failed in this audit. The 2023/2025 study/sample relation remains unknown. |
| Romeo 2023, `10.1109/RO-MAN57019.2023.10309631` | uncertain → FT | **awaiting_text**, never E2-excluded | Only the institutional abstract, DOI and Zenodo supplement listing have been documented; original IEEE paper/scripts not yet verified (R005 #111). |

### New bounded publisher reading in this qualification

Original legal publisher PDF: [Kühne et al., *Frontiers in Neurorobotics* 14:593732 (2020)](https://www.frontiersin.org/articles/10.3389/fnbot.2020.593732/pdf), DOI `10.3389/fnbot.2020.593732`. On 10 November 2026 this GPT-6 pass inspected **PDF page images 4–5** and selected PDF text including page 1. Page 4 **Materials and Methods > Design / Audio Stimuli** identifies five interview-derived utterances per voice (Watson, Sophia, human), including apparent imperatives and robot persona statements; page 5 **Procedure** places them in a voice/speaker first-impression rating questionnaire. That supports the *proposed* G01/E2 exclusion: no operational task-state information or action instruction to the listening participant. The superficially imperative sample is a serious negative case, not an instruction to the participants to act. The full paper was not read, no sound stimulus was heard, and neither the original PDF bytes nor its SHA-256 were reverified in this run. The `FRONTIERS-PDF` hash in R004 is explicitly **inherited prior evidence**, not newly proved.

Access method: open-access original publisher PDF through a web PDF reader and rendered page images. Reading day: 2026-11-10; **exact HTTP response timestamp was not captured** and must not be invented. Earlier source review and the [separate 05:32 UTC later pass](../r006_kuhne_e2_laterpass_20261110/RECHECK.json) were both AI-assisted, nonblinded, not human adjudication. Frozen v1 §6.2 permits a separate later intra-agent check; it never becomes independent human agreement.

### Specific Integration/R006 next operation

1. For **Kühne only**, independently inspect the same publisher Methods pages and assess the contrary task-message interpretation. If supported, record a genuine performed `assistance` reading event with the **actual** reviewer identity/time, pinned `SRC-REL-KUHNE-2020@1`, `FRONTIERS-PDF`, bounded file-page ranges, `selected_ranges_read` and no fabricated PDF/hash/audio claim. Distinguish the 05:32 later E2 verification from any new reviewer.
2. Submit one `full_text` `SCR` for Kühne with `decision=exclude`, reason `E-NOT-MACHINE-MESSAGE`, `reading_refs` linking the valid reading `AID`, correct frozen protocol/track, the already admitted uncertain TA prerequisite and real decision actor/time. This is a **source-scope scientific decision**, not an independent study/sample record. If material contrary text changes E2, retain uncertainty and do not register the exclusion.
3. Integration serially adds records/roots (only as necessary), regenerates **all** deterministic shared registry views including the large index, and verifies the full history; only then qualify exact-final-head CI and postmerge main. No source manifest edits or cross-worker branch changes are authorized by this PR.
4. Separately route Becker/Romeo 2025 missing R004 source manifestation/version through their owning lane or explicit Integration coordination; retain Romeo 2023 `awaiting_text` and R005 #111 for original report/supplement retrieval. **Do not construct fake AID records for the three unregistered manifestations.**

Reproduction from a full checkout:

```sh
python research/screening/r006_ft_source_gate_20261110/check_gate.py
python -m unittest tests.test_r006_ft_source_gate_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

The first command expects the **dated 4 TA / 0 FT checkpoint**, with one source-located exclusion candidate and three blocked FT candidates. Historical checkpoint numbers must not be silently updated to pretend that future records were already registered. Graph/manifest checks on the *current* complete repository must be rerun when Integration actually registers full-text records.

**Current scientific delta:** canonical TA 4→4; canonical FT 0→0; STUDY/EXP/SAMPLE 0→0; selected Track E/G corpus 0→0. One report has both a registered R004 manifestation and two temporally separate source-limited exclusion analyses; **zero new full-text decisions admitted**. This reduces the *actionability* of the highest-value pending exclusion without claiming corpus acceptance. #5/#6/#7/#8 and R009 dependency remain open. AI-authored technical tests validate no scientific truth or independent reviewer.
