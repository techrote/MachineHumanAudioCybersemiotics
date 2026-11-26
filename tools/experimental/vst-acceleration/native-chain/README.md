# MHAC-VST-ACCEL-002 — native Golden Receipt → Freeze Socket chain

Refs #632, #626/#627. Original musical score plus integration regression, not a DAW, VST3 host, production TTS or human evidence. Scope: two host-independent cores from the already separately qualified Windows plugins. No SDK code or upstream source redistributed here. Inspect upstream rights before any external redistribution.

## Reproduce

Python 3.9+ and a GCC/Clang-compatible C++17 compiler. From a clone of this repository, fetch the two exact commits if not locally present:
```sh
git fetch origin eb78ea3b7a08a646910e66235724f259aeeb8190 fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2
python tools/experimental/vst-acceleration/native-chain/run.py --repo . --out chain-audition
```
Use `--cxx clang++` or a GCC-compatible Windows compiler if needed; Windows execution of this launcher is not yet qualified. A separately recovered pair of header files named engine.hpp and freeze.hpp can be supplied with `--headers /path/to/headers`. Both modes require exact blob hashes before compilation; local headers are isolated into a temporary build directory. Output directory must be new/empty. Optional `--sanitize` enables ASan/UBSan (where supported). No network fetch is performed by the script; git show mode requires objects already present. Local run used --headers because Git DNS was blocked.

## Exact input provenance

| Core | Commit | Git blob |
|---|---|---|
| [Golden Receipt #447](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/447) | eb78ea3b7a08a646910e66235724f259aeeb8190 | 482ffd924042f201c513a5e68c1b3e6a95c54999 |
| [Freeze Socket #439](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/439) | fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2 | 510fb2ab09690754c21f3c6bea0d3e9c48fd72d6 |

GitHub file retrieval and local git hash-object agree for both. Separate [Golden Windows qualification](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45537942765) and [Freeze Windows qualification](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45534581573) rechecked completed/success. SDK v3.8.0_build_66 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0 and seven recursive pins documented and verified in prior #627 batch; no SDK dependency, checkout or ABI execution in this DSP-only increment. Catalogue #627 integrity run 45724675619 now completed/success.

## Actual evidence, 2026-11-26

Linux x86_64 GCC 14.2.0, C++17 -O2 -Wall -Wextra -Werror: executable PASS. Separate -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer execution PASS. The Python launcher --headers mode executed twice, identical WAVs; tampered source negative control rejected before compile. Tested chain.cpp blob e3cf38e45bc333fdcd9db5d450d41e65a21fb387 and final launcher blob fa43cea35ebe1e84ef55b774a501e46e524b36a1 verified committed. No independent reviewer/subagent.

| Rate Hz | Paired frames | Wet-altered frames | Wet peak (linear) | Wet/dry energy |
|---:|---:|---:|---:|---:|
| 8000 | 32000 | 5653 | 0.0526751 | 0.531869 |
| 24000 | 96000 | 16982 | 0.0525811 | 0.531872 |
| 44100 | 176400 | 31216 | 0.0525796 | 0.531865 |
| 48000 | 192000 | 33975 | 0.0526339 | 0.531870 |
| 96000 | 384000 | 67961 | 0.0526349 | 0.531870 |

880400 frames exactly equal across constant 64 vs mixed 1/7/31/127/512/3/1024 partitions, after encoded parameter roundtrip in memory. Dry reference uses partition 257. Six note events, changed motif deletion and synth gain, three freeze contracts, bank edits, hold/release, bypass, note-off, exact silence after 2450 ms, no remaining active voices, shared stereo gain with 0.75 R/L ratio, finite/bounded output and wet energy lower than dry. Corrupt effect state rejected. Score sample-indexed automation is authored here and is not the actual VST adapter event dispatcher. Parameter presets only, not transient voice/transport persistence; no DAW session or VST state stream tested. Block-partition test is a native loop invariant, not a claim about scheduling/latency or sample-accurate host automation.

Original 48k stereo PCM16 dry/wet pair, 4 seconds each; identical fixed 0.5 conversion gain, no loudness normalization, peak 862/32768 FS, silence after 2.45 s. Not acoustic SPL or human listening evidence. Same-toolchain SHA256:
- golden-dry.wav: 2284c20bc6008ac7f92a95e97fe6dc3e721ad5441c16caeb07def92efe1b7ffa
- golden-freeze.wav: 88067f614b125450a9f9716bb1d2a55b47f96cc56e1efe0d1451171e179e43c9

## Disposition

Draft/HOLD; no new CI workflow, no paid resources, no merge. Git DNS blocked, no local Windows host or SDK installed; git-show launcher path and Windows native execution untested. Existing individual Windows artifacts remain available via #627. Next extend this score into a true pinned SDK VST3 host chain, exercise actual plugin loading, event queues, buses, and component/controller state streams; qualify on Windows and compare output with this native reference only after mapping semantics. No scientific or human evidence claims.
