# R006 — Romeo 2023 canonical full-text access disposition (10 November 2026)

Refs #6. **This branch is a Draft/HOLD handoff, not an accepted corpus or merged manifest.**

## Exact pinned source and decision chain

- `SRC-REL-ROMEO-2023@1`: Romeo, Torre, Le Maguer, Cangelosi & Leite, *Putting Robots in Context: Challenging the Influence of Voice and Empathic Behaviour on Trust*. 32nd IEEE RO-MAN 2023, pp. 2045–2050, DOI `10.1109/ro-man57019.2023.10309631`. Original R004 source: verified DOI, `metadata_only`, no registered original-PDF manifestation. Heriot-Watt portal distinguishes conference (28–31 August 2023) from final publication listed 13 November 2023. Do not rewrite the historical source date without R004 coordination.
- `SCR-R006-REL-ROMEO-2023-TA@1`: canonical single-agent title/abstract `uncertain` decision (8:11:16 UTC 10 November), not a human second assessment. The Heriot-Watt abstract reports two video-based online studies. No original paper body was read for this first-stage decision.
- **New** `SCR-R006-REL-ROMEO-2023-FT@1`: `awaiting_text` under frozen v1 §6.2(3), not `exclude` or `include`. Actual agent registrar/date and previous TA/source revision pins are preserved; `reading_refs=[]` and `review_refs=[]` truthfully record no full-paper reading or human reviewer. Its absence of a source-file manifestation is deliberate and this status is not a scientific determination of E2.

## Access boundary and legal routes

1. [Heriot-Watt institutional original-publication landing page](https://researchportal.hw.ac.uk/en/publications/putting-robots-in-context-challenging-the-influence-of-voice-and-/): abstract/metadata and DOI only, re-read on 10 November; no original report body or new audio evidence.
2. [Zenodo version 1, DOI 10.5281/zenodo.8042317](https://zenodo.org/records/8042317): public landing page advertises `ROMAN2023_Ila_Marta.pdf` and MD5 `7137b64efa2e75ab9aec951ca03449fe`, **not verified from local original bytes**. A direct file-download request timed out in this pass; its preview rendered only viewer controls, not supplement text. Web-mediated access time was not captured at HTTP-response precision, so only the observation date is claimed.
3. The accepted [R005 source-access checkpoint, PR #111](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/111) documents prior publisher/supplement retrieval failures and distinct hit provenance. No 2023 paper, utterance scripts, sound or video files have been accessed here.

The distinct 2025 ACM paper (DOI `10.1145/3711938`) and its physical-maze procedure **cannot establish** equivalence to 2023 OS1/OS2, a conference-to-journal extension, repeated participants or independent samples. [R005 PR #115](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/115) is still a separate Draft source investigation; it is not a basis for claiming 2023 experimental identity.

## Integration contract

This change introduces **one new canonical full-text status record**, but **does not** change shared `research/registry/generated/*` files. Integration Shepherd alone must serialize those changes in a trusted full checkout before accepting the record:

```sh
python -m unittest tests.test_r006_romeo23_ft_awaiting_20261110 -v
python -m unittest discover -s tests -v
python tools/validate.py --write-exports
python tools/validate.py --previous-ref <exact-current-accepted-main-SHA>
python -m tools.build_record_fixtures --check
git diff --check
```

Review the entire diff and complete record/identity history, regenerate both `records-index.json` and `evidence-flow.json` against the exact candidate head, run exact-final-head CI, obtain required source/scope review and guarded merge. **An initial PR check that complains about stale generated exports is an expected unmerged integration gate, not a pass.** Never omit the large index or change validator semantics to accommodate it.

Expected *if successfully integrated*: four canonical TA decisions unchanged; canonical FT decisions **one exclusion + one awaiting_text** (Kühne/ Romeo 2023); Becker 2025 and Romeo 2025 still need full-text disposition; 0 canonical FT inclusions, 0 STUDY/EXP/SAMPLE, 0 selected Track E or G corpus. The `awaiting_text` item remains explicitly unresolved for programme completion.

**Next actual gate:** R005 or the source owner obtains the lawful original six-page 2023 report and original supplementary scripts, validates identities/bytes and exact audio-task utterances; R006 then records a new genuinely sourced eligibility disposition and handles any study/experiment/sample overlap with 2025. No owner purchase, new human review or participant contact is requested.

AI-only screening and register checks are not independent human review, and structural tests are not source-fidelity or scientific validity.
