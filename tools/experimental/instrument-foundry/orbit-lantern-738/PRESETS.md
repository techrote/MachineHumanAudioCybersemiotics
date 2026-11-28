# Orbit Lantern — INST-011C preset bank and Windows qualification

Refs #738; research origin #264 / #265 at 56c107f8f4147316a588484c47be28bc8f840fbb. Creative interpretation of persistent lattice orbits, not the original escape compiler or human evidence. Resumes adapter head fe8936830e6d099fc874ce2a54af64a7e428d9c0.

Eight original component-only VST3 preset candidates; 86 bytes each: 48-byte header, ten-byte OL01 state, 28-byte chunk list. Exact processor FUID 24C15B793B8C4F4B98275F233EE969C4. Format checked against official pinned public.sdk source/vst/vstpresetfile.cpp (writeHeader/writeChunkList) and pluginterfaces base/funknown.cpp (FUID::toString). No state, parameter, DSP or adapter changes. Reader is intentionally restricted to the canonical generated subset, not a general third-party parser. Actual DAW preset import not performed.

Build with the native CMake instructions in HOST.md; run orbit_preset_bank <preset-dir> <audio-dir> to write the eight patches and eight original 3s stereo 48 kHz PCM16 recordings. With no arguments runs the same regression without writing files. All recordings use overlapping C3/G3/D4 note events and velocities 0.8, final 50ms exact silence. Patch settings are note-latched. Quarter/Interference/Persistent compare blend alone; Needle uses 10ms release, Slow Ember 850ms and -25 cents, Offset Halo 400ms and +25 cents, Hollow Fifth -100 cents, Bright Return +100 cents. No listening claims.

Native evidence 2026-11-27: GCC 14.2 optimized warnings-as-errors including -Wshadow, Clang 17 ASan/UBSan, both PASS: 9009 roundtrips, 640 rejected container/magic mutations, 1152000 exact paired stereo frames, safe amplitude bounds and release silence. Tests used orbit.hpp Git blob 4f85b153f3391a99e18005407c78ef17a8ea6579, exact match to predecessor. Same-agent checks. Official SDK tag and seven dependency commits re-resolved via GitHub, inherited recursive lock; direct Git checkout DNS blocked. SDK ABI not tested locally. No substitute SDK.

New path-scoped Windows workflow derived from the qualified Afterimage workflow at 5a53f8b5a2b41ddf3ccab4396b004c8ecfb8e549; one Windows x64 runner, existing lock checks in VST3.cmake, strict official validator, notices, source receipt, presets and audio. No shared workflow modified. Windows build and validator must actually succeed before any new binary is described as installable. Actual host, preset import, deadline and independent review gates remain. Draft/HOLD.

## INST-011M — spectral release (0.3.0 candidate)

Parameter 1814 is a stepped 0..1000 spectral-depth control (default zero). It is sampled at note-off for fixed and phase-conditioned releases; linear mode ignores it. Existing releases do not change when this control is automated. OL03 adds a little-endian uint16 depth to OL02 (13 bytes, 89-byte preset); OL01/OL02 still serialize identically when depth is zero. Older plugins cannot read OL03. Three new original patches 12 Fixed Spectrum, 13 Phase Spectrum and 14 Half Spectrum share the existing matched score. The native utility writes all fourteen presets and recordings. Use the existing exact SDK 3.8.0 workflow; do not install a source candidate as a binary. Actual DAW load/preset import, modulation sideband and deadline qualification remain outstanding. Ref #738; creative synthesis interpretation of draft #265, not human evidence.

## INST-011V — Constellation performance bank (0.4.0)

Five additional component-only presets use the same existing qualified 0.4.0 interface; no DSP, SDK, class ID, parameter ID, state or version changes. Refs #738; creative synthesis interpretation of #265 at 56c107f8f4147316a588484c47be28bc8f840fbb, not human evidence.

| Preset | Blend (permille) | Release (ms) | Cents | Release mode | Spectral depth | Sustain depth | Cycle (ms) |
|---|---:|---:|---:|---|---:|---:|---:|
| 18 Glass Constellation | 180 | 650 | -12 | Phase | 700 | 900 | 1400 |
| 19 Tidal Pedal | 700 | 900 | 0 | Fixed | 250 | 1000 | 6000 |
| 20 Flicker Choir | 550 | 180 | 12 | Phase | 800 | 800 | 320 |
| 21 Still Constellation | 180 | 650 | -12 | Phase | 700 | 0 | 1000 |
| 22 Long Arc | 1000 | 1000 | 0 | Phase | 1000 | 1000 | 8000 |

Run the existing orbit_preset_bank generator with preset and audio directories. It now emits 22 presets, 22 WAVs and an original Constellation Score.mid (format 0, 120 BPM, 480 PPQ, 14 paired notes, four simultaneous held notes maximum). Import the MIDI into a DAW instrument track, load a matching preset, and set tempo to 120 BPM. Presets 18 and 21 form a matched sustain-on/off comparison. The other three explore different cycle/release combinations. New WAVs are eight seconds, 48 kHz stereo PCM16; native renders are not DAW captures. The previous 17 recordings retain their three-second score. No listening assessment.

Linux Release CTest 11/11 PASS; GCC Release and Clang ASan/UBSan preset generators both passed 66,032 roundtrips, 3,741 rejected mutations and 4,368,000 exact paired stereo frames. All 34 previous WAV/preset files are byte-identical; all 45 current generated files are byte-identical across the tested compilers. A separate local parser verified MIDI header, track length, tempo, note lifetimes and end tick; all five new WAVs have exact final 50 ms silence. Windows packaging and actual DAW preset import remain unverified for this new bank. Existing qualified 0.4.0 binary remains the intended audition target.
