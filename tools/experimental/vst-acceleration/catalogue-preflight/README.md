# MHAC VST Acceleration — Windows x64 catalogue preflight

Refs #626. Read-only offline delivery qualification, not a plugin, installer or scientific evidence. This deliberately lives outside both foundries and shared build/registry files.

## Run

Python 3.11+; standard library only. From this directory:

```sh
python -m unittest -v
python preflight.py pins.json /path/to/downloaded/actions/archives
```

On Windows use `py -3` if appropriate. Download the four **outer** Actions archives and rename to the exact filenames in pins.json; preserve bytes. Direct inner delivery ZIPs also work with a separately reviewed manifest using the inner digest, not by bypassing the digest check. Nonzero exit means stop; never update a trusted pin merely to silence a failure. The JSON success report identifies the actual archive, inner delivery and binary hashes. No extraction or code execution takes place.

## Recovered actual Windows artifacts (2026-11-25)

| Plugin | PR | Exact Windows run | Download | Version |
|---|---|---|---|---|
| Freeze Socket | #439 | [45534581573](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45534581573) | [14986731404](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45534581573/artifacts/14986731404) | 0.1.0 |
| Golden Receipt | #447 | [45537942765](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45537942765) | [14987637390](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45537942765/artifacts/14987637390) | 0.1.0 |
| Three Winters | #597 | [45709981415](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45709981415) | [15068070040](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45709981415/artifacts/15068070040) | 0.2.0 |
| Erasure Loom | #599 | [45722951639](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45722951639) | [15073276177](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45722951639/artifacts/15073276177) | 0.2.0 |

The exact source SHA and outer SHA-256 were independently read from GitHub PR/workflow/artifact metadata and compared to downloaded bytes and embedded BUILD-SOURCE receipts. Factory IDs were independently read from each pinned plugin.cpp (blob IDs respectively 7eb912915247545c023c187697d8a29a546d6594, bd7da2fcd822b07dd5c3a09def14a33223a4ab05, a392dd4d43ad750a345d6311389138e9619aa295, 2d80f9e881331bdf76022f79d1b0e59bb82e9540). SDK tag v3.8.0_build_66 resolved via official upstream to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; seven recursive pins come from the pinned qualification recipes and recovered receipts, not a new native checkout. All four Windows and corresponding research-integrity workflows returned completed/success at inspection. Each embedded validator transcript records 47 passed, zero failed with no ERROR: marker. Eight class IDs and four bundle install names are distinct. Exact hashes in receipt.json. Artifacts are ephemeral GitHub downloads, not committed binaries.

## Qualification and limits

Executed locally using Python 3.13.5 on Linux: five unittest methods PASS (18 package mutation cases, separate digest and two catalogue collisions, duplicate JSON key, positive direct/nested equivalence); four real nested Actions packages PASS. Local Git DNS failure prevents full checkout and full native repo suite; no additional CI workflow or paid runner added. Same-agent code and tests, but distinct from originating foundry implementations. Git blob identities of tested code, test, pins and receipt were matched against the committed files. No Windows host execution, actual DAW loading, audio listening, fresh SDK build, binary signature/authenticity certification or independent human review was performed in this run. Static PE header checks are not a complete PE parser. Path checks are conservative, not a general-purpose hardened archive extractor; ZIPs are never extracted by this utility. Only matching trusted manifest digests establish identity; embedded receipts and validator text are not cryptographic attestations by themselves. Artifact expiry remains a delivery concern.

For owner audition, after preflight and ordinary trust/review, manually extract each original delivery ZIP, retain its notices and evidence alongside it, and copy the complete .vst3 directory (not only its inner DLL) to the normal Windows VST3 scan path (commonly C:\Program Files\Common Files\VST3), avoiding overwriting an existing same-name version. Rescan in the DAW. Use Golden Receipt and Three Winters as MIDI instruments; Freeze Socket and Erasure Loom as audio effects. Start at low monitoring gain; check note release, bypass, parameter automation and state reopen. Do not confuse distinct class IDs with actual host coexistence. No claim that Erasure Loom's separate native multiscale laboratory is exposed in this adapter. Preserve upstream issue-specific gates.

Next: independent review, qualify more distinct exact-head binaries and perform a real multi-plugin host load/render and saved-session round trip; keep the manifest immutable per audited batch, not a moving latest list.
