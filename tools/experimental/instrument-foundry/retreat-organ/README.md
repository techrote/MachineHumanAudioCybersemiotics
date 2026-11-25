# MHAC Retreat Organ 0.1.0

Refs #510; direct relay realization of [#365](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/365) at 8054d306ce926b7102ba36ebbbc05d874c8188c6, Model and Result B, with a creative carrier/ring-modulation mapping. Not human evidence or a physical magnetic model. The Signal Foundry's Retreat Shaper uses the same mathematical construction for audio attenuation; this is an independent note-driven generator, not a dependency on that branch.

## Play and automate

16 voices, MIDI note on/off, velocity and event tuning, rejected excess notes (no stealing); free-running timing, no tempo synchronization. Each note starts with both eight-relay banks off. Path and interval are captured at note-on; Dial (manual only), Blend and Gain apply live. A full 0–16–0 excursion gives the same total mass for the two banks; a nested 0,15,1,14,2,...,9,7 excursion ends with A=7/8 and B=0. The last level holds until note-off. Each note has its own trajectory and phase. A mass of zero retains a quiet fundamental, while increasing mass morphs toward inharmonic ring sidebands at 0.5 and 2.5 times note frequency. Fixed gain bound ±0.5 FS, 5 ms full-scale slews, 20 ms release, zero latency, 21 ms declared tail, no input bus, mono or dual-mono stereo, float32/64 adapter, no transport dependency. Sidebands are attenuated together near Nyquist; no claim of strict alias-free time-varying modulation.

| Parameter ID | Normalized | Meaning |
|---|---|---|
| 400 | 0, .5, 1 | Manual, Major, Nested |
| 401 | 0–1 (17 steps) | Manual level 0–16 |
| 402 | 0–1 | A to B bank blend |
| 403 | 0–1 | 25–200 ms step interval |
| 404 | 0–1 | Gain |

Patches (Path, Dial, Blend, Interval, Gain): Nested A (1,.5,0,0,.7); Nested B (1,.5,1,0,.7); Major witness (.5,.5,0,0,.7), compare Blend=1; Manual performance (0,0,0,.3,.7), automate the dial through the nested trajectory while holding a chord, then sweep Blend. Play sustained MIDI 48 or chord; single-note levels are intentionally conservative. State RO01 stores five normalized values as fixed-point little-endian integers; sounding voices and memory are not serialized. Host-native editor. No sustain pedal, pitch bend, MPE, custom GUI or host sync in 0.1.0.

## Build and audition

From this directory, CMake 3.25+, C++17: `cmake -S . -B build`, `cmake --build build --config Release`, `ctest --test-dir build -C Release --output-on-failure`. Run organ_test --render from a writable directory to write four original 48 kHz PCM16 mono files; names overwrite existing files. Compare major A/B (exact same PCM) and nested A/B (different PCM); all use MIDI 48, velocity .9, 25 ms steps, note off at 1.1 s, 1.2 s observation. No per-file normalization. The events test compares manual and autonomous trajectory rendering across five block partitions; it is not a host adapter test.

For VST3, clone official https://github.com/steinbergmedia/vst3sdk.git at tag v3.8.0_build_66, run git submodule update --init --recursive, require root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and clean recursive gitlinks. Configure with -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/sdk/path; build Release target MHACRetreatOrgan. On Windows use -A x64 with a Visual Studio generator. The scoped Windows workflow runs SDK validator and packages the standard bundle with SDK notices. Copy the complete MHACRetreatOrgan.vst3 folder to C:\Program Files\Common Files\VST3 and rescan; Linux/macOS builds are intended, not validated. No VST2 or alternative SDK. Retain SDK notices and do not assign a new license to MHAC. No binary is claimed until the exact-source qualification workflow succeeds.

## SDK lock

Official tag resolved to root above via GitHub connector on 2026-11-25. Root commit diff explicitly confirms six updated gitlinks; the complete seven-entry list below was read from the previously qualified Reset Choir package. Root pin plus recursive status and cleanliness checks enforce recorded gitlinks; new workflow records actual checkout and dependency notices.

- base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206
- cmake de6e54eeaaab35b7145f5c32c279b5e892146e04
- doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4
- pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c
- public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95
- tutorials 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34
- vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c

See QUALIFICATION.md for executed tests and limitations.
