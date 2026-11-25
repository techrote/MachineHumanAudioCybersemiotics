# Phase Cycle Prism Live — FX-006B

Refs #576, #568, #569 and research #297 (research head c66c128ae550aadd16a46ddc7559406dbbc65be9). Stacked on FX-006A at 305532cccac26e7d04aaff26e2af15962a1d6ac6. Direct realization of virtual phase-cycle coefficient cancellation; the selectable spectral resynthesis effect is a creative engineering extension. No human or psychoacoustic claims.

## Signal contract

Stereo is interpreted as complex I/Q. At 48 kHz the 1x grid uses 400/480/720/800 Hz; 2x uses 800/960/1440/1600 Hz; 4x uses 1600/1920/2880/3200 Hz. The first carrier in each group is absent in the demonstration. The wet path resynthesizes only these four bins; it is not a broadband distortion remover. Cancellation removes the modeled cubic products generated from the captured coefficients, not arbitrary distortion already present in the input. The grid is latched at frame start and the drive/cancellation settings at frame completion. Consecutive coefficient sets, including different grids, are interpolated during output. Wet/gain and bypass slew over up to 5 ms. The sample-offset adapter applies parameter points as they arrive; grid/drive/cancel remain intentionally frame-quantized. No oversampling is implied by the grid labels.

N = max(96, round(sampleRate/80)); grid frequencies are bin * grid * sampleRate/N. Latency N samples and tail bound 3N samples, independent of grid. At 48 kHz: 600 samples (12.5 ms), tail 1800 samples. The additional wet interpolation history is not a pure delay. Rate acceptance 1000–2000000 Hz with Nyquist margin from the 96-sample minimum; unusual rates are engineering test cases, not a claim of DAW compatibility. Prepare allocates the two fixed-size-for-rate vectors outside processing; step uses bounded arithmetic and no allocations/locks/I/O. Input and output protected to ±1 FS. Stereo only; no mono interpretation is claimed.

## Controls and presets

Normalized state PC01: 28 bytes, six little-endian IEEE float parameters following magic. Reject malformed, nonfinite and out-of-range data. This is the first plugin state; FX-006A had no VST state. Stable IDs 900 signed drive (0.5 neutral), 901 cancellation, 902 wet, 903 gain, 904 grid (0/0.5/1), 905 bypass. Defaults .75/1/.5/.5/0/0. Example normalized patches:
- Raw witness: 1/0/1/.7/0/0
- Corrected witness: 1/1/1/.7/0/0
- Upper prism: 1/.5/.8/.7/1/0
- Spectral glaze: .35/1/.35/.7/.5/0
- Protected delayed dry: .5/1/0/1/0/1

## Build and audition

From the parent phase-cycle-prism-568 directory:
    cmake -S live-576 -B build-live -DCMAKE_BUILD_TYPE=Release
    cmake --build build-live --config Release
    ctest --test-dir build-live -C Release --output-on-failure
    ./build-live/prism_live_demo

On Windows multi-config generators use build-live/Release/prism_live_demo.exe. Three original 3.25-second stereo PCM16 demos: grid-dry.wav, grid-raw.wav, grid-corrected.wav. Each one-second segment uses successive 1x/2x/4x grids with identical .18 FS occupied-carrier amplitudes and 10 ms edge envelopes. Final .25 seconds silent input. Wet gain .7; no loudness normalization. Start at low monitoring volume.

Native adapter build requires the official Steinberg SDK tag v3.8.0_build_66, root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. See parent SDK-GITLINKS.txt for the seven exact pins. Clone recursively, keep clean, no substitution. From parent:
    cmake -S live-576/vst3 -B build-vst -A x64 -DMHAC_VST3_SDK=C:/path/to/vst3sdk
    cmake --build build-vst --config Release --target MHACPhaseCyclePrism validator

Windows workflow performs both native regression suites, exact pin validation, Release build, mandatory validator with explicit ERROR rejection, and portable packaging including upstream notices. After qualification, copy the entire MHACPhaseCyclePrism.vst3 directory to C:/Program Files/Common Files/VST3 and rescan the DAW. No installer, online runtime or VSTGUI dependency. macOS/Linux adapter targets intended, not qualified. No new project license granted.

## Verification receipt, 2026-11-25

Linux x64 GNU 14.2 warning-clean C++17 Release: original and new CTest each 1/1 PASS. New test under ASan/UBSan PASS. 90 grid/rate/cancellation combinations, 10 rates from 1 kHz to 2 MHz including the two unusual validator rates; maximum coefficient-oracle absolute error and corrected residual 3.95508e-16 FS. Legacy reference maximum difference 8.25233e-16 FS. Exact bypass impulse, finite tail, partition-independent parameter changes, state roundtrip and corrupt-state rejection, nonfinite/extreme input. Offline processing benchmark 480000 samples took approximately .017–.020 s on local Linux; not worst-case callback certification.

PCM16 coherent target projection over central 0.5 seconds of each one-second segment:
400 Hz dry 1.38234e-7, raw .00816523611, corrected 5.64447e-8 FS.
800 Hz dry 1.29174e-7, raw .00816592104, corrected 1.72246e-7 FS.
1600 Hz dry 3.12707e-7, raw .00816519028, corrected 1.92311e-7 FS.
Remaining carriers about .1464 FS in both wet renders. Three WAV hashes reproduced:
grid-corrected.wav 1ec223a3bc2d37929a2a093686fb5d36c8b55b2f8ca5c112a1072fa4d1ce33ad
grid-dry.wav 1c8242dd4caa4a46494c0f847420aeaebc6eca8fc73707426bbc40a8603eb1fa
grid-raw.wav 5412a31c8fc2ad5fa7b5f441b0e6a7b4385554ccd40bc0f425c3ca608a9ba509

Local Git retrieval blocked by DNS. SDK adapter compilation, actual Float32/Float64 host execution, bus/automation host tests, official validator, actual DAW load and independent review outstanding. Native results are not evidence of a working VST3 binary. Windows CI is the recovery route. No shared registry/workflow or sibling changes. Draft/HOLD.
