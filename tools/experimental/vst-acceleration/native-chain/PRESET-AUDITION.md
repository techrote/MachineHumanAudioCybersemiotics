# MHAC-VST-ACCEL-003 — Preset and MIDI audition kit

Refs #632/#633 and #626/#627. Cumulative addition to native-chain scope; no foundry, shared CI, frozen records or main changes. Base main 495a98ca12bae467a507031f04931aa4254b1866; previous acceleration head 6fac46299513277e40fe3e7f9179b48f162a2f45 passed integrity run 45731882795. Software/audition apparatus only, no research or human validation.

## Reproduce

Python 3.11+ standard library; from this directory:

    python preset_bank.py --out MHAC-preset-audition.zip

Runs four unittest methods before generating a new ZIP (refuses overwrite). No network or installed SDK needed. Install the matching original Windows bundles, with their notices, from [Golden Receipt 0.1.0](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45537942765/artifacts/14987637390) and [Freeze Socket 0.1.0](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45534581573/artifacts/14986731404). Use the catalogue preflight in #627 against the original packages. This ZIP is an additional preset/MIDI kit, not a plugin package. No SDK or plugin binary redistributed. Do not overwrite existing installed versions.

## Exact format evidence

Read original processor/controller adapters and state codecs at Golden Receipt eb78ea3b7a08a646910e66235724f259aeeb8190 (#447; engine blob 482ffd924042f201c513a5e68c1b3e6a95c54999, adapter bd7da2fcd822b07dd5c3a09def14a33223a4ab05), Freeze Socket fe3a3f4268e59d68698d34b8fd45f43ea2c9e0f2 (#439; engine blob 510fb2ab09690754c21f3c6bea0d3e9c48fd72d6, adapter 7eb912915247545c023c187697d8a29a546d6594). Processor class IDs from verified Windows moduleinfo in #627. Component-state chunks only: GR01 uses five Q24 parameters; MHFZ version 1 uses ten integer millionths. Both controllers implement setComponentState. No controller-only state or transient state persisted. Host loading remains untested.

Official SDK v3.8.0_build_66 root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; Windows job 138949085246 log read again, recursive checkout of all seven dependencies recorded. Read exact [preset file implementation](https://github.com/steinbergmedia/vst3_public_sdk/blob/a3911a4615dabbfdfd9d181ee26b05c70c289a95/source/vst/vstpresetfile.cpp) (blob 2febe4a41d39740f5e2e8ba1a64e130afdb9564a) and [FUID string implementation](https://github.com/steinbergmedia/vst3_pluginterfaces/blob/31d6eeba6daaa3e2a8bfbe3e7a90ca0b7fbfbc1c/base/funknown.cpp) (blob d796780e2c958bef790b0769abc10c92077b4bf8). Independently implement only the documented version-1 header, ASCII processor FUID, little-endian list offset, one Comp chunk and chunk-list entry. Strict parser accepts only this generator's canonical subset, not arbitrary valid VST3 presets. No SDK code copied; no license changes.

## Actual results

Linux Python 3.13.5, four unittest methods PASS twice; 12 preset round trips byte-identical, two fixed state-byte controls, normalized quantization tolerance, 1,344 truncated prefixes and 120 structural mutations rejected, plus trailing-data, out-of-range-state and nonfinite-input controls. Separate MIDI event decode verified six note ons, six note offs, 120 BPM, 500 PPQN and 4 s end marker. Two generated ZIPs byte-identical; unzip -t PASS all 15 entries, per-file hashes in manifest. Exact tested generator Git blob a38fa7b7d3be87005835bf54316e5bd67cb28d92 matches committed file at dff71d3b289c12449b4d9fed58a31f4029e03b09. ZIP SHA256 820308e0e50ae65cdedff4c4fe2f739312f21fce83aeabc54bbe6ec225cca164. AI-assisted same-agent implementation/testing. No new native SDK compile, no actual VST host, no listening or independent review; Python state encoder/parser is independently authored against source format, not an invocation of the C++ state codec. Local git ls-remote failed DNS; no Wine or SDK checkout. No new CI workflow or paid resources.

## Owner audition protocol

At low monitoring gain import Audition.mid at 120 BPM, assign Golden Receipt, insert Freeze Socket. Test Golden 02/03 identical deletion fingerprints, 04 equal-gap counterexample. Test Freeze 02/03/04 using identical Hold and Step A-D automation; merely choosing mode without Hold does not engage freeze. Use Freeze 06 as a bypass reference. Compare parameter readback, dry/processed renders and save-close-reopen behaviour; retain host/version, sample rate, buffer size and exact package hashes. MIDI velocities are 7-bit approximations and the MIDI file has no automation; it is not a reproduction of the prior exact native DSP chain. The presets are candidate patch files, not host-qualified ones. Next real SDK/DAW load, parameter/event queues and component/controller restoration remain HOLD. No main merge.
