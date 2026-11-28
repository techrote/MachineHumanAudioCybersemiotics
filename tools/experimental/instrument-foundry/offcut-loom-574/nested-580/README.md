# Offcut Loom — nested residual laboratory (INST-006B)

Refs #580, #574, #575 and [the pinned expedition, section 5](https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/839e0719729485311cacd8085bb49f7268a2ecc6/research/expeditions/instrument-plays-offcuts/README.md). Base 5d890b8a9db5d760c374fc197836d931a33f87e6. Exploratory creative instrument extension; no scientific or human-evidence promotion.

## Contract

Given the first complement (P,R) from the original voice, let M=clip(R,-U,U), D=(R-M)*a with 0<=a<=1. The second cut never changes P. Changing only a never changes M. Reclip M+D at U to recover M; reclip P+M+D at the original threshold to recover P (per voice, before summation). With unarticulated complements, the sum reconstructs the source up to floating-point rounding. This is not energy conservation. The helper partition expects a finite, bounded pair from the original split contract; the engine supplies that pair. The second threshold is scaled by the original voice envelope and velocity.

Eight fixed slots reuse the original carrier, attack/release, tuning, velocity and note identity semantics. Patch controls: original four values (routing forced split internally), second cut 0..1 of full note gain, deepest articulation depth 0..1, deepest modulation ratio 1..16 relative to carrier (capped at .45 cycles/sample). All latch at note-on. Each stem can be rendered to a separate buffer, or omitted via null pointer; no new allocation or I/O in tick/render. The sum of absolute stem magnitudes is bounded by .4 FS across eight voices. A ninth note is rejected, no stealing. Silence follows the original 40 ms release. Clipping/modulation can alias; no anti-alias guarantee. Constraints do not apply to arbitrary polyphonic re-clipping.

## Reproduce

From this directory, with the parent core.hpp from the pinned predecessor:

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
    cmake --build build --config Release
    ctest --test-dir build -C Release --output-on-failure

Create an empty demos directory and run build/nested_test demos (on multi-config Windows, build/Release/nested_test.exe). Three original four-second 48 kHz stereo recordings: nested-slow and nested-fast put primary+middle on left and deepest stem on right; nested-mix duplicates the fast summed output. All use original normalized threshold .25, amount 1, colour 0 (1:1), second cut .12, deepest depth 1, ratio 1 or 8. The API exposes the individual primary and middle buffers even though the stereo demos combine them. Suggested additional patch: cut .25, ratio 5, depth .65, original defaults. No installed plugin exposes these controls yet.

## Qualification receipt — 2026-11-25

GNU 14.2 Linux x64: Release CMake/CTest 1/1 PASS; parent original CTest 1/1 PASS; -Wall -Wextra -Wpedantic -Werror plus ASan/UBSan PASS. 267531 finite partition cases, maximum full-reconstruction error 1.11022e-16; 521175 paired voice frames across ten rates 1 kHz..2 MHz, exact primary and middle equality across deepest ratio changes, max deepest delta .00892003 FS. Capacity, release, nonfinite patch, extreme notes, reset, variable blocks and Float32 primary vs Float64 checks passed. Three repeat renders byte-identical on this environment; left identical across slow/fast, 70369 changed right samples, summed PCM reconstruction differs by at most one integer count. Maximum demo peak .030702 FS. Eight-voice ten-second offline benchmark .209-.224 s (no callback worst-case certification). No subjective listening or independent review.

Source identities of tested files: nested.hpp d5f4af976a7672eee137c903359677bba514d8e8; test.cpp ee93af6a8b39e9857ce1c130e0d967fac5724ae5; CMakeLists.txt 1c68c619d9bb9d72febebe966593076f7a885238; parent core.hpp 2cc832d3ba3d637da2d52fc176f093a471e9d1e9.

## SDK and next gate

The parent VST3 0.1.0 is unchanged; its exact Windows workflow 45642729031 passed 47/47 official validator tests with no explicit errors. The downloaded archive matched both published hashes; source and SDK receipts and x64 PE inspected. Official tag v3.8.0_build_66 re-resolved to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0, all seven dependency commits re-resolved and matched the parent CMake lock and artifact receipt. The parent CMake verifies clean recursive SDK checkout, exact root and dependencies and includes SDK license resources. Local SDK fetch failed DNS; no substitution. The nested lab requires no SDK. Windows and macOS nested compilation, plugin bus layout, stable new parameter IDs, state migration, host timing and validator remain unimplemented/unqualified. No new workflow or shared files. Next: choose three-stem VST3 output arrangement with stereo fallback, implement state migration and exact-head host qualification. Same ChatGPT assistant implemented and tested; Draft/HOLD.
