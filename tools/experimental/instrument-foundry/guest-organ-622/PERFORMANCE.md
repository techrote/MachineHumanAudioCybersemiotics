# Guest Organ 0.3.1 — silent continuation scheduling

Refs #622, #461 at fb3fca1c21213b8520584108c1d65aa1db4b6cd4 (Executed miniature, Exaptation). Creative instrument implementation maintenance, not new scientific evidence. Parent 36e0b638d03dc403b76e27a9787148e6d8b4860a; base 495a98ca12bae467a507031f04931aa4254b1866.

The spectral and FM banks now skip sine evaluation when the countervoice blend is exactly zero, but continue identical per-partial phase arithmetic. No phase reset or bulk phase jump. Audible frames use the same summation. At full eight-note FM capacity this avoids up to 112 sine evaluations per sample during the opening quotation, keeping the eight base voices. No change to sound modes, class IDs, 11 automation IDs, GO03 state, buses, capacity or latency. Build and installation instructions in [LIVE.md](LIVE.md); 0.3.1 is a new candidate, not the recovered 0.3.0 Windows binary.

## Qualification, 2026-11-26

GCC 14.2 Linux x64 C++17 Release, -Wall -Wextra -Werror, CTest 5/5; new silent regression ASan/UBSan pass, 1,769,472 paired FM and spectral bank frames across nine sample rates, four roots, three depths and repeated silent/active switches. All three predecessor FM WAVs reproduced byte-identically. Same-agent engineering tests, no listening, human evidence or independent review.

Run CMake as in LIVE.md, then ctest --test-dir build --output-on-failure. Run guest_fm_demo into an existing directory to reproduce the audio. For the benchmark, compile silent_bench.cpp using g++ -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Werror; copy the identical benchmark source into a separate checkout of the parent and compile there too. Each trial has eight held FM voices, rate 48kHz, 64 samples per measured block, twelve trials. Audio processing only is timed, not hashing or allocations in the harness. Output hashes of all four double frame fields matched (3593a295e7bd41f5), not cryptographic equality proof. Observed median/p99/max in microseconds:

| Version | Opening | Continuation |
|---|---|---|
| 0.3.0 | 118.508 / 339.8 / 22625.8 | 120.808 / 324.126 / 5001.52 |
| 0.3.1 | 22.902 / 145.447 / 2929.96 | 119.906 / 691.701 / 3109.76 |

Opening median improved roughly 5.17x. Continuation median essentially unchanged; continuation p99 worsened and both versions exceeded the nominal 1333.3us block deadline in maximum observations. Uncontrolled shared Linux environment, no hard realtime guarantee; note-on setup cost not measured. Concurrent state and real DAW validation remain open.

Official SDK tag v3.8.0_build_66 resolved to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0, seven root gitlinks matched SDK-LOCK.txt and the actual 0.3.0 Windows recursive checkout. Local clone still DNS blocked. No SDK substitution. Reuse existing scoped Windows workflow, strict validator and license packaging. No change to frozen research, shared manifests or sibling paths. No merge; Draft/HOLD pending exact-head qualification and independent review.
