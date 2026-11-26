# FX-009L — Multi-pair Receipt laboratory

Refs #674, #338/#339 at `f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64`, sections 2–4 of The Undo That Needs a Forecast. Native C++17 research measurement and creative DSP extension, not a scientific acceptance or human study. Existing RF04 VST3 source, IDs, presets and audio law are unchanged.

## Model and controls

A matching contains disjoint pairs; each pair maps both members to the lower index and the remaining states are unchanged. The decoder trusts the action, collapsed index and exact receipt. `Matching::pair` rejects overlapping pairs. Low-level calls require valid indices, a matching constructed via `pair` (do not mutate its public representation), and valid receipt fields. `Live::apply` validates the complete configuration atomically from the audio owner's perspective; it is not a concurrent mailbox.

- Resolution 3–8 bits; pair count 0–128 subject to N/2. Geometry seed selects a reproducible shuffled matching, not a uniform statistical sample. Pair count takes a prefix of that matching.
- Fixed: low-bit tag of requested budget, lower-index tie decision. Balanced: finite-field permutation, low-bit tag, shared fair tie traversal; receipt seed independent of geometry seed. All pairs share one multiplier and tie direction per epoch.
- Preview: select one common original-index digit maximizing the number of separated pairs, lowest digit on ties. This is a restricted heuristic, not an optimal general codebook. Known action: tag upper/lower membership using the full matching, one bit suffices. Both preview and known always use one bit; the budget setting applies only to fixed/balanced. Preview hint incurs a separate channel cost.
- Epoch 5–1000 ms; 32-bit receipt seed; geometry changes preserve clock, seed/rate/resolution/epoch restart it. Five-ms interpolation of transfer tables and wet/bypass slew. Stereo shares schedule but never mixes channels. Reset restarts seed; finite input/output clamped to +/-1 FS, zero preserved, no algorithmic delay or audio tail. Quantizer discontinuities and aliasing remain. No dynamic allocation, blocking or I/O in frame/apply; bounded rebuild is more expensive than settled processing. No deadline guarantee.
- MR01: 28 bytes, little-endian. Magic 4, bits/count/budget/contract 4, epoch 2, bypass/reserved 2, geometry seed 4, receipt seed 4, binary64 wet 8. State is configuration only; no clock or ramp history. Separate native format, not a VST3 preset or RF04 migration.

## Research controls

For any fixed matching and endpoint, complete balanced traversal has exactly N/M-1 incorrect draws out of 2(N-1), M=2^budget. Unpaired states are exact. This marginal holds for disjoint pair fibres, not arbitrary many-to-one actions, and does not imply independent errors across pairs. The explicit pairs (0,1) and (2,3) have identical XOR difference and perfectly correlated lower-endpoint error indicators under the shared draw. Audio error is not the discrete probability. The deterministic schedule is not IID; a short correlated signal need not realize the marginal.

The native test reconstructs the pinned five-action, ten-triangle counterexample using 30 active states padded by two isolated states. All 32 two-hint partitions fail a bipartite union test; 2+2+1 works with three hints. A smaller single-action witness pairs (0,1), (4,6), (3,7); no common raw binary digit separates all three pairs. Known matching membership is exact. The small witness does not rule out unrestricted binary tags for a known matching.

## Build and audition

From this directory: `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release`, `cmake --build build --config Release`, `ctest --test-dir build -C Release --output-on-failure`. Run `receipt_fold_multi_test --render ./` (use the built executable, on multi-config Windows builds under Release) for four original four-second stereo WAVs and MR01 patches. Settings: 5 bits, 16 pairs, fixed/balanced budget 1, geometry seed 9, receipt seed 42, 35 ms epoch, wet .8. The initial geometry 17 rendered fixed and preview identically because digit zero was best; geometry 9 deliberately separates the conditions (4/16 versus 12/16 pairs). Known separates all 16. No subjective listening claim. A/B comparisons include different tie policies as well as tag changes.

Existing SDK pin and notices remain in force for the separate plugin target. For a plugin build set MHAC_VST3_SDK to the exact recursive checkout per SDK-PIN.txt and VST3.md. No SDK replacement or new adapter; native test does not require SDK. This iteration does not ship a new VST3 binary. The old 0.3.0 bundle remains the installable effect. No state/parameter IDs changed.

## Qualification checkpoint (2026-11-26)

GCC 14.2 Release CTest 12/12, Clang 17 ASan/UBSan dedicated test PASS. 18,076,032 decoder world evaluations across 3–8 bits, three geometry seeds and four pair counts per resolution, complete balanced cycles for every budget; 120,000 paired double stereo frames at five rates and 96,000 exact float32 single-pair reference frames. MR01 roundtrip/reserved-bit rejection, silence, invalid configuration, bypass and nonfinite checks. Four WAVs and patches regenerated byte-identically in same build. Initial compilation exposed namespace ambiguities, corrected by explicit namespace alias; initial small witness accidentally shared a digit across two pairs, corrected before qualification. No independent reviewer; same AI implementation and tests. Dense per-frame rebuild, actual callback deadlines, VST3 integration, desktop DAW and macOS/Windows new-source validation remain open. Do not claim research validity from structural checks.
