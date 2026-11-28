# Receipt Fold 0.3.0 candidate — Balanced Receipt host integration

Refs #674; #338/#339 at f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64, section 4. Restricted finite model and creative audio interpretation; no human or physical recovery claim.

## Controls and clock

Existing IDs 1700–1708 and class IDs unchanged. 1709 balanced mode (off default), 1710 epoch (5–1000 ms, 995 steps), 1711 seed (0–65535, 65535 steps). The native RR01 laboratory retains its 32-bit seed; the host deliberately exposes 16 bits to fit the existing two-word coherent mailbox. Balanced mode uses the existing effective budget and endpoints, overrides the legacy contract only while on, and uses deterministic complete multiplier/tie cycles, not IID draws. Enabling, changing seed, epoch or resolution restarts the draw schedule. Reset also restarts it; schedule position is transient, not saved. Endpoint/budget changes preserve the clock. Bypass slews wet to zero while clock continues. Shared stereo clock, independent channels. Five-ms table retarget and wet slew, no additional latency or audio tail; quantizer discontinuities remain. One shared transfer table, not a dual processor crossfade.

## State

RF04 = 20 bytes: magic, little-endian uint64 control word (lower 32 bits RF03; bit 32 enable; bits 33–42 epoch milliseconds; bits 43–58 seed; bits 59–63 zero), then binary64 wet. RF01/02/03 read with balanced off, 25 ms, seed 0. RF04 writes always; older plugins cannot load it. Back up projects before upgrading. Old preset utility still emits RF03; RF04 preset-file authoring/import not qualified.

## Reproduction and qualification

Native: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run receipt_fold_balanced_host_test with two WAV paths for the original fixed-contract vs balanced-mode four-second stereo demonstration; same score, endpoints, resolution and wet, with 4–7 bit resolution and epoch changes. This compares the legacy deterministic lower tie with the balanced family and fair ties together, not an isolated estimate of tag randomness. GCC 14.2 Linux CTest 10/10, Clang 17 ASan/UBSan new regression passed. 192000 exact legacy stereo frames, 192000 balanced oracle frames (1e-7 tolerance), 192000 partition-invariant frames across six rates and both float formats. 10000 RF04 roundtrips and normalized rebuilds, 10000 RF03 migrations, 56 RF01/RF02 migration samples, 20000 malformed-state probes. 30000 concurrent requests per run, bounded busy-save failure permitted. No audio-thread locks, heap, I/O in the core. No hard deadline, desktop DAW, listening or independent review claimed.

VST3 build: exact official SDK 3.8.0 build 66 and all recursive pins per SDK-PIN.txt and CMake; existing Windows workflow only. Local GitHub DNS prevents SDK checkout, so adapter is source only until exact-head hosted build and official validator pass. Keep the qualified 0.2.0 bundle for audition/rollback. Draft/HOLD.
