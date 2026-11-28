# VST-TTS-FOUNDRY-001 local prequalification

**Date:** 2026-11-28

**Disposition:** local implementation evidence only. This is not independent VST3 qualification, a DAW audition, a listening study, or authority to merge/promote.

## Native Release

Environment: Linux x86_64, GNU C++ 14.2.0, CMake Release, `-Wall -Wextra -Wpedantic -Werror`.

Command:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
ctest --test-dir build --output-on-failure
```

Result: **4/4 PASS**.

Covered witnesses:

- LOGOS and ARTICULUM deterministic 44.1/48/96 kHz rendering at 1/64/511-sample block partitions;
- finite/bounded and non-silent output checks;
- malformed/non-linguistic text fallback;
- LOGOS block-boundary fixed-capacity phrase exchange;
- LOGOS and ARTICULUM state round trips plus corrupt-magic refusal;
- concurrent 20,000-plan SPSC producer/audio-consumer stress;
- ARTICULUM 384 kHz long-run stability;
- original standalone WAV specimen generation.

## ASan + UBSan

Command:

```sh
cmake -S . -B build-san -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined'
cmake --build build-san -j2
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
UBSAN_OPTIONS=halt_on_error=1 \
ctest --test-dir build-san --output-on-failure
```

Result: **4/4 PASS**, no reported sanitizer finding.

## Generated specimens

All are mono 16-bit PCM, 48 kHz, with no per-file normalization:

| File | Frames | Peak FS | RMS FS |
|---|---:|---:|---:|
| `logos-spoken.wav` | 240,000 | 0.3699 | 0.1288 |
| `logos-melodic.wav` | 288,000 | 0.3408 | 0.1234 |
| `articulum-tract.wav` | 288,000 | 0.6127 | 0.2507 |

## Still pending CI / independent qualification

The repository workflow is responsible for proving exact VST3 SDK 3.8.0 provenance, compiling the actual Linux and Windows VST3 modules, running the Steinberg validator, exercising the actual loaded modules via the SDK host probe, packaging/extracting the bundles, and repeating validator/host checks on extracted copies. Those results must not be inferred from this local native prequalification.
