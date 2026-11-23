# MHAC-X007 — Execution and qualification ledger

**Project:** [Issue #191](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/191) · [Draft PR #192](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/192)  
**Scope:** only original isolated expedition files and one narrow test-import bridge.  
**Base at PR opening:** \`3791929a376ef32e586e50f20c58ba76625fd10f\` on \`main\`.  
**Research/implementation:** one GPT-6 assistant with GitHub connector, published scholarly web material, code inspection, independent local audio arithmetic and GitHub CI. This is self-review, not independent expert or human validation.

## Actual checks as of 23 November 2026

1. GitHub Actions [Research integrity run 45247897104](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45247897104), PR head \`0a3befbfc5a0bb43fabfa6d942d56e4edd4f7383\`: **Unit tests — success**. This includes repository test discovery through the isolated \`tests/test_mhac_x007.py\` bridge.
2. In the same run: **Validate repository — failure**; the deterministic fixtures step was skipped. The expedition README links \`EVIDENCE.md\`, which was not present at that first run. The repository's \`tools/validate.py\` explicitly refuses missing local Markdown link targets; this file is now added, but a subsequent final-head CI run is required before attributing the failure to that cause alone.
3. The authored test code exhaustively enumerates the \`3^6 = 729\` simple four-vertex absent/same/different relation graphs and 16 possible local relabel masks per graph (11,664 graph/mask checks), plus input, theorem, certificate and wave boundary controls. **These are finite software assertions, not empirical study samples.**
4. An independent, minimal local Python rendition of the published oscillator specification generated three **synthetic WAVs**, each at 22,050 Hz, stereo PCM16, 13,230 frames. Its SHA-256 values:
   - \`balanced.wav\`: \`aa438224d48597ececb0e06a0740b980dce88ac54fb52468f5baa61babf3b2dc\`
   - \`frustrated.wav\`: \`4cd84d2eedb32c579ce628d1cd21984a4ada94d1abcaf0664ae3b33bae4a5f5d\`
   - \`switched_frustrated.wav\`: \`4cd84d2eedb32c579ce628d1cd21984a4ada94d1abcaf0664ae3b33bae4a5f5d\`
   
   The last two hashes match as the algebra predicts, whereas a one-edge change changes rendered bytes. These hashes are **local reconstruction observations**, not claims that the checkout CLI was run or that the uncommitted \`build/\` directory exists on GitHub. The exact checkout CLI can be independently reproduced from \`choir.py\`.
5. The source-bounded reading is recorded in [SOURCES.md](SOURCES.md). The Zaslavsky author-posted §1.1 and Theorems 1.1/1.2 were directly inspected; the Harary original and Hertz full article were not read.
6. The \`choir_lab.html\` interactive visual/Web Audio UI has been authored and reviewed statically for obvious structure. **No browser GUI acceptance, Web Audio listening study or accessibility user test was performed.**

## Qualification ledger

| Gate | Status |
| --- | --- |
| Isolated paths, source/rights limits, correct claim classes | Completed author self-check |
| Synthetic finite tests | First GitHub Actions run reports success |
| Repository validation and fixtures | Not yet passing on an exact final head |
| Distinct balanced/frustrated PCM and invariant switched duplicate | Independently reproduced sample-level hashes; exact checkout run still to compare |
| Browser interactive runtime and playback | Pending external/browser verification |
| Human sound interpretation / behavioral impact | Not studied, not claimed |
| Required final-head CI, approval and merge | Pending, PR remains Draft |

## Falsifiers and acceptance decisions

A result would be materially falsified by any four-vertex signed graph where the streaming algorithm disagrees with independent complete assignment enumeration; any local binary recoding that changes a complete cycle XOR; any emitted certificate whose accepted path does not validate; a generated WAV whose purported switched counterpart differs in exact bytes; or any claim that a balanced graph identifies truthful sources.

The strongest negative result is retained: **greedy accepted-subset selection is not globally minimum correction**, and the identity of a rejected edge depends on input order. These limitations are not implementation bugs to remove by relabeling them as confidence scores.

## Next exact verification

Run the fresh GitHub workflow on the commit that adds this ledger; inspect check-runs **and** legacy commit status for that precise SHA. If repository validation remains red, inspect the failing step and correct only the scoped expedition. Re-run \`python research/expeditions/frustrated-choir/choir.py --out build/mhac-x007\` in a clean checkout and compare WAV digests to the local reproduction. Keep human listening/GUI acceptance separate from code proof and retain the Draft PR if any required gate remains unverified.
