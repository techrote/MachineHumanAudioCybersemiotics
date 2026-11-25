# MHAC Freeze Socket — 0.1.0 research prototype

Refs #437; origin: [#422](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/422) / [PR #423, pinned report](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/03e3f121fbb2362d76db4d6cd597d27ae087ea8b/research/expeditions/metaphor-becomes-socket/README.md). The finite transport, latch and snapshot contracts are directly realized; mapping them to a four-step attenuator is a creative audio interpretation. This is not a spectral/waveform freeze or a validated human interface. No canonical records changed.

**Status:** The parent source `fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2` passed Windows x64 SDK 3.8.0 build and official validator (47/47); [parent artifact](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45534581573/artifacts/14986731404). This clock-corrected follow-up (#466) has native Linux regression evidence in [CLOCK-QUALIFICATION.md](CLOCK-QUALIFICATION.md); its own Windows build/validator and DAW audition are still required. Do not attribute the parent binary to this revision.

## The effect

Place the effect on a sustained chord, pad, noise, or drum bus. Four editable amplitude steps form a free-running modulation sequence. The Hold switch changes which subsystem continues to evolve:

| Contract | Output while held | Transport | Edits during hold |
|---|---|---|---|
| Output latch | Captured single step value | Continues | Live bank changes; hidden until release |
| Transport pause | Current step of live bank | Stops, including fractional phase | Edits of that step are immediately observable |
| Bank snapshot | Steps from captured bank | Continues | Live bank changes; hidden until release |

All three modes coincide at the instant of capture. When changing mode while held, recapture from the current live bank at the current phase. Release reads the live bank without resetting phase. Apply all same-offset parameter changes before capture/render. Clock advances after the sample. Wet, depth and bypass continue to operate regardless of hold. Bypass does not reset the clock.

## Controls and audition recipes

Stable normalized IDs 100–109: Rate, Depth, Mix, Freeze contract, Hold, Step A, B, C, D, Bypass. Rate is logarithmic: 0.25 * 2^(6 * normalized), expressed as steps per second, not cycles per second; default 2 steps/s. Mode 0/0.5/1 selects latch/pause/snapshot. Hold and Bypass use threshold 0.5. Other controls are linear 0–1. Host-native parameter editing is the intended UI. No custom editor or DAW sync in 0.1.0.

Start with Rate .5, Depth 1, Mix 1, bank [.15,.45,1,.25], Hold 0, Bypass 0. Play a sustained source and engage Hold at 1.125s. Edit A to .95 at 2s and C to .1 at 2.25s; release at 3.25s. Duplicate the track into three parallel channels and use different modes for a clear A/B/C comparison. Do not sum the tracks at full gain; monitor them separately or attenuate each lane.

Other patch ideas: bank [1,0,1,0] for alternate rhythmic gating; [1,.8,.6,.4] for a descending staircase; [.5,.5,.5,.5] as the negative control that conceals the contracts until edits.

The shared control gain is 1 - Depth * Mix * (1 - token), or 1 for bypass. It is linearly slew-limited at 200 units/s (full-scale transition <=5 ms), clamped 0–1, with no positive gain boost or generated audio. Float and double input sanitization converts nonfinite/subnormal values to zero. Wet/dry are combined into one effective gain because this processor has no phase shift or delay. Latency and tail are zero. Mono and stereo matched layouts are requested; channel gains are identical, no interchannel mixing. Samples are not hard clipped; valid overs from upstream stay overs during bypass. Ramp transitions can still produce desired modulation sidebands; not a guarantee of perceptual clicklessness.

Automation adapter processes each valid queue point at its sample offset, with step-held parameters and final gain smoothing; no interpolation between host points in this version. State is a 48-byte MHFZ version-1 payload: ten little-endian 32-bit normalized millionths, strictly checked before applying. Presets restore parameters but restart transport and capture from phase zero. Class IDs are fixed in plugin.cpp. No runtime dependency on other MHAC branches.

## Build and render the tested DSP

From this directory (CMake 3.25+, C++17 compiler):

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
# Linux/macOS single-config generator:
./build/freeze_test mode-
# Windows Visual Studio generator:
# build\Release\freeze_test.exe mode-
```

The optional argument is a filename prefix, producing mode-0.wav, mode-1.wav and mode-2.wav: three original 5-second stereo 48 kHz PCM16 renders from an identical additive sine carrier and timed gestures. No third-party audio assets. See [qualification receipt](QUALIFICATION.md).

## Native VST3 build (parent qualified; follow-up requires requalification)

Use the official SDK only. The CMake guard requires a clean checkout of the exact release commit and all recursive gitlinks. Do not substitute a floating tag or SDK from a framework.

```sh
git clone https://github.com/steinbergmedia/vst3sdk.git vst3sdk
git -C vst3sdk checkout --detach 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0
git -C vst3sdk submodule update --init --recursive
git -C vst3sdk submodule status --recursive
cmake -S . -B build-vst -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/path/to/vst3sdk -DCMAKE_BUILD_TYPE=Release
cmake --build build-vst --config Release --target MHACFreezeSocket
```

For Windows x64, configure with `-G "Visual Studio 17 2022" -A x64` and the absolute SDK path. CMake requests the SDK validator when its target is available. Check actual validator exit status; if not invoked, build its target and run it on the generated bundle. SDK sample plug-ins and VSTGUI are disabled; no symbolic link installation requested. The core-only build needs no SDK.

Expected distribution (once built/verified): copy the complete generated MHACFreezeSocket.vst3 bundle, including its Contents hierarchy and SDK license resources, into the DAW's VST3 scan location (Windows typically C:\Program Files\Common Files\VST3; macOS ~/Library/Audio/Plug-Ins/VST3; Linux ~/.vst3 where supported). Rescan. Do not copy an inner shared library alone. Zip the complete bundle with this document, verified build receipt and applicable third-party notices. There is no qualified bundle to install yet. No code-signing or redistributable licensing decision has been made.

## SDK lock and rights

Steinberg official tag v3.8.0_build_66 resolves to [9fad9770f2ae8542ab1a548a68c1ad1ac690abe0](https://github.com/steinbergmedia/vst3sdk/commit/9fad9770f2ae8542ab1a548a68c1ad1ac690abe0), CMake project version 3.8.0. The release commit diff records base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206; cmake de6e54eeaaab35b7145f5c32c279b5e892146e04; doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4; pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c; public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95; vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c. Tutorials did not change in that diff. The immutable root commit and recursively committed gitlinks pin all dependency revisions (including unchanged/nested links); CMake refuses missing, moved or dirty dependencies. Full recursive checkout verification remains unexecuted because of DNS. Record the actual recursive status output at the first native build.

Read official tag CMakeLists.txt, .gitmodules and LICENSE.txt through GitHub, plus SDK example processor/controller/factory and CMake excerpts at the pinned public SDK commit. The SDK release uses MIT; retain its full copyright/license notice and applicable nested third-party notices with redistributed binaries. CMake includes the root license as a bundle resource. No SDK source copied into this repository, no logo, no new license granted for MHAC code. Source inspection does not establish ABI compatibility.

## Remaining qualification

Native SDK checkout, Windows x64 build, validator, actual mono/stereo float/double DAW or test-host processing, sample-accurate queue and zero-sample flush verification, state/automation/bypass/load checks, portable ZIP, host-independent code review and exact-head repository checks. Host-level concurrency, lifecycle and parameter display need independent scrutiny. Target Linux and macOS subsequently. The test suite covers the control engine, not the VST3 bus/stream API. Treat the adapter as Draft/HOLD until validated.

## Windows build recovery (qualification candidate)

The scoped Windows workflow `.github/workflows/mhac-freeze-socket-windows.yml` uses one standard Windows 2022 runner, exact PR HEAD, the pinned SDK, Release native tests, a native bundle build, and a **mandatory** standalone official validator run. It preserves the validator transcript, root and recursive gitlink receipts and packages the full bundle only after all checks succeed. The separate validator step is not a bypass. The accepted rate range is now 1,000–2,000,000 Hz (finite fractional rates included), shared by core and adapter, to cover the unusual high-rate SDK stress case observed in instrument-lane CI run 45531129635. No parameter/state format or ordinary audible behavior changes intended. See the run and receipt for actual qualification, not this description.
