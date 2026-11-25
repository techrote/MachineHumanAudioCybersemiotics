# Erasure Loom 0.1.0 — VST3 candidate

Refs #598, #320/#321. Continuation of the native laboratory at 6469ef867d2338e7ec061613a1a73b005e10346e, on the existing draft PR #599. Source research: 332e1029b30f20cf3f9eab52ac0b21c65c8688e8, The Sample That Survives Its Absence, Model and exact certificate / Exact two-erasure law. This is a creative processing extension and synthetic measurement instrument, not general audio restoration or evidence of human effects.

## Host contract

Stereo input/output only, independent channels; mono arrangements rejected. Float32/Float64 audio entry points, no MIDI. Core frame 144 samples and conservative tail 288 samples. At 48 kHz: 3 ms latency, 6 ms tail. Bypass is latency-aligned and smoothed, not a bit-transparent path outside the core's sanitized +/-1 FS input domain. No custom GUI; use host-native controls. Processor FUID DC4F4B71-8CA24A61-A3B728C4-C77342EE; controller FUID 180FD226-37C64D5B-9BEA1378-6F8D22A1. These IDs and parameter IDs are intended to remain stable.

| ID | Control | Normalized mapping / default |
|---|---|---|
| 1100 | Separation | 1+round(3v), default 4 |
| 1101 | Rotation | round(8v), default 0 |
| 1102 | Amplification budget | 1+15v, default 2 |
| 1103 | Repair | v, default 1 |
| 1104 | Wet | v, default .5 |
| 1105 | Wet gain | v, default 1 |
| 1106 | Bypass | v>=.5, default off |

Parameter points are consumed at their sample offsets as steps, not interpolated between host points. Geometry, budget and repair latch at frame start; wet, gain and bypass have 5 ms bounded slew. Changes in reconstruction geometry can cause deliberate discontinuities. State EL01 is 60 bytes: ASCII EL01, seven little-endian IEEE binary64 normalized values. Decode validates complete size, tag, finite range before application. The state is patch-only; no audio buffers. No preceding VST3 state version exists. Concurrent state access during processing is not yet qualified; the initial adapter inherits direct state access and requires serialized lifecycle calls pending a thread-safe handoff. Do not claim concurrent state restore is safe.

## Build and install

Native CMake 3.16+: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run loom_demo and loom_live_demo in separate writable directories. The latter generates an original six-second stereo chirp/pulse reference and wet geometry sweep, 48 kHz PCM16, 288 samples tail. Separation changes from adjacent to distributed at 3 s; rotation changes every .25 s; budget cycles from 1 to 16 and back over 3 s.

For VST3, use CMake 3.25+ and a clean recursive clone of the official SDK tag v3.8.0_build_66 at 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; git submodule update --init --recursive. The seven pins are in SDK-GITLINKS.txt and enforced by vst3/CMakeLists.txt along with clean checkout and recursive submodule status. No substitute SDK. Configure: cmake -S vst3 -B build-vst -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/path/to/sdk. Build --config Release --target MHACErasureLoom validator. Use the SDK validator, preserve its complete log and SDK notices. If Windows build succeeds, extract the complete MHACErasureLoom.vst3 bundle into C:/Program Files/Common Files/VST3/ and rescan. Linux/macOS intended, not compiled. Do not install unqualified artifacts.

Presets (separation, rotation, budget, repair, wet, gain): Guarded Grain (1,0,2,1,.5,1); Fragile Scatter (1,0,16,1,1,.7); Distributed Repair (4,0,16,1,1,1); Dropout Gate (4,0,2,0,1,1). Start with low monitoring gain. Presets are settings, not binary VST3 preset files.

## Local receipt 2026-11-25

GNU 14.2 Linux x64 C++17 Release -Wall -Wextra -Werror CTest 2/2 PASS. Debug ASan/UBSan CTest 2/2 PASS before adding the new renderer (test sources unchanged). 12,348 paired sample frames across seven rates including 1234.568 and 1234567.8 Hz, normalized control mapping against original engine, state roundtrip and invalid state rejection, deterministic automation, latency and finite tail. Float-quantized input versus the same promoted double input, not a host-format test. Original 576 Fourier basis and 360 budget checks PASS; max basis error 4.77396e-15. New renderer executed twice, byte-identical outputs; reference peak .138213 RMS .0674625; geometry sweep peak .362953 RMS .0691328. No listening claim. Local SDK clone blocked by DNS; official tag and all seven dependency commit identities freshly resolved through GitHub. No local VST3 build, actual host, concurrency or independent review claim. Scoped Windows workflow is a qualification attempt, not a PASS. Draft/HOLD.

Tested source Git blobs: loom.hpp fc35c6e40fdf75d643b2d94041a7a396fd6ea618; loom_test.cpp f0a462b9d7e2b7febba5fdbf98ee31069a6df6e2; loom_demo.cpp 225b2398c6fe559a1a6ec01cb5fec21d99817927; live.hpp b9e215365a2ea5953332d0a9b33d884f41848c5d; live_test.cpp d7030c1698d0b8464298aed41e5920750ca96b9f; live_demo.cpp cc7bdeb45b6fff1af501585d12c14656118ae79c; CMakeLists.txt 4e378e5d9b332b4bb478b4b35136cab7030c303c.

Next: inspect exact Windows result and validator, qualify state handoff and real DAW lifecycle, then consider fixed-latency selectable reconstruction scales and softened boundaries. The arbitrary-audio negative control remains: exact recovery only holds for the source's periodic degree-three model.
