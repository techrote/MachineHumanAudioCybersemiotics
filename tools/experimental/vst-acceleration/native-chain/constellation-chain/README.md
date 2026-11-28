# ACCEL-047 — Constellation memory shuttle

Refs #632, #738, #748; creative performance interpretation of draft #265 (56c107f8f4147316a588484c47be28bc8f840fbb) and #423. Not a formal general solver, perception study, VST3 host test, or mainline integration. No plugin, class/parameter IDs, states, shared workflows or existing qualified artifacts changed.

## Exact dependencies

Obtain the following native header directories at these exact refs (no branch-tip substitution). Only the 13 header files listed in verify_sources.py are required. The CMake configure step rejects mismatched Git blob identities. Use a clean directory containing only those files; reconfigure after any changes.

- ORBIT_DIR: #739 at 646d1f4dadd4ded55b3c4f681e94856923611445, tools/experimental/instrument-foundry/orbit-lantern-738/; Orbit Lantern 0.4.0 Windows run 46110904795 artifact 15249403545.
- BANK_DIR: #749 at b858c94f165dcc2c59e193b51e5e6a73de96cbfc, tools/experimental/signal-foundry/counterfactual-resonator-748/; Harmonic Memory Bank 0.3.0 Windows run 46115417655 artifact 15251347207.
- SHUTTLE_DIR: #633 at b5f509eb5c857dc6e411a7718bdc40dfa09bb0ad, tools/experimental/vst-acceleration/native-chain/palimpsest-shuttle/; Shuttle 0.2.0 Windows run 46106434543 artifact 15248002499.

SDK not linked in this native test. Retain official v3.8.0_build_66 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and the seven recursive pins in Orbit SDK-LOCK.txt. The latest Bank job 140888031477 logs confirm the root and all seven checkout SHAs; tag CMake blob matches the pinned root. No substitute SDK used. Preserve upstream notices when redistributing.

## Build and audition

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DORBIT_DIR=/path/orbit -DBANK_DIR=/path/bank -DSHUTTLE_DIR=/path/shuttle
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
mkdir -p audio
./build/constellation_chain audio
```

On Windows multi-config builds the executable is typically build/Release/constellation_chain.exe. Python 3 is needed only for source verification. Audio output is six original 5-second 48 kHz stereo PCM16 WAVs (including dry reference); final 50 ms fade and initial 10 ms fade applied only during export. No DAW or subjective listening performed.

## DAW routing and score

Split Orbit Lantern stereo output into a dry bus (linear gain 0.4) and an effect send (gain 8, hard clamp +/-0.9, then Bank at 100% wet, then Shuttle, then linear return gain 0.35). Sum the dry and return buses. The hard clamp is an explicit native fixture stage, not an intrinsic plugin setting. Use low monitoring levels; Bank can persist indefinitely. Reset/reinstantiate between cases. Disable automatic plugin bypass on silence. This is a routing recipe, not a validated DAW project; native numerical matching is not promised in other hosts.

Orbit patch Glass Constellation: blend 180/1000, release 650 ms, cents -12, mode 2, spectral depth 700/1000, sustain depth 900/1000, cycle 1400 ms. At 0 s notes MIDI 45,52,59,66 velocity 0.8; at 0.75 s all off. Note 69 velocity 0.7 at 3 s, off at 3.5 s. Bank: frequencies 110/165/220/330 Hz, gain 800/1000, peak mix 1000/1000, selectivity 0, all Capture on, Erase and Discard-on-close off. Wet 1000/1000, bypass off. Shuttle: wet 650/1000, reverse 850/1000, feedback control 200/1000 (actual 13%), stereo cross 400/1000, bypass off, initial stagger 0.

At 1 s close all four Bank Capture controls (IDs 2014, 2023, 2032, 2041). Set Bank budget (2054, normalized budget/16) and objective (2055, count=0 or energy=1) before playback. At 2 s raise Admit Budget (2056) then lower one sample later; set Shuttle stagger (ID 5) at 2 s. Modes: persistent budget 0/count/stagger 100%; count budget 4/count/100%; energy budget 4/energy/100%; full budget 16/energy/100%; aligned budget 4/energy/0%.

## Executed evidence

GCC optimized and Clang ASan/UBSan: 4,702,500 paired stereo frames per compiler across 44.1, 48, 96 kHz, 5 configurations, block sizes 1 and 257. Exact per-stage agreement including Bank host versus direct core; finite bounded samples, final synth voices released, full Bank erasure exact digital zero by 2.5 s. Six WAVs byte-identical between compilers. CMake Release CTest 1/1. Modified pinned header rejected. Initial GCC misleading-indentation error corrected without dropping warnings-as-errors.

At 48 kHz (2.5–3 s window): persistent output RMS 0.0117343, budget 4 RMS 0.00938395, full RMS 4.31e-8 (Shuttle residual, not Bank persistence). Matched energy budget 4 side RMS aligned 0.00424868 versus staggered 0.00653456. Both objectives select mask 2 and cost 4 at all three tested rates: a useful negative contrast, not a demonstration of general objective equivalence. See FX-011V for a different excitation fixture where objectives diverge. Full mask 15/cost 16 in all three rates.

Offline harness allocations are outside plugin callbacks; no claim of real-time chain performance, new binary, desktop DAW compatibility, independent review, or human evidence. No new CI workflow. Preserve #819 frozen mainline inventory and its independent qualification gate.
