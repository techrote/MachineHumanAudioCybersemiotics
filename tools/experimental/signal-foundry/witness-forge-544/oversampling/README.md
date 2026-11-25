# Witness Forge — oversampling laboratory (FX-005B)

Refs #552, #544 / #547 (parent b0cf15fa06e02df013501a553b558abab5147c63), #296 / #297 (formal draft c66c128ae550aadd16a46ddc7559406dbbc65be9). This is a creative engineering extension and measurement instrument for the ideal cubic I/Q channel, not a new theorem or human evidence. The existing VST3 adapter, class IDs, WF01 state and SDK build lock are unmodified. Base main 495a98ca12bae467a507031f04931aa4254b1866; other lane inspected (#551). Only this subdirectory added.

## Contract

The standalone C++17 Oversampled class reuses the parent's parameter definitions and cubic law. Select fixed 1x, 2x or 4x at prepare(rate,factor), outside the audio callback. For 2x/4x, a unity-DC Blackman-windowed sinc interpolator and decimator each have 32*factor+1 taps, cutoff 0.45*base-rate, group delay 16 base samples. Process uses fixed arrays and bounded polyphase interpolation plus decimation; no heap allocation, locks or I/O. All modes have 32 base-sample alignment delay; the 1x wet branch is explicitly delayed. Dry and protected bypass use the exact delayed guarded input. Wet tail has finite support through sample 64 of the impulse; 64 samples is a conservative support bound, not a qualified host tail declaration. Output is guarded to +/-1 FS. No intermediate clipping before the decimation filter; final clipping can reintroduce aliasing. The 1x mode is an aligned static-control baseline, not bit-equivalent to the original zero-latency plugin during automation. Drive/coupling/isolation slew in base-rate time and are held across the corresponding high-rate substeps; wet/mix/gain/bypass are applied at the output. Mode is a setup argument, not persisted or automatable. Changing mode resets history; never use prepare as a live switch. Parent WF01 can still encode the six normalized parameters, but mode-aware state migration and host latency reporting are not implemented.

## Reproduce

From this subdirectory: cmake -S . -B build; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run oversampling_test with an existing output-directory argument to write three little-endian stereo PCM16 files, 48000 Hz. Optional WAV wrapping uses standard Python wave (2 channels, sample width 2, rate 48000). Original analytic tones are deliberately high-frequency and not musical presets; monitor conservatively. Use formal controls (Drive/Coupling/Isolate/Mix/Gain/Bypass = 1/1/0/1/1/0). To audition ordinary stereo, try 0.3/1/0/0.7/0.8/0 at 2x as a starting patch (not a listening-tested preset).

## Qualification receipt — 25 November 2026

Linux x64 GNU 14.2 C++17 Release CMake/CTest 1/1 PASS with -Wall -Wextra -Wpedantic -Werror; separate ASan/UBSan executable PASS. 18 factor/rate combinations (8, 44.1, 48, 96, 192, 384 kHz): exact delayed bypass impulse, neutral wet peak at 32, unit DC impulse sum, finite support, Float32/Float64 tolerance, drive change at sample 127, nonfinite/extreme input, invalid setup rejection. Three PCM renders reproduced byte-identically on same machine. Core/source blob identities verified against committed files. No new Windows execution, host adapter, host automation or independent review.

At 48 kHz, two complex carriers +15000 and -12000 Hz at amplitude 0.18 generate a +42000 Hz cubic product that aliases to -6000 Hz at 1x. Coherent double precision projection after 128 samples, over 48000 frames:

| Factor | Unwanted -6000 Hz | Wanted 400 Hz (separate 480/720/800 experiment) | 15000 Hz carrier |
|---|---:|---:|---:|
| 1 | 0.005832 | 0.011664 | 0.197496 |
| 2 | 1.25567231299e-7 | 0.0116638956871 | 0.19752116814 |
| 4 | 1.18940356268e-7 | 0.0116638932459 | 0.19752117647 |

2x/4x PCM16 files are identical in this example; extra CPU does not buy a demonstrated audible benefit. No broadband or arbitrary-distortion guarantee: finite filters attenuate near Nyquist, transient ringing and time-varying automation can change spectra, and nonlinearities after decimation can alias. Offline 10 s of 48 kHz stereo processed in about 0.009/0.074/0.137 s respectively; not deadline certification. No subjective listening.

## Parent binary recovery

Exact-head #547 Windows run 45607412439 and integrity run 45607412217 succeeded. Artifact 15017863087 downloaded: outer SHA256 b9e3201c66b97b20b30f8831e8064d503853825ab69988da8cfb630040dd3e8e matches published digest; inner SHA256 cf44b1c3a78f8471072c1cd3b4c4c308709c13a9882059034e1216e568725df7. Both archive CRC checks passed, PE AMD64 and module metadata VST 3.8.0 / Fx Distortion confirmed, source receipt matches parent, SDK root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and seven gitlinks match parent CMake. Official tag v3.8.0_build_66 freshly resolved to that SHA. SDK license/notice files present. Validator summary 47 passed, 0 failed, but transcript reports setupProcessing errors at 1234.568 and 1234567.800 Hz in both precision suites; normal 22050 through 384000 Hz and two fractional rates accepted. Preserve these errors; do not claim clean all-rate qualification. Mono unsupported by design. Windows build is the original 0.1.0, not this oversampling module. Local git SDK retrieval remains DNS-blocked; no substitute. Next: repair unusual-rate contract or explicitly qualify refusal, then integrate fixed-latency oversampling with versioned quality state and safe switching policy. No new paid resources, workflows or shared manifests.
