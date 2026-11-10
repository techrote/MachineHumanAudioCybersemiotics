# R005→R006 source-custody Integration verification — 10 November 2026

**Refs #5 / #6.** This note accompanies source-unchanged reuse of the three paths from R005 author Draft #133 at original head `07d5ee2e92a33cc3e461695d374f4ddf5de425aa`. Integration base is R006-accepted `83dd4791f008835544bb8884be8b4f5934fad654` (PR #135; canonical title/abstract 8, 5 include + 3 uncertain). The author's earlier '6 TA' checkpoint in README was correct at its authored time and is **not** a current corpus count; it is preserved as history rather than silently rewritten.

## Independent evidence check

[Original prior source-acquisition job #129816985315](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/42812437569/job/129816985315) has three actual `MHAC_R006_PDF_RECEIPT` lines: Becker 2025 Hamburg HTTP 200, 10,436,314 B, 25pp, SHA-256 `e5a2429e47e15208e285c4f3c1aa35e86529b0591139ff36d46e94babe42f230`; Romeo 2025 Chalmers HTTP 200 twice, each 3,445,682 B/23pp but distinct SHA-256 `ab894fbe2b707df1a140320910ed71dc2799e200c99a15ad373b07c712a5ea21` and `1261fc33accc55c7098ddd59e4f507f95b4d79fa31e3a4b308feddfcb2a7c14c`. The associated original response HTTP Date values were 2026-11-10 12:03:09, 12:03:12 and 12:03:14 UTC, respectively. Checked against original runner log, not reverse-inferred from a DOI or future mock file.

These historical receipts do **not** supply retained original PDF bytes, licence approval, complete-article reading, participant identities, independent samples or an R006 full-text inclusion. The proposed CLI can hash **a later genuine retained local original** into operator-attested JSON and verify local bytes; self-reported rights, edition, timing and reading extent remain unverified by that tool. Synthetic tests are not primary-source experiments or real acquisition.

## Current canonical gate and owner action

Merged-main `evidence-flow.json` after #135: **8** title/abstract (5 include/3 uncertain); full-text 1 exclude, 1 awaiting text, **6** required FT decisions missing, 0 FT include; **0** admitted publications, studies, experiments or independent samples; selected E/G 0/0. The frozen 2026-10-04 search cutoff is unchanged; no additional canonical search hits were registered.

**Single critical follow-up:** R004/Integration must lawfully and durably retain exact original Becker 2025 DOI `10.1145/3706066` and Romeo 2025 DOI `10.1145/3711938` byte instances in rights-compliant private storage, capture actual retrieval/acquisition, licence and edition evidence, verify SHA-256 on the retained files, then register their manifestations through the canonical source path. Romeo 2023 original IEEE DOI `10.1109/RO-MAN57019.2023.10309631` separately remains an `awaiting_text` case; its Zenodo supplement is not the article. R006 alone determines full-text E1–E6, publication–study–experiment–independent-sample mapping and Track E/G eligibility. No human assessor or external permission claimed.

Reviewed original source-PR scope in [source audit #5844937211](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/133#pullrequestreview-5844937211); Integration runs exact final-head full tests and merged-main CI before any acceptance. #5/#6 stay OPEN, R007/R008 are **not** selected-corpus-ready.
