# Projector Lattice — FX-004B / live configuration
Refs #528, #520/#521 (parent c8d9dae82e0275d1dfe80c6749873e725028a32d), #416/#417 (research draft 0039dbdead33f28b7eefb4ad5680aa05d437ff29). Read the parent README for the static paraunitary contract. This creative engineering extension does not establish a new mathematical or human-perception result.

## Controls and installation
Stereo only, both channels intentionally coupled. Stage axes L/R/S/D (normalized indices 0,1,2,3); each stage delay 1–1024 samples (normalized index 0–1023, plus one). Parameter IDs 100–103 axes, 104–107 delays, 108 causal inverse, 109 mix (0–65535 quantization), 110 bypass. Defaults Sum32/Left127/Difference256/Right511, forward, about 50% mix. Try full wet short delays 1/7/19/31 for tight spectral routing; or the default program plus an inverse instance with matching static full-wet settings for delayed reconstruction. For conservative headroom use <=1/16 FS at input to the pair. Do not expect reconstruction under clipping, bypass, wet/dry blending, or changing programs. Both channels must be retained. Zero declared latency (intentional delay effect); conservative tail 4096 samples.
When a qualified Windows artifact exists, unzip the entire MHACProjectorLattice.vst3 bundle into C:\Program Files\Common Files\VST3 and rescan the host. No binary claimed until that workflow passes.

## Real-time contract
Live has two preallocated 64 KiB lattice histories. The old engine remains audible while the exclusively owned inactive engine is configured and warmed for its complete FIR tail (at most 4096 samples); then a 5 ms linear crossfade occurs. Latest requested configuration is coalesced during a transition and begins on the next sample after completion if different. Each switch includes one bounded 64 KiB clear; no heap, locks, file/network I/O or logging in process. This is intentionally not instantaneous discrete modulation, and crossfades are not claimed paraunitary. Wet and bypass use a finite full-scale 5 ms slew. Input and final output bounded to +/-1 FS; nonfinite and tiny inputs zeroed. Bypass is protected dry, not bit-transparent for out-of-range/nonfinite signals. State stores desired program and controls, not delay history; 26-byte PL v1 little-endian state with validation and transactional decode. Reset clears history and installs desired controls. Native adapter applies queue points before corresponding sample; zero-length flush supported, discrete changes coalesced as above. Host state/processing lifecycle, automation queues and real-time deadline behaviour still need actual adapter qualification. No GUI beyond host controls.

## Build
CMake 3.25+, C++17. cmake -S . -B build; cmake --build build --config Release; ctest --test-dir build -C Release --output-on-failure. Run lattice_live_demo in a writable directory to render three 48 kHz stereo little-endian PCM16 files (dry, fixed, automated), wrap in WAV with Python wave as described in parent README. Automated demo changes program at 1 s, direction and stage 3 at 2 s, bypass at 3 s. Original synthetic tones only.
SDK: git clone --branch v3.8.0_build_66 https://github.com/steinbergmedia/vst3sdk.git; git -C vst3sdk submodule update --init --recursive. Configure with -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=<absolute clean SDK checkout>. Exact root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0, official tag freshly resolved 2026-11-25. Recursive gitlinks enforced by CMake, SDK and recursive checkout must be clean. Prior qualified #506 artifact records:
- base 3d2e82f8e6bff59c1d8b7a27491a29c2286b5206
- cmake de6e54eeaaab35b7145f5c32c279b5e892146e04
- doc 6d4737c9e70750056e731d88d49aa06eefc8a1a4
- pluginterfaces 31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c
- public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95
- tutorials 33b73dfbb87f3fde3bce8c0a10cae934dc66ad34
- vstgui4 76823bdbe286e4bdb9f79ab8986af5ce7202336c
Windows workflow builds validator and plugin, requires zero validator failures and packages complete bundle, notices and source/SDK receipt. Local GitHub DNS resolution failed; no SDK compile performed here. Linux/macOS plugin targets intended, unqualified.

## Executed receipt 2026-11-25
GPT-6.2 same-agent implementation/testing. GNU 14.2 Linux x64 native CMake Release CTest 2/2 PASS (standalone core targets); ASan/UBSan live test PASS. 96,787 live assertions: exact old-engine output during warm-up, numerical linear blend oracle, exact equality to independently warmed new engine after fade at six rates 8–384 kHz; rapid changes, float determinism, silence, bypass and state rejection. Two million double frames with periodic inverse changes took 0.0364 s on local offline benchmark, not worst-case real-time measurement. Automated demo peak 0.091601 FS; three PCM hashes reproduced twice:
- automated 7ffce62488a77cb154b707f05330fcaf9c804c1acc9d414cf0f1d46bc6b4bd0d
- dry 53923eb02a87d2383de9e8b48c70b3e39f34fe432273ba3cbd039720068e561e
- fixed ba76a95d54f9a2c42f5cc380eac969873439a13e482942859fe803190de48e9f
Tested blobs: lattice.hpp dad04b158bb5f6f606f5e04ee8d13a1dc4b3b020; live.hpp 8f8701a60d89e9833edaa5ecfd8140e91602ecb9; live_test.cpp fed66ddfa3771ad37aa69820335d02386b49e4eb; live_demo.cpp 071bfd7a25963a1bade7255e470d44851d1950d1. Native adapter derived from qualified #506; not locally compiled. No listening, independent review, DAW or SDK validator claim for new plugin. No shared manifest, frozen protocol, or sibling changes. Draft/HOLD.
