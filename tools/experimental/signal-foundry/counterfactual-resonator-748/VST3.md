# FX-011C — Counterfactual Resonator VST3 candidate

Refs #748 and pinned draft #265 (56c107f8f4147316a588484c47be28bc8f840fbb). Creative DSP interpretation, not a general escape solver or human evidence. Previous README and HOST-BRIDGE describe the original native stages; this document supersedes their build and sample-rate status.

The adapter preserves CR01 (12 bytes), assigns IDs 1900–1906 as in HOST-BRIDGE, and uses the existing lock-free state mailbox. It accepts matched mono or stereo buses, Float32/64, and ordered sample-offset parameter queues with step admission; the DSP smooths wet, gain and monitor. Zero-sample calls flush parameters, absent inputs excite with zero, and output silence flags reflect actual samples, not input silence. No-output calls advance zero-driven state. Pulse is rising-edge/coalesced; it is not saved. The undelayed dry path reports zero fixed latency, not a frequency-independent wet group delay. Tail is always reported as infinite because nearest rounding can sustain indefinitely, including after input silence. Use Erase or reset to stop a persistent tone; begin audition at low monitor volume. Host parameter view uses normalized values with range labels.

Native rate admission now covers finite 1 kHz–2 MHz, retaining fractional rates; nominal pitch is still capped by sample rate / 16. Nine rates were tested against direct DSP over two block partitions, including 1234.568 and 1234567.8 Hz. At 2 MHz/40 Hz, floating phase accumulation can place the first tick one frame after the ideal integer boundary (initial strict 12500-frame assertion failed); the test allows 12501 frames. No exact rational-clock claim. A long accumulation and zero-drive erase witness passes. Invalid rates preserve existing state. Existing eight WAVs and four CR01 patches reproduce byte-identically. The excitation dead zone is unchanged.

Build native tests with CMake as before. For VST3 use CMake 3.25+ and a clean recursive checkout of the exact SDK:

```sh
git clone --branch v3.8.0_build_66 --recursive https://github.com/steinbergmedia/vst3sdk.git sdk380
cmake -S . -B build-vst -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/path/to/sdk380 -DMHAC_VALIDATE_POST_BUILD=OFF
cmake --build build-vst --config Release --target MHACCounterfactualResonator validator
```

Run the built official validator against the complete bundle, requiring zero failed tests and zero explicit ERROR lines. Retain the SDK notices and exact source/SDK checkout receipt. The dedicated Windows workflow performs these steps and packages only after the gate. Once qualified, copy the complete bundle into C:/Program Files/Common Files/VST3 and rescan. Native CR01 files are not standard VST3 presets; DAW preset import remains untested.

GCC 14.2 Release and Clang 17 ASan/UBSan Debug CTest each 3/3 pass, including 1,187,765 host assertions. Local missing-SDK configuration fails closed; local GitHub DNS prevents SDK checkout, so this adapter has not been locally compiled or validated. Windows/macOS, actual DAW, callback timing, and independent review remain outstanding until real evidence. Two candidate class IDs are distinct from the 42 existing IDs in the supplied collections; compiled IDs still require verification. Same-agent implementation and checks, no subjective listening. Draft/HOLD.
