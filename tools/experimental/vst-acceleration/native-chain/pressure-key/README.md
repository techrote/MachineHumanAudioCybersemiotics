# ACCEL-050 — Pressure / Key Constellation

Refs #632, #738/#739, #748/#749. Creative native integration of per-note finite-orbit morphing and budgeted erasure, not a new formal result, human evidence, SDK-host qualification or independent review. Keep the previously qualified original ACCEL-048 chain unchanged.

## Reproduce

Copy only the exact headers in DEPENDENCIES.txt into a separate Dependency root (Orbit, Bank, Shuttle). Orbit files are under tools/experimental/instrument-foundry/orbit-lantern-738 at the listed commit; Bank under tools/experimental/signal-foundry/counterfactual-resonator-748; Shuttle under tools/experimental/vst-acceleration/native-chain/palimpsest-shuttle. Verify git blob IDs before building. No SDK sources are needed. Preserve the existing Steinberg 3.8.0 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and seven recursive pins in the respective plugin branches; no substitution.

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DDEPENDENCY_ROOT=/absolute/dependency/root
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    mkdir audio
    ./build/pressure_key audio
    python make_score.py audio

For multi-config Windows use build/Release/pressure_key.exe. Windows native compilation of this chain has not been executed.

## Performance

Orbit patch blend 180, release 650 ms, cents -12, release mode 2, spectral depth 700, sustain depth 900, sustain period 1400 ms. Dry bus gain .4; separate effect send gain 8 clamped to +/- .9, Bank wet 100%, four bands 110/165/220/330 Hz each gain 800/1000, peak mix 1000/1000, selectivity zero. Close all Capture controls at 1 s; send an independent stereo key (right channel only, four 10 ms pulses at 1.5, 1.53, 2 and 2.5 s) to Erase key, never to audible output. Set energy-first objective and budget 4 or 16. Disable auxiliary key for no-key controls. 1.53 s onset should be suppressed. Shuttle wet 65%, reverse 85%, feedback control 20%, cross 40%, stagger 100%. Return gain .35. Reset each plugin before a run.

MIDI score uses original notes 45/52/59/66 at 0 s, off at .75; note 69 at 3 s, off 3.5. Polyphonic pressure 45 at .25 s, 59 at .5, 69 at 3.25. MIDI rounds float velocity/pressure to 7 bits. DAW must actually forward poly pressure and support auxiliary input. Native renderer uses exact float velocities and pressure. Do not monitor the key track (0.8 FS). Keep output monitoring gain low; persistent memory may continue beyond the 5 s export. Four comparisons: baseline, pressure alone, pressure plus budget-4 key, full erasure. Six stereo PCM16 WAVs, 48 kHz, 5 s. No listening judgment.

## Executed evidence (28 Nov 2026)

GCC 14.2 Linux Release with -Wall -Wextra -Werror, Clang ASan/UBSan and CMake/CTest 1/1 PASS. 12 rate/mode cases, 36 native executions, 7,524,000 paired stereo frames per compiler for two reference comparisons per case; dry, bank and mix sample-exact between 1/257-frame keyed blocks and explicitly scheduled 1024-frame manual admission. Final voice count zero, saved configuration exact, finite bounded output, maximum-budget Bank exact silence after 2 s. Six generated WAVs byte-identical across compilers. At 48 kHz, Bank RMS 2.75–3 s: pressure/no key .0625061, pressure/key .0244736, full 0; dry .024587 baseline vs .0285696 pressure (0.25–0.75 s). Not a perceptual assessment.

Latest individually qualified Windows artifacts: Orbit 15268476929 (run 46158137235), Bank 15268772488 (run 46158563142), Shuttle 15248002499 (run 46106434543). The new Bank archive outer digest 205cf432490c8b3f3c578f405c1d073d3894f32ac1498224097ff7a7daabadc2, inner 3fd661b3c8c1356b097d10e0ea330fa38567ec032a5becf75886f4d94b8601e3; exact source, SDK root, seven dependency revisions, module and class version 0.4.0 and both CRCs inspected. Actual SDK Bank 128 legacy, 16 budget and 32 key cases passed; validator 47/47. No combined binary replay of these newer versions or physical hardware validation claimed. Mergedown retains #819 frozen inventory and independent promotion authority. Next: actual SDK-host chain with pressure queue and active auxiliary bus (not Pedalboard-only parameter segmentation).
