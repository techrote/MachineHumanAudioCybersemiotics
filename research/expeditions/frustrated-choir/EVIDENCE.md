# MHAC-X007 — Execution and qualification ledger

**Project:** [Issue #191](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/191) · [Draft PR #192](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/192)  
**Scope:** only original isolated expedition files and one narrow test-import bridge.  
**Base at PR opening:** `3791929a376ef32e586e50f20c58ba76625fd10f` on `main`.  
**Research/implementation:** one GPT-6 assistant with GitHub connector, published scholarly web material, code inspection, independent local audio arithmetic and GitHub CI. This is self-review, not independent expert or human validation.

## Actual checks as of 23 November 2026

1. GitHub Actions [Research integrity run 45247897104](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45247897104), PR head `0a3befbfc5a0bb43fabfa6d942d56e4edd4f7383`: **Unit tests — success**. This includes repository test discovery through the isolated `tests/test_mhac_x007.py` bridge.
2. In that initial run **Validate repository failed**, with deterministic fixtures skipped. The README then linked the absent `EVIDENCE.md`. Adding the missing target resolved the defect; [run 45248310343](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45248310343) at `1e79e6586424c4cfe93b16f80e64c20b09100958` completed **success**.
3. Expanded experiment head `83bec2620064064e49fbc535be6ad2cdf4acd605` passed [Actions run 45248689791](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45248689791): **Unit tests, Validate repository and Check deterministic synthetic fixtures all succeeded**. Job steps were inspected. Any later ledger amendment needs another head check.
4. The authored test code exhaustively enumerates the `3^6 = 729` simple four-vertex absent/same/different relation graphs and 16 possible local relabel masks per graph (11,664 graph/mask checks), plus input, theorem, certificate and wave boundary controls. **These are finite software assertions, not empirical study samples.**
5. An independent, minimal local Python rendition of the published oscillator specification generated five **synthetic WAVs** at 22,050 Hz, stereo PCM16. The three loop-demo files each contain 13,230 frames; the two order-variant files each contain 39,690 frames. Its SHA-256 values:
   - `balanced.wav`: `aa438224d48597ececb0e06a0740b980dce88ac54fb52468f5baa61babf3b2dc`
   - `frustrated.wav`: `4cd84d2eedb32c579ce628d1cd21984a4ada94d1abcaf0664ae3b33bae4a5f5d`
   - `switched_frustrated.wav`: `4cd84d2eedb32c579ce628d1cd21984a4ada94d1abcaf0664ae3b33bae4a5f5d`
   - `order_ab_first.wav`: `0edcbf8003b6551d5fa5f9222b4d823c423d815e80644b68b50c9427351d1a11`
   - `order_ab_last.wav`: `3e7be523a0b7f9782647046e33939b604c13464fb7ac67988145ca1feec0c6df`
   
   The frustrated and switched-frustrated hashes match as the algebra predicts; a one-edge change changes rendered bytes. The two order-variant WAVs differ **despite sharing the same complete six-edge graph**. This demonstrates that the selected cycle basis and number of dissonances are presentation-order-dependent. All five files are **independent local reproductions**, not outputs from the repository checkout CLI. These hashes are **local reconstruction observations**, not claims that the checkout CLI was run or that the uncommitted `build/` directory exists on GitHub. The exact checkout CLI can be independently reproduced from `choir.py`.
6. The source-bounded reading is recorded in [SOURCES.md](SOURCES.md). The Zaslavsky author-posted §1.1 and Theorems 1.1/1.2 were directly inspected; the Harary original and Hertz full article were not read.
7. The `choir_lab.html` interactive visual/Web Audio UI has been authored and reviewed statically for obvious structure. **No browser GUI acceptance, Web Audio listening study or accessibility user test was performed.**

## Qualification ledger

| Gate | Status |
| --- | --- |
| Isolated paths, source/rights limits, correct claim classes | Completed author self-check |
| Synthetic finite tests | Successful at `83bec262` in run 45248689791 |
| Repository validation and fixtures | Successful at `83bec262` in run 45248689791; refreshed head check required after this amendment |
| Five WAVs: switch-invariant duplicate, substantive edge flip, order-dependent score | Independently reproduced sample-level hashes; exact checkout run still to compare |
| Browser interactive runtime and playback | Pending external/browser verification |
| Human sound interpretation / behavioral impact | Not studied, not claimed |
| Required final-head CI, approval and merge | Head `83bec262` CI green; amended-head CI, review and merge pending; PR remains Draft |

## Falsifiers and acceptance decisions

A result would be materially falsified by any four-vertex signed graph where the streaming algorithm disagrees with independent complete assignment enumeration; any local binary recoding that changes a complete cycle XOR; any emitted certificate whose accepted path does not validate; a generated WAV whose purported switched counterpart differs in exact bytes; or any claim that a balanced graph identifies truthful sources.

The strongest negative result is retained: **greedy accepted-subset selection is not globally minimum correction**, and the identity of a rejected edge depends on input order. These limitations are not implementation bugs to remove by relabeling them as confidence scores.

## Next exact verification

Inspect exact-head Actions and legacy statuses after this ledger amendment. Run `python research/expeditions/frustrated-choir/choir.py --out build/mhac-x007` from a clean checkout and compare its five WAV digests with the independent local reproduction. Browser-review the interactive demo, Web Audio controls and accessibility. Keep the Draft PR unmerged while acceptance gates remain open.
