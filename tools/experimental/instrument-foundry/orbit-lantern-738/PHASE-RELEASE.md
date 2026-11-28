# INST-011H — Phase-conditioned release and Windows test recovery

Refs #738 and #264; research draft #265 pinned 56c107f8f4147316a588484c47be28bc8f840fbb (Exact model and Exact intervention compiler). Creative sonification, not a physical resonator or listener study.

PhaseBank discovers the bounded reachable closure of the 68-state orbit under nearest and truncation updates, computes lexicographic costs to zero by reverse Bellman relaxation and precomputes 68 gain routes outside processing. Each route uses nine truncations and 48–60 updates. The forward tuple-cost Dijkstra test independently checks all 68 costs using the same integer transition. A separate Python calculation also found 857 reachable states. The native instrument's offPhase(id) selects the long oscillator's phase bin floor(68*phase/tau) at note-off. It holds that choice for the entire release, maps squared radius normalized by the starting state's energy (capped at one) to amplitude and linearly interpolates over the existing release time. This is phase-indexed envelope sonification, not direct integer-state audio feedback. At short releases states may be skipped between samples. The long oscillator phase is used even in blended mode. Existing linear and fixed intervention releases are retained, no preset or VST3 adapter changes. No new heap operations in on/off/tick.

Windows predecessor 45938282655 failed native compilation with MSVC C3493 (side not captured in the oracle lambda); the SDK and validator stages were skipped. The fix makes side a static local constexpr, avoiding capture. The previously qualified 0.1.0 binary is not invalidated by this test-source failure. No gate weakened; MSVC verification of the correction pending.

Build from the scoped directory:

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure
    mkdir Audio
    ./build/orbit_phase_test Audio

Use the Release executable subdirectory for multi-config generators. Fixed.wav (lowercase fixed.wav on disk) and phase.wav are 4-second 48 kHz PCM16 stereo original comparison renders: two three-note chords, pure long-cycle blend, 800 ms release, note-off offsets separated by 733 samples. Same score and pitch, different release trajectories.

2026-11-27 GCC 14.2 Linux Release CTest 5/5 PASS; phase probe 419014 checks with renders and 370984 without. Clang 17 ASan/UBSan phase probe PASS. Six rates including fractional extremes, eight voices, sustained equality, repeated note-off, immediate release, finite bounds and exact final silence. Both WAVs repeat byte-identically. PCM16 overall RMS fixed 0.03688245 and phase 0.03636250 FS; paired RMS difference 0.00182211 FS. No listening assessment. Previous escape native stress rerun 0/2000 observed misses; earlier misses remain negative evidence. Phase-mode real-time timing and actual host tests not qualified.

SDK tag v3.8.0_build_66 root and all seven gitlinks freshly reconciled to SDK-LOCK.txt; recursive trees retrieved complete, no nested gitlinks. Local SDK clone DNS blocked; no SDK code consumed. Existing notices retained in native package. No substitute. No new VST3 binary, no independent review, no shared files or merge. AI-assisted engineering. Draft/HOLD.
