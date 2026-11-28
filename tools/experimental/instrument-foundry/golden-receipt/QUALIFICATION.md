# Qualification — MHAC-INST-001

2026-11-25. Single-agent implementation and checks; no independent or human validation. Base main reported by adjacent PRs 495a98ca12bae467a507031f04931aa4254b1866. Read AGENTS, RAG, programme, runbook, issue #428 and comment, #429 report pinned at 07fb2f67a5a2cf26312699410f00152033cae843; #439 effects branch and CMake/plugin source read at c88d4cf1d295b08e5f6f8f248d28aaca8e9ffee6 (existing repository workflow reported success, not SDK validation). Fresh issue #446 and branch; no existing instrument branch found by mhac-inst search. Separate paths; no changes to research records or shared manifests.

## Executed locally

- Linux x86_64 GNU C++ 14.2.0, CMake 3.31.6: Release build and CTest 1/1 PASS. Core test: 4,620,153 assertions without renders, 5,109,777 with WAV renders. Counts are overlapping per-sample checks, not independent observations.
- AddressSanitizer + UndefinedBehaviorSanitizer: 4,620,153 assertions PASS.
- Rates 8, 44.1, 48, 96, 192 kHz; same sample sequence across different offline chunk loops (not host adapter block tests); two golden collision pairs, equal-gap negative control, note ID/channel release, full 16 slots and excess-note rejection, silence, state round-trip/rejection, nonfinite gain and invalid rate rejection.
- Release test wall time ~0.09 s on execution environment, not an isolated real-time CPU benchmark. Adapter float/double buffers, bus arrangements, host event offsets, and automation untested.
- WAVs generated twice, byte-identical on repeat, six 1.7 s 48 kHz stereo PCM16. Peak 0.06424 FS, no clipped samples.
- Missing SDK path configuration correctly rejected; actual SDK checkout and plugin build were not possible.

| Local verified Git blob | SHA |
|---|---|
| engine.hpp | a431e682eb493d97ef84d2904567594ff1f93056 |
| test.cpp | 46b89c6ee119b9441e8af87a4bcfb0f9fcbf50af |
| CMakeLists.txt | d3a5981da4218dda6252639b4b282ccbb5d4f6a9 |

## WAV receipts (SHA-256)

- golden-0.wav: 8ab802933215f4de4509e66ab8f891cdb85dc53ae53564e053d0c9f49517acb9
- golden-1.wav and golden-3.wav: 48d2bc56aa0bae7b02933d088c2928fa1559ed4806352ebbb31a173538ee4d39
- golden-2.wav and golden-4.wav: 9e94ace671c49b1571f0f9e8fc49532471972c57ded57a067b37ab5a7cb82cc7
- equal-delete-1.wav: 027e565862935f3804fa45a31543b25fd3b1c4e2bd2e4c10d6e9e58f00a3acf4

The matching hashes demonstrate exact render identity for the implemented collision classes only. They are not listening observations or empirical evidence. WAVs reproducible from test.cpp rather than stored in repo.

## Blocker

git ls-remote https://github.com/steinbergmedia/vst3sdk.git failed with "Could not resolve host: github.com" in native environment. GitHub connector read official exact root commit message VST SDK 3.8.0, CMake project VERSION 3.8.0 and tag v3.8.0_build_66 CMake content. Recursive gitlink check enforced at configure time, but no actual recursive checkout verified. No plugin build, official validator, Windows/macOS host testing, portable plugin ZIP or full repository native suite. Next: use narrowly scoped native Windows/Linux build environment with exact SDK pin, run validator, then audition and test host events, state, automation and performance. Draft/HOLD; no acceptance claim.

## 2026-11-25 follow-up — native Windows validator recovery

Prior exact head `b5535eddc4bbd4b2030c5b9c6adbf898a38b6342`: [Windows run 45531129635](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45531129635) compiled native core and plugin, checked out pinned SDK, but official validator emitted setupProcessing errors at 1234.568 and 1234567.800 Hz for both sample formats. The displayed 47/0 summary did not override process exit -1; package step was skipped. [Integrity run 45531130368](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45531130368) passed. Read adjacent Freeze Socket qualification at fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2 without editing it.

Repair: shared engine and adapter predicate accepts 1000–2000000 Hz, rejects nonfinite and out-of-range rates. Longest motif is at most 3,160,000 samples at 2 MHz, within uint32. New regressions exercise full-length exact alias pairs, highest tuned pitch, finite bounded output, release and silence at fractional and endpoint rates. Linux GNU 14.2.0 -O2 test with renders PASS 10,906,711 assertions; ASan/UBSan PASS 10,417,087. Original-range rejection negative control fails at assertion 4,620,141 (exit 1). All six 48 kHz WAV hashes unchanged from above. Tested source blobs: engine.hpp 482ffd924042f201c513a5e68c1b3e6a95c54999; test.cpp d4b109bf536c6a58e0e90302b26534b86d17c021. DNS still blocks native SDK checkout locally. Windows workflow separates compilation from a mandatory validator exit-code and summary gate; preserves validator transcript, exact source/SDK and recursive gitlinks, notices and complete ZIP. No shared workflow edits. Same-agent checks, no DAW or independent qualification. Await exact-head CI before publishing any binary; remains Draft/HOLD.
