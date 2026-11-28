# Guest Organ — native quotation/adoption instrument laboratory

Refs #622 and #460/#461, pinned [source](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/fb3fca1c21213b8520584108c1d65aa1db4b6cd4/research/expeditions/voice-lends-mouth/README.md), Executed miniature and Exaptation. The local adoption bit and delayed countervoice are direct realizations of the miniature's musical rule; note transposition, repeated motif cycles, and polyphonic scope are creative extensions. Citation is explicitly inaudible and does not grant permission. No human evidence, licensing mechanism or production communication system.

## Playing
Call prepare(rate), configure(Patch), on(id, MIDI note, tuning cents, velocity), tick() or process(), and off(id). Configuration is copied per onset; existing notes keep their motif, speed and adoption policy. Default intervals 0,7,3,10 semitones, 4 steps/s, counter gain .65. The base phrase repeats with continuous phase. Adoption enables the reversed motif, octave-up, after one complete four-step cycle; base is unchanged. Cite is an independent local annotation bit with no DSP effect. Left = base; right = base + counter. Frame also exposes independent base and counter values. The first cycle is identical regardless of the two bits. Voice capacity eight; duplicate IDs and new IDs at capacity are rejected (including release tails), not stolen. 5 ms attack/counter slew and <=31 ms release; zero algorithmic latency. Sample rates 1–192 kHz; step duration rounded to integral samples. Oscillator increments bounded to .45 cycles/sample; output absolute bound .52, including eight saturated velocities. No allocations or I/O inside tick/process. Single-thread access required. Host-independent DSP only; no VST3 adapter, state serializer, GUI, real DAW or worst-case timing qualification. No claim of fully click-free output or alias-free arbitrary modulation.

## Build and reproduce
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    mkdir audio
    ./build/guest_demo audio

For Visual Studio generators use build/Release/guest_demo.exe. Four original stereo 48 kHz, 16-bit, six-second WAVs: mode-0 replay, mode-1 cited replay, mode-2 adoption, mode-3 cited adoption. Two pairs of identical sounds by design. Note 48 at 0 s, note 55 at 2 s, releases 4 s and 5 s. Compare first 1 s and full left channel for exact equality. Try motif {0,5,-2,9}, rate 7, gain .35 for faster interlocking phrases; or {0,0,7,3}, rate 2, gain .9 for slower exposed counterpoint.

## Receipt 2026-11-25
Linux x64 GCC 14.2 Release -Wall -Wextra -Werror CTest 1/1 PASS; ASan/UBSan PASS. Six rates, 259400 paired history frames, exact mode equality and first-cycle equality, scope, finite output, capacity, block partition, float/double, mono alias and release. Four repeated WAVs byte-identical; full left channel and first second stereo identical across modes. Original outputs peaks .059998 and .083405 FS, exact final 50 ms silence. No listening or independent review. Tested same-agent implementation. SDK tag and all seven upstream commit identities resolved, matching recovered Three Winters exact SDK recursive checkout; SDK unused by this core, local git DNS failure. For future VST3 integration reuse the exact 3.8.0 build 66 lock, verify all recursive gitlinks/clean checkout and include applicable licenses/notices. No alternate SDK. No shared files edited; full repository CI separate. Draft/HOLD.
