# Harmonic Memory Bank: module replay (FX-011P)

Refs #748, #265 at 56c107f8f4147316a588484c47be28bc8f840fbb. This is engineering qualification of a creative effect implementing a restricted minimum-intervention policy; not evidence of human effects.

The shared fixture now runs 128 native cases (four bands, two block sizes, normal/reversed same-offset queue order, manual conflict present/absent, mono/stereo, paired 48 kHz float32 and 96 kHz float64). Independent direct HarmonicBank calls supply the timing/host interface oracle. The loaded module uses SDK ParameterChanges and real component lifecycle, matched buses and silence flags. It checks exact output and state, held-high suppression, rearming, final silence, zero-frame state and automation flush, truncated/appended state rejection and all 42 controller parameter IDs/normalized state values. Commands remain nonpersistent. This is not an independent DSP implementation or desktop DAW assessment.

Native:
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build
    ctest --test-dir build --output-on-failure

Windows: follow BANK-VST3.md with the exact locked recursive SDK; build target bank_sdk_replay, then run its Release executable with the complete MHACHarmonicMemoryBank.vst3 path. The existing Windows job requires the validator and complete replay transcript before packaging. SDK probe must actually compile/run before claiming success. Local DNS blocks SDK checkout. No DSP/class IDs/parameters/state version changes. Same-agent verification; no listening or human evidence.

Native Linux GCC Release 14/14, Clang ASan/UBSan expanded fixture 5,904,853 checks, both previous automated WAVs byte-identical. Intermediate -Wshadow build failure corrected (local variable name). No SDK substitution.

## FX-011Q — lifecycle recovery (2026-11-27)

Exact predecessor `f874218e2d47c81667d4b8324f341ad293ccfc94`, Windows run [46054600234](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/46054600234), job 140693917770: native 14/14, both official validators 47/0, controller 42 PASS, then `optimal host failure 5905003` before the first module case. The numbered assertion is the initial `setProcessing(true)` call (native total 5904854 including argc check; controller 133 assertions; case creation/lifecycle and state checks lead to assertion 5905003). The pinned SDK `public.sdk` a3911a4615dabbfdfd9d181ee26b05c70c289a95 `source/vst/vstaudioeffect.cpp` implements the inherited `AudioEffect::setProcessing` as `kNotImplemented`. Bank Processor had no override. Add an explicit allocation-free, state-preserving success override. Reset remains at activation/prepare, not a pause/resume. The replay keeps its strict success checks, adds named lifecycle diagnostics, an empty start/stop pair, pause/resume during excitation with uninterrupted native audio as oracle, and checked final stop/deactivate/terminate for every case. No DSP, state, IDs, version, SDK pin or workflow change. Native archive sources verified against predecessor blobs; local standalone native CTest 1/1 PASS. SDK checkout still DNS-blocked; new SDK adapter/replay not locally compiled. Exact-head Windows run must succeed before claiming recovered compiled delivery. Preserve previous qualified 0.2.0 and failed replay evidence separately.

## FX-011U budget control extension

The original 128 cases remain mandatory; add 16 cases (48 kHz float32/96 kHz float64, 127/257 frames, mono/stereo, both objectives). Compare each sample against direct HarmonicBank admission. Queue budget command before same-offset settings, retain high while increasing budget, then rearm and require final silence. Controller checks all 45 IDs and legacy state migration; processor reads HM01 and writes HM02; malformed lengths rejected. Windows packaging requires both case sets and controller receipt. No local SDK build or desktop DAW claim.
