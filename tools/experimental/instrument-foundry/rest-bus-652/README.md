# Rest Bus 0.1.0 — playable silent-state clock laboratory

Refs #652, #326 and [PR #327, pinned source](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/bd05772a3b0c98ae80e78e39a1c0ee36281ef387/research/expeditions/rest-rewrites-instrument/README.md), sections 3–4. The five-state discrete clock directly realizes the restricted finite selector. Polyphony, note-relative pentatonic offsets and audio envelopes are creative musical extensions. No new theorem, human evidence, independent review or production communication claim.

## Operation

Call Engine::prepare(rate, secondsPerTick) before use; default clock period 0.3 s, accepted period 0.01–10 s. Quantize to the nearest whole sample. The selector is global and each accepted note latches its offset (0, 2, 5, 7, 10 semitones) at onset, with tuning in cents and velocity 0–1. Eight fixed voices include release tails; extra notes and duplicate held IDs are rejected. Call off explicitly (a future MIDI adapter must map velocity-zero note-on to off). Output is dual mono or single mono, with 5 ms attack and 30 ms release, no autonomous audio or feedback; high frequencies clamp to 0.45 sample rate. Peak bound 0.48 FS. All event calls occur before rendering their intended sample on the processing thread.

Clock::tick counts eligible rendered samples only, never wall time. Four mutually exclusive domains: idle (no held note), held (at least one held note), rendered (every sample), manual (only explicit step). Idle refers to key state, not residual audible release. Changing the domain retains the partial tick and selector, while changing Clock::period clears the partial tick but retains the selector; Engine::prepare and reset clear voices, selector and partial tick, retaining the chosen domain. Manual stepping is ignored in other domains. No transport sync or automatic voice stealing. A sample at the clock boundary advances the selector after rendering, so an onset at the next sample sees the new state. No threading guarantee, persistent state or VST3 adapter in this native milestone.

## Build and reproduce

From this directory, run:

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    ./build/rest_demo

On multi-config Windows generators run build/Release/rest_demo.exe instead. The demo writes four original mono 48 kHz 16-bit WAVs (4.45 s each: 4.4 s score plus 50 ms tail). Each uses identical MIDI pitch 57, four 200 ms held notes, twelve 300 ms gate-closed ticks. Release tails can sound during the first 30 ms of a gap; this is not the original hard-gated PCM.

| Demo | Gap ticks | Selector path |
|---|---|---|
| rest-0 | 12,0,0,0 | 2,2,2,2 |
| rest-1 | 3,3,3,3 | 3,1,4,2 |
| rest-2 | 0,4,4,4 | 0,4,3,2 |
| rest-3 | 3,3,3,3, manual hold | 0,0,0,0 |

## Qualification, 26 November 2026

GCC 14.2 Linux x64 C++17 Release, -Wall -Wextra -Werror, CTest 2/2 PASS. Both tests also passed ASan/UBSan. Main regression 222321 assertions, eight sample rates (1 kHz–2 MHz), five finite capacity counts (1/35/105/124/125), silence, held gate, all four domains, eight voices, saturation, invalid inputs and exact float32/float64 conversion with variable block partitions. Second regression proves 4800 paired frames remain identical after changing the manual selector mid-note, subsequent notes differ, and idle counts while release is audible but not while any key remains held. All four WAVs repeat byte-identically on this build and last 10 ms are digital zero. No physical listening or CPU deadline qualification.

Source base main 495a98ca12bae467a507031f04931aa4254b1866. Native source/build blob identities: rest.hpp 162b095775bb27cc6a4a0a6b790ad2c7e95aa212; test.cpp e89e14407af4c9d58b19a6da26a5f23eeea7199f; demo.cpp 39f256592df58e257cb5356c0f6a9740e950c81c; CMakeLists.txt 479e52645c87afe9dba271c30458942b538a2136; clock_audio_test.cpp f2199b6e912d399888ca5930447e0bbc7d40c9d8. Tested locally and matched remote readback.

## Next gate

SDK-independent engine only. Local GitHub DNS unavailable; no SDK checkout or substitute used. SDK-LOCK.txt pins the exact required upstream release and seven submodules. Add an isolated VST3 processor/controller using the existing instrument lane pattern: stable class/parameter IDs, sample-offset note/automation dispatch, versioned clock/patch snapshot contract, host reset and transport policy, mono/stereo negotiation, CPU budget and exact Windows validator. Preserve the clock/audio distinction; never treat idle duration as evidence of intent. No shared registries, frozen protocols or sibling branches changed.
