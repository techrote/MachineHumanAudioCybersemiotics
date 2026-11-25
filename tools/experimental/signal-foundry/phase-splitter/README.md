# MHAC Phase Splitter 0.1.0

Exploratory stereo VSTfx candidate and portable C++17 core. Refs #505, #416 / [draft #417](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/417), pinned 0039dbdead33f28b7eefb4ad5680aa05d437ff29. Direct realization of the diagonal projector delay E_d = I-P+z^d P, where P projects onto the common-mode axis. The complementary return R_d = P+z^d(I-P) satisfies R_d E_d = z^d I. Fixed integer delay, full wet, unity gain and unclipped normal signals only: total energy over a fully flushed stream is preserved, and cascading matching forward/return recovers both channels delayed by d samples (within floating precision). Neither output alone generally preserves the input. No claim of loudness equality, human effects or universal dyadic factorization.

For a left-only sinusoid of period q samples, left power fraction is cos²(pi*d/q), right is its complement. At 48 kHz and d=16, 750 Hz (q=64) gives equal power; q=81 gives about 66.19% left. Use as a spatial comb-routing effect or measurement instrument. For audition set a stereo track, place mono material on one channel only, sweep the delay, or use both channels for complementary phase routing. Two instances at the same delay, forward then return, mix and gain 100%, recover the input delayed by d when no limiting occurs. Leave headroom: per-channel peaks can grow even when total energy is conserved. No feedback.

| ID | Control | Mapping |
|---|---|---|
|100|Delay|1 + round(63p) samples; default 16|
|101|Return mode|0 delays mid; 1 delays side|
|102|Mix|0–100% linear dry/wet|
|103|Gain|0–100% linear output gain; default 50%|
|104|Bypass|slews to dry unity, delay history continues|

Fixed ring buffers, no allocations in DSP, finite sanitization and input/output clipping to +/-1 FS; deliberately not a transparent bypass for overrange input. These safety bounds, gain, dry blending and moving interpolated taps are creative additions, not paraunitary operations. Delay motion and direction/mix/gain use 5 ms full-range slew (not a guarantee of click-free behavior for arbitrary pathological input). State MHSP v1, 28 little-endian bytes, normalized millionths; runtime history not saved. Stereo only, host-native parameters, float/double adapter, 0 reported compensation latency (intentional delay is the effect), conservative 64-sample tail. A forward/return cascade adds d samples of real latency even though each effect reports zero.

Preset recipes (Delay, Return, Mix, Gain, Bypass): quarter-cycle witness (15/63,0,1,1,0), safe wide comb (31/63,0,1,.5,0), return (15/63,1,1,1,0), subtle (7/63,0,.35,.7,0). Use matching sample delay rather than milliseconds when testing the inverse. Reinitialize or allow settings to settle before comparison.

## Build and reproduce
```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```
Run splitter_test with an existing output directory to produce three 48 kHz stereo PCM16 little-endian files (dry-left, forward, return-mode separately), 3 seconds each, 100–3700 Hz chirp. Wrap with Python wave or import as raw. The third is not a cascade. No copyrighted source audio.

VST3: clone official Steinberg tag v3.8.0_build_66, verify root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0, recursively initialize gitlinks and keep clean. Then cmake -S . -B build-vst -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/path/to/vst3sdk ; cmake --build build-vst --config Release. The scoped Windows workflow verifies root and recursive checkout, runs official validator, packages SDK notices and receipts. Expected seven direct SDK gitlinks (verified from qualified Retreat Shaper 0.2.0 receipt, new build must verify its own): base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206; cmake de6e54eeaaab35b7145f5c32c279b5e892146e04; doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4; pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c; public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95; tutorials 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34; vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c. No SDK substitution. Once qualified, copy complete MHACPhaseSplitter.vst3 to C:\Program Files\Common Files\VST3 and rescan. Windows SDK qualification pending; Linux core tested; Linux/macOS plugins intended only.

## Qualification receipt — 2026-11-25
Main base 495a98ca12bae467a507031f04931aa4254b1866. Native Linux g++ C++17 -O2 -Wall -Wextra -pedantic: 544,876 checks including renders PASS; separate ASan/UBSan 544,870 checks PASS. Eight sample rates (including fractional extremes) x 64 delays: both-channel reconstruction within 1e-14 and total energy within 1e-10 after flushing; impulse, nonfinite/extremes and float automation, bypass settling, state version rejection and q64/q81 spectral power checks. Counts include per-sample comparisons, not independent trials. Three PCM payloads repeated byte-identically. Tested and remote Git blob identities: splitter.hpp 719f24dc826d1bd812c0b95c5da07efb2e046a07, test.cpp e7ac373abd9a3310cb265f480a94edafdb7aaac9. WAV SHA256 dry 484d36ffaaf175ff0e6fbd68a9d3d5e44a19754e1d5e354b204d200151f7154b; forward 5e4e27919cde0533beded3a19c04b9b852920cea984bcae4fc90c8b1b5e9f6de; return mode 07d7b224a4b27bab61b019b72dd3b0c4d9dd99f2e52efcd2e3664050c189c8a5. Peak .320435 FS, no clipped PCM. Same-agent source/test; no independent review or listening. Native GitHub clone still fails DNS, so the adapted VST3 source and CMake SDK path have not been compiled locally. Adapter boundary tests, host CPU/automation, physical DAW audition and platform validation pending. No new binary claimed. No canonical manifests changed.
