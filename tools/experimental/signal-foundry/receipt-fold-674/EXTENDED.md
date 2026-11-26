# Receipt Fold 0.2.0 candidate — extended host controls

Refs #674, #338/#339 (f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64 §§2–3). Direct restricted pair-collapse index law, creative audio rendering and engineering integration; no human, physical recovery, listening or scientific acceptance claim. Base main 495a98ca12bae467a507031f04931aa4254b1866; predecessor c1b8586258946de0669b3f6eec9b79ec05ce2b91, exact Windows and integrity runs 45841257973/45841258098 succeeded (predecessor plugin still 0.1.0).

## Host controls

| ID | Meaning | Normalized mapping |
|---|---|---|
| 1700 | Legacy collapse pair | rank / 27, unchanged |
| 1701 | Receipt contract | mode / 3, unchanged |
| 1702 | Wet | binary64, unchanged |
| 1703 | Bypass | 0 or 1, unchanged |
| 1704 | Resolution | (bits - 3) / 5, 3–8 bits |
| 1705 | Fixed budget | budget / 8, effective min(budget,bits) |
| 1706 | Fine endpoint A | coordinate / 255 |
| 1707 | Fine endpoint B | coordinate / 255 |
| 1708 | Fine source | 0 legacy, 1 fine |

Default 3 bits, budget 1, fine disabled, dry. Both component IDs retained. Coarse endpoints multiply legacy indices by 2^(bits-3), so the original rank remains stable. Fine coordinates are sorted, then right-shifted by 8-bits; coincident indices expand to the next adjacent index (or previous at the upper edge). Every pair at every resolution is reachable. Fine mode ignores but retains legacy rank. Budget retains its requested value when resolution is reduced. Same-offset control edits are applied as one complete transaction. Five-ms transfer/wet ramps, no feedback, zero tail/latency. Quantization/aliasing remain intentional. Finite audio is bounded to +/-1 including dry/bypass.

## State

RF03 is 16 bytes: magic RF03, 32-bit little-endian controls (rank 5, mode 2, bypass 1, resolution offset 3, budget 4, A 8, B 8, fine 1), followed by binary64 wet LE. RF01 imports with default new controls, RF02 imports exact effective configuration (fine enabled at >3 bits). Older plugin cannot read RF03; retain backups before upgrading. Invalid state leaves destination unchanged. Controller uses same migration. No runtime history persisted. Bounded atomic sequence snapshots preserve binary64 wet; non-audio save may explicitly fail when busy. Existing RF01 preset generator remains useful for legacy patches, not an RF03 preset generator. Actual DAW import untested.

## Reproduce

Native: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run receipt_fold_extended_test --render in an empty output directory for original 4-second stereo coarse-pair.wav and fine-pair.wav (5/6/7/8-bit stages, same input and wet). Try coarse vs fine at 80% wet, absent receipts, A=96, B=175. Try increasing fixed budget with the same pair; preview is exact for the restricted discrete model, not continuous waveform reconstruction.

SDK checkout and notices remain governed by SDK-PIN.txt and the existing CMake checks and Windows workflow. For an actual qualified build copy the complete .vst3 directory into the DAW's standard VST3 scan location; Windows C:\Program Files\Common Files\VST3. New binary not claimed before strict qualification.

## Same-agent verification, 26 November 2026

GCC 14.2 Linux Release CTest 7/7, Clang 17 ASan/UBSan 7/7. 131072 exact legacy stereo frames and 262144 exact block-partition frames across eight sample rates and float32/64; all 393216 ordered fine endpoint mappings valid; RF02 migration all pairs at six resolutions, RF03 state/normalization 10008 patterns, RF01 rank migration 28. Concurrent 30000 state requests, zero busy saves in recorded render run (scheduling-dependent; bounded failure possible), no torn accepted snapshots. Dense per-frame automation native-only 480000 stereo frames in 0.308231 s on current Linux environment, not a deadline or DAW test. Both new WAVs byte-identical on same-build rerender. SDK tag and all seven recursive trees reverified; no nested gitlinks. Local DNS blocks exact checkout, no substitute. No actual 0.2.0 Windows or official validator result yet; existing narrow workflow reused. DAW lifecycle, true host queues, RF03 preset import, independent review, latency distribution and listening remain unqualified. No shared/frozen/sibling edits or merge.
