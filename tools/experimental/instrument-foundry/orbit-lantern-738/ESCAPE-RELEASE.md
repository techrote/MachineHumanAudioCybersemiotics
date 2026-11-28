# INST-011G — Intervention-shaped release

Refs #738 and #264; research draft #265, pinned 56c107f8f4147316a588484c47be28bc8f840fbb, Exact model, Exact intervention compiler and Synthetic census. Creative sonification of an exact finite escape witness, not a physical decay model or human evidence.

`escape_release.hpp` is a separate native eight-voice instrument sharing Orbit Lantern's Spectrum, rate admission and OL01 Patch. On note-off, choose a linear or intervention-shaped release. The 60-step nearest/truncation path from (-16,4) to (0,0) uses nine truncations. Its squared radius, normalized by 272 and capped at one, is mapped to amplitude and linearly interpolated across the captured release duration. It preserves oscillator phase and pitch; it does not claim phase-conditioned escape or audio-rate integer feedback. At short durations multiple states may fall between samples. Release mode is event-local, not a new persistent field. Existing VST3 adapter, IDs, presets and DSP remain unchanged. No new binary feature is claimed.

Prepare builds the spectra and route outside the callback. Eight fixed voices, no heap allocation or locking in on/off/tick, bounded Fourier loops, finite input checks, exact silence after release and 0.52 FS per-channel output ceiling. Note-on rejects a full bank, duplicate ID and above-band pitch; repeated note-off preserves the first release choice. Both modes share the same sustained waveform. Native caller supplies event offsets by invoking on/off before the desired sample; no new MIDI or VST3 interface yet.

Build and render (from this directory):

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    mkdir Audio
    ./build/orbit_escape_test Audio

On multi-config generators use the executable in the Release subdirectory. Both demos use 48 kHz stereo PCM16, two three-note chords, 800 ms release, 100% long-cycle blend; note-offs at 0.5 and 2.5 seconds. Identical score and phase; only release mapping differs.

2026-11-27 Linux GCC 14.2 Release CTest 4/4; Clang 17 ASan/UBSan new probe PASS. Independent forward tuple-cost Dijkstra verified 857 reachable states, optimum 9 truncations/60 updates versus 25 pure truncation updates. Sustained baseline samples exactly equal; linear release max absolute difference 1.72605e-14. Seven rates including fractional extremes, three blends, eight voices, duplicate release, immediate note-off, repeatability, finite bounds and silence tested. Two Release renders match byte-for-byte. Offline 96 kHz/32-frame stress: 0/2000 and 2/2000 misses in two runs (max 78.449 and 971.978 us); sanitized run 1/2000 (max 1706.52 us). Preserve these timing negatives; not DAW qualification. No subjective listening or independent review.

Inherited exact SDK lock and prior hosted checkout receipts; tag and seven commit identities re-resolved, local GitHub checkout DNS blocked. No SDK code used in this probe. Windows/macOS build of this extension and host exposure outstanding. Next: phase-conditioned routes, envelope audition and a backward-compatible note-latched release-mode parameter if warranted. No shared changes or merge.
