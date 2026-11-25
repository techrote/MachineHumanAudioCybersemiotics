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


## FX-007D — 0.2.0 integrated probe and softened edges

Refs #598, #321 (research pin 332e1029b30f20cf3f9eab52ac0b21c65c8688e8, section 2). The restored-probe operator directly realizes the formal single-observation result; the continuous morph and boundary admission are creative engineering extensions, not general audio repair or evidence of human effects.

The same stereo VST3 class IDs and parameters 1100–1106 remain. New continuous normalized parameters are 1107 Probe restoration and 1108 Soft erasure edges (both default zero). EL02 state is 76 bytes; EL01 is 60 bytes and migrates with both new controls zero. The stream reader reads the version header before consuming its fixed payload; invalid versions and short states fail. Old software cannot read EL02. Geometry, probe, repair and edge latch at frame boundaries; wet/gain/bypass slew remains 5 ms. Latency 144 samples and conservative tail 288 samples unchanged.

Edge=0 preserves the exact hard reconstruction; Edge>0 blends the missing chunk's reconstructed value with its original sample using wet weight min(1, min(lane,15-lane)/(8*Edge)). The first and last samples of each missing chunk are original at any nonzero edge; at Edge=1 the maximum wet weight is 7/8. This deliberately admits original observations and changes the erasure contract; the pre-clipping coefficient norm remains bounded by the convex budget because the identity row has norm 1. It is not a general anti-aliasing filter, nor does it guarantee click-free parameter switching. No dynamic timescale or latency change yet.

Native build: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run loom_live2_demo from a writable directory (Windows multi-config: build/Release/loom_live2_demo.exe). Four original 4s 48 kHz stereo WAVs plus tail use the same source: hard (probe=0/edge=0), soft (0/1), probe (1/0), morph (both swept). All use separation 1, budget 16, rotation 0, repair/wet/gain 1. For conservative processing use budget 2, wet .5, edge .5, probe .5. No external samples or services. Install the complete VST3 bundle to C:/Program Files/Common Files/VST3 after a successful exact-source build; rescan host.

Local Linux x64 GCC 14.2 C++17 Release -Wall -Wextra -Werror CTest 4/4 PASS; new live2_test ASan/UBSan PASS. 53,424 exact migrated legacy paired frames and 19,404 additional checked frames at seven sample rates; truncation, NaN, unknown version, soft edge envelope, probe endpoint, delayed bypass, tail and finite independent channels tested. Four new WAVs reproduced byte-identically in two runs; hard peak/RMS .26971/.0689067, soft .240639/.069238, probe .179978/.0692624, morph .232794/.0693336 FS. Native tests do not exercise IBStream or actual host lifecycle; concurrent state access remains unqualified. Previous head 08ec9d11a8749e0231360cbfd503895b9944cd8d completed Windows run 45697259719 (47/47 official validator) and integrity run 45697259680; its adapter was still 0.1.0. Local SDK clone DNS blocked, exact official tag and seven upstream revisions re-resolved and recursive gitlinks confirmed in predecessor Windows logs. Existing scoped workflow, SDK lock and license packaging retained. No new Windows result claimed before exact-head qualification. AI-assisted code and same-agent tests; Draft/HOLD, no independent review or listening.
