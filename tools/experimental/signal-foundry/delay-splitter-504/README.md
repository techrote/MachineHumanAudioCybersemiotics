# MHAC Delay Splitter 0.1.0

Refs #504, #416, #417. Source base 495a98ca12bae467a507031f04931aa4254b1866; research draft pinned 0039dbdead33f28b7eefb4ad5680aa05d437ff29, section Minimum delay bounds and construction. Direct realization of the single diagonal projector stage, plus creative smoothed control extensions. Not a realization of the entire cyclotomic theorem or evidence about listeners.

## Routing and use

Stereo input and stereo output are required; a left-only source shows the complementary combs most clearly. With P the projector onto (1,1), forward E=I-P+z^d P, reverse F=P+z^d(I-P), and F E=z^d I. At fixed delay, full wet and adequate headroom, total finite-stream energy (including tail) is preserved, and a second instance in inverse mode restores the input delayed d samples. It cannot undo time-varying settings, clipping, independently changed channels, or partial wet mixes. Identical stereo inputs are simply delayed in forward mode, not widened; sum-to-mono is not a substitute for the two-port inverse.

Controls/IDs: 100 Delay (16,64,256,1024 samples), 101 Causal inverse, 102 Wet mix (default 50%), 103 Bypass. Fixed maximum tail 1024 samples, zero compensation latency (intentional delay as effect). Two channels intentionally coupled. Switches and mix use a 5 ms one-pole time constant with eventual exact snap; crossfades are not paraunitary. Input/output guards clamp to +/-1 FS and suppress nonfinite or tiny values; for the lossless experiment use input peaks <=0.25 FS. State v1 stores four little-endian binary64 normalized values with magic and version; runtime delay history is not saved.

Suggested patches: Short comb (16, forward, full wet); Broad comb (256, forward, full wet); Long spatial comb (1024, forward, 50%); Reconstruction (two instances at same fixed delay, full wet, forward then inverse). Use a stereo track with the source panned left for the first two. Allow control changes to settle before measuring; start both instances from cleared histories. Monitor at low volume.

## Build and install

CMake 3.25+, C++17. Core: cmake -S . -B build; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run splitter_demo in a writable directory to generate four original stereo WAVs (dry, 16/256-sample splits and reconstructed 256). No dependencies in core.

Native adapter: official Steinberg vst3sdk tag v3.8.0_build_66, root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0. Clone that tag, initialize recursive submodules exactly to recorded gitlinks, and pass -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/path/to/checkout to CMake. Build refuses wrong root, dirty checkout or divergent/missing recursive submodules. CI retains recursive gitlink and source receipts and SDK MIT notices; no new repo license. Known seven gitlinks from qualified sibling SDK: base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206; cmake de6e54eeaaab35b7145f5c32c279b5e892146e04; doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4; pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c; public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95; tutorials 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34; vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c. Fresh tag resolved by connector to root; six changed gitlinks independently visible in upstream commit diff; seventh from sibling receipt. Fresh recursive checkout not yet executed here.

When an actual validated Windows bundle is published, extract entire MHACDelaySplitter.vst3 to C:\Program Files\Common Files\VST3 and rescan. Linux/macOS plugin builds intended but untested. Host-native parameters, no custom GUI. No runtime network.

## Qualification (25 November 2026)

GPT-6.2 assistant implemented and self-tested, no independent reviewer. GNU C++ 14.2 Linux x64, CMake Release CTest 1/1 PASS, ASan+UBSan run 654636 checks PASS. Eight sample rates (1000 to 2MHz including fractional validator rates), four delay choices, exact dyadic sample reconstruction with delay, finite-stream energy, exact impulse, deterministic float processing, extreme/invalid inputs, bypass settling and v1 state rejection. Demo at 48kHz: energy delta and double-domain reconstruction error zero for both 16 and 256 sample settings; peak 0.248413/0.247467 FS. Four WAVs reproduced byte-identically within this environment. No listening or human evidence. Core tests do not qualify adapter event queues, bus negotiation or variable host blocks; dedicated adapter-level tests and measured CPU budget pending. No Windows binary claimed.

Native GitHub access failed DNS (git ls-remote); connector used for repo and SDK tag metadata. Scoped Windows workflow based on qualified Retreat Shaper; mandatory validator and portable ZIP. Exact-head CI and independent review outstanding. No frozen records, shared manifests or sibling branches edited.

Local tested Git blob identities: splitter.hpp 19fd7e171005182c8e6a953a1007e48e5bfb653c; test.cpp 6e903ddb9a0658748845220848b4cf8c5cc60389; demo.cpp 6d4c09a256689d576d956e3e366d41c0def22e35. WAV SHA256: dry cd820b144c9af797ef03c965a23ab1c7b0ee5bcaaec30336b1173b58fcdd0eba; reconstructed-256 1aa38224a730fada304da9bf06c307113c2b81f9376f47c9e570f032b5568e31; split-16 5ce7df55465bbe4c5de9047585e8743d96b1a9e7c189a0bc426cfe98e86d1b18; split-256 fe7ac59344d4d4c43f1b3e89e6e0c5a46bc2ee10a0b07a0a0d4003af33e27724.
