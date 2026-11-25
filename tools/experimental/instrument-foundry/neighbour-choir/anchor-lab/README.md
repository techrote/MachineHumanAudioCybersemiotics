# Neighbour Choir Anchor Lab

Refs #534, #526/#527 and #388/#389 (research draft 661e4898ac42b2a44f6808f9d7c0e85434b07f1f). Parent instrument 11d8e5b9944937774b523f3cd2eb4bdbd760e32c. The witness field is a direct implementation of the draft's pair intervention; timed resonator reinjection is a creative synthesis extension, not a claim about perception or a new graph theorem.

`AnchorVoice` is an independent note-latched generator using the parent propagator. Set topology, root and second node (0–15, distinct), frequency, normalized coupling and strength, amplitude decay (0.01–10 s) and intervention time (0–2 s). `start` resets state; `release` suppresses pending injection and releases in 40 ms; `next` advances one sample without heap allocation, I/O or locks. Attack 5 ms, mono output, conservative ±0.25 FS bound. Calling `start` on an already audible voice replaces it abruptly: use inactive slots or external voice fades. No host adapter, state persistence, pitch events or polyphony are added by this module; the original instrument remains unchanged.

## Reproduce

From the anchor-lab directory (keep parent engine.hpp in place):

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
mkdir -p demos
./build/anchor_lab demos
```

On multi-config Windows use build/Release/anchor_lab.exe. Parent CMake also registers the lab in CTest, using the existing scoped Windows workflow. No new workflow or SDK dependency. Parent VST3 build instructions and notices remain in its README and qualification receipt.

All WAVs: 48 kHz PCM16 stereo, 0.7 s, left rook/right Shrikhande, root 0, 220 Hz, velocity .8, coupling .45, decay .9 s, strength .5, intervention .1 s, release .45 s. `adjacent.wav` uses second node 1 on both. `nonadjacent.wav` uses rook node 5 and Shrikhande node 6. `linear-control.wav` duplicates a strength-zero reference. These are new offline patches, not DAW preset files. Adjacent pair contrast reverses for the chosen nonadjacent pair; arbitrary nonadjacent pairs are not guaranteed to differ. The nonadjacent witness is not a clique count. At PCM16 precision the two contrast files are exact channel swaps.

## Verification — 2026-11-25

Same-agent GNU 14.2 Linux x86-64 C++17 Release: standalone CTest 1/1 and parent CTest 2/2 PASS. Direct ASan/UBSan and compiler warnings enabled PASS. 1,293,393 assertions (mostly per-sample checks); 240 unordered graph/pair witness cases; five full render rates 8, 44.1, 48, 96, 192 kHz, sample-exact block partitions 1/511, suppressed late interventions, invalid inputs, silence after release. Both contrast renders have sum squared difference 0.815412, PCM difference RMS 0.0049263 FS, peak 0.0476394 FS. Control difference zero. Three WAVs byte-identical across two local runs. Source hashes (Git blobs): parent engine 20a496303d45337e18913b1abba08fa474150800; lab header 352b4dcf87d60089e4bda8c7e2cab8ceb6ec89fd; test/renderer ae724d8f27e21272baf80dccdf6f97850f3021a6; lab CMake 6ed76d5eb2790abca5ec51f759ee74fde27fda7a; parent CMake 826b0a1685f73d2c6a65bc1c3c2ce47a31d61c78. Source readback matched. No independent review or listening, no new plugin binary or measured worst-case CPU claim. Native GitHub DNS blocked local SDK checkout. Main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS/RAG/programme/runbook/integrity/validation/experiments/human gates inspected. Signal lane #529 separate. Parent Windows and integrity runs 45583313404 and 45583311600 succeeded. Actual downloaded parent archive digest 0a1454605c48f5ccc4bed20dd7817668c1201a5f35401a8c762135df48298940 matched, inner archive integrity passed, PE x64, 47/47 validator, exact source and SDK 3.8.0 build 66 (tag freshly resolved to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0), seven recursive gitlinks matched parent receipt, license notices present. Parent qualification is not qualification of this new lab on Windows. Draft/HOLD pending exact-head CI and review. No changes to shared manifests or frozen records.
