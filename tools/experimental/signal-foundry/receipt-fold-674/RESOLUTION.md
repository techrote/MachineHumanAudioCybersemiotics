# FX-009F — variable-resolution native laboratory (Refs #674)

Research #338/#339, pinned f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64 sections 2–3: direct restricted pair-collapse endpoint contract extended to dyadic alphabets, creative audio rendering. Not scientific or human evidence. Predecessor b0e7f818fb7cd1a79d99453c408e208adda01334 Windows qualification 45831272174 and integrity 45831272110 both passed. Main 495a98ca12bae467a507031f04931aa4254b1866; sibling #681 inspected read-only.

## Interface

Audio-thread-owned resolution::Live, independently usable C++17. Choose 3–8 bits (8–256 bins), ordered pair lo < hi < 2^bits, fixed receipt budget 0–bits, absent/fixed/preview/full, wet 0–1, bypass. Fixed retains low bits; preview retains one differing bit with trusted action hint; full retains all bits. Decode lower endpoint on ambiguity. Only one pair collapses; at high resolution fewer amplitudes are affected. Preview/full recover quantized indices only. Output bin centres are half-scale as in the legacy engine. Exact zero and nonfinite input map to zero; dry is sanitized/clamped. No tail or delay.

The 256-bin finest-grid representation aligns all dyadic bins. Five-ms crossfade of transfer laws on a common input grid; retarget starts at current interpolated table. Wet-only changes do not rebuild tables. Fixed storage, bounded 256-entry rebuild plus interpolation on changed law; per-frame evaluation uses two lookups. No allocation/locks/I/O in native frame/apply. Dense discrete automation CPU deadlines not established. Quantization discontinuities and aliasing remain; smoothing only controls law changes.

RF02 is 20 bytes: magic, bits/lo/hi/mode/budget/bypass (six bytes), two reserved zero bytes, binary64 little-endian wet. Reader accepts legacy RF01 via explicit migration to 3 bits and one fixed bit; rejects invalid/reserved values without replacing destination. RF01 remains unchanged in actual VST3 0.1.0. RF02 is not yet host state, no new parameters/CIDs, no new binary or DAW support claimed.

## Reproduce

CMake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run receipt_fold_resolution_test --render (Release/ on multi-config systems) in an output directory. Two four-second original stereo PCM16 WAVs at 48 kHz; each second advances from 3 to 6 bits, pair bins/8 and 3*bins/4, wet .8; absent vs preview. Native audio only. Both files deterministic on tested build; peak 0.509979 FS, last 50 ms zero. Per-second RMS A/B difference 0.216174, 0.134894, 0.092860, 0.061029 FS (specific input, not perceptual). No listening claim.

GCC 14.2 Release and Clang 17 ASan/UBSan CTest 6/6 each; 1,506,336 endpoint contract/state cases (both endpoints, all ordered-by-value pairs, modes and budgets), 120,000 exactly equal double stereo frames vs legacy through RF01 migration across five rates; retarget bound, invalid state, float bypass and silence probes. Not exhaustive over all interior indices or float32 automation. SDK root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and seven root gitlinks rechecked; existing exact SDK build/notice contract unchanged. Local SDK checkout DNS blocked. New Windows qualification and actual host integration outstanding. Single AI implementation/test, Draft/HOLD.
