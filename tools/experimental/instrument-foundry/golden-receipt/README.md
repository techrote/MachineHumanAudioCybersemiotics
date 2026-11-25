# MHAC Golden Receipt 0.1.0

Experimental VST3 instrument source and standalone C++17 pulse-motif generator. Refs #446; research #428 / draft #429 at 07fb2f67a5a2cf26312699410f00152033cae843. The source expedition is not accepted empirical research. This is a direct implementation of its normalized timing fingerprints, with a creative sine-pulse audio mapping, not a human perception or priority claim.

## Musical behavior

Each note starts an independent one-shot motif; hold the note until the last pulse has sounded. Four equal-amplitude, phase-reset sine pulses encode the selected timing shape. Deleting an onset removes it and positively affine-normalizes the remaining first and last onset to the same span. Golden intervals (phi,1,phi) yield normalized interior positions 1/phi^2 or 1/phi after deletion. First/third deletions are the same waveform, as are second/fourth, at identical settings and note events. The renderer deliberately uses the exact same floating-point expression for each alias class before integer sample rounding; this is a faithful symbolic implementation, not proof that physical recordings remain indistinguishable.

| Parameter ID | Default normalized | Interpretation |
|---|---:|---|
| 200 Shape | 0 | Golden or equal gaps |
| 201 Missing onset | 0 | None, first, second, third, fourth |
| 202 Span | 0.4 | 0.2–1.5 seconds from first to last onset |
| 203 Width | 0.5 | 15–80 ms raised-sine-squared pulse |
| 204 Gain | 0.7 | Smoothed master gain |

Shape/deletion/span/width are captured at note-on; gain affects all existing voices with a 5 ms full-scale slew. 16 fixed voice slots, no hard stealing: excess note-ons dropped. Note-off releases the matched voice over 10 ms; if note ID unavailable, release all matching channel/pitch voices. Note-event tuning supported (limited to +/-1200 cents, frequency capped at .45 sample rate); no pitch-bend, sustain, host-clock sync or MPE yet. Mono/stereo dual mono, no audio input, no network, no custom GUI. Zero latency, conservative 1.59 s tail. Rational soft-bound of the sum limits output to 0.5 FS before master gain; single notes intentionally have substantial headroom. The standalone DSP is allocation-free per sample and bounded by 16 voices x 4 pulses. Parameter snapshots and note identities are ephemeral; versioned GR01 state serializes five Q24 normalized parameters only.

## Preset recipes (not VST preset files)

- Golden witness A: Shape=Golden, Missing onset=First, Span=.4, Width=.5, Gain=.7; A4 velocity .9, hold at least .8 s.
- Golden witness A': same, Third. Identical audio with no other voices.
- Golden witness B/B': Second/Fourth, all else identical.
- Equal control: Equal gaps, First; compare Second (different interior onset).
- Chord clouds: Golden, None, Span=.65, Width=.85, Gain=.7; stagger a C minor triad, allow at least 1.2 s before note-off. Untested musical recipe, not a listening result.

## Build and audition

Native core requires only C++17 and CMake >=3.25:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

Create a demos directory and invoke golden_test with the directory as its sole argument (Windows multi-config executable typically build/Release/golden_test.exe). It writes six 48 kHz 16-bit dual-mono WAVs of 1.7 s each using the native DSP. No plugin host needed.

SDK pin: official Steinberg vst3sdk tag v3.8.0_build_66, commit 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. The pinned root's CMakeLists declares 3.8.0; the same file is accessible at the named release tag. Recursive dependency versions are locked by the committed gitlinks, never by latest branch heads. No SDK source is vendored. Build must fail for missing/wrong root commit, uninitialized/divergent recursive submodules or dirty checkout. Package original SDK LICENSE.txt with any plugin and retain applicable third-party notices; audit the actual linked dependencies before redistribution.

```sh
git clone --recursive https://github.com/steinbergmedia/vst3sdk.git sdk-380
git -C sdk-380 checkout --detach 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0
git -C sdk-380 submodule update --init --recursive
git -C sdk-380 submodule status --recursive
cmake -S . -B vst-build -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/path/sdk-380 -DCMAKE_BUILD_TYPE=Release
cmake --build vst-build --config Release --target MHACGoldenReceipt
```

On Windows with Visual Studio use an x64 generator (-A x64 for VS). Preserve the entire generated .vst3 bundle and install to the host's scanned VST3 path (Windows commonly C:/Program Files/Common Files/VST3); rescan and insert on an instrument track. These plugin build/install instructions are proposed and not yet executed. Native adapter source targets SDK 3.8.0 but is uncompiled. No DAW compatibility, validator success or distributable binary claimed. See QUALIFICATION.md.

## Follow-up

Build native SDK on Windows x64 and Linux, run official validator and real host note/event/automation/state and CPU tests; verify notices and exact recursive gitlinks in build receipt. Add richer timbres only behind an explicit experimental mapping parameter so the equal-pulse baseline survives. Do not change shared manifests or integrate until review and exact-head checks.
