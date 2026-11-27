# Harmonic Memory Bank: module replay (FX-011P)

Refs #748, #265 at 56c107f8f4147316a588484c47be28bc8f840fbb. This is engineering qualification of a creative effect implementing a restricted minimum-intervention policy; not evidence of human effects.

The shared fixture now runs 128 native cases (four bands, two block sizes, normal/reversed same-offset queue order, manual conflict present/absent, mono/stereo, paired 48 kHz float32 and 96 kHz float64). Independent direct HarmonicBank calls supply the timing/host interface oracle. The loaded module uses SDK ParameterChanges and real component lifecycle, matched buses and silence flags. It checks exact output and state, held-high suppression, rearming, final silence, zero-frame state and automation flush, truncated/appended state rejection and all 42 controller parameter IDs/normalized state values. Commands remain nonpersistent. This is not an independent DSP implementation or desktop DAW assessment.

Native:
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build
    ctest --test-dir build --output-on-failure

Windows: follow BANK-VST3.md with the exact locked recursive SDK; build target bank_sdk_replay, then run its Release executable with the complete MHACHarmonicMemoryBank.vst3 path. The existing Windows job requires the validator and complete replay transcript before packaging. SDK probe must actually compile/run before claiming success. Local DNS blocks SDK checkout. No DSP/class IDs/parameters/state version changes. Same-agent verification; no listening or human evidence.

Native Linux GCC Release 14/14, Clang ASan/UBSan expanded fixture 5,904,853 checks, both previous automated WAVs byte-identical. Intermediate -Wshadow build failure corrected (local variable name). No SDK substitution.
