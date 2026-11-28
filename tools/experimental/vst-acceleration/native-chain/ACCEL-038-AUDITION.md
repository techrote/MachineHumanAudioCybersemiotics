# ACCEL-038 — exact Windows owner audition suite (2026-11-27)

Refs #632 / Draft/HOLD #633. Parent d996a0b8c457630e3d18a4b2a06393640f8d3fbf, live main 495a98ca12bae467a507031f04931aa4254b1866. The exact parent Windows [45994220931](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45994220931) and integrity 45994220871 completed successfully. Direct SDK probe: all six sample-offset runs 20,000 stereo frames each (44.1/48/96 kHz, 127/1024 blocks), max error 0; 20,000 concurrent restores, 407 saves, 300 audio blocks, whole state and final restore checked. Cold restore, zero-frame ordering, lifecycle and exact partition comparisons passed. Official validator 47/47, zero explicit errors; 48 preset renders, 24 zero-error comparisons; native mailbox 500,000 restores/439,726 consumed. Archived rate witness 480,296 frames/768 poles. No TSAN or actual DAW audition.

New qualified Trace Bell package artifact 15195705883: outer SHA256 fa74dd77708ab33537b0f69037ecc92f8236297ffc3f09580860d71fe82595c9, inner c36408772286a89314373a3126a878521df51b50dfa8e0a5e3fc8e70012ec327, binary f2bc429bc1df60bb0c05e67ce2b05bbf675cecd19901173a546c09f0950187a5. Both CRCs, AMD64, source and SDK gitlinks independently inspected. All ten WAVs and eight presets byte-identical to qualified ACCEL-034. The lifecycle correction is now qualified.

## Portable four-plugin set

The new offline standard-library package_audition.py assembles exact previously qualified artifacts without recompiling, changing upstream binaries or downloading at runtime. The source-host receipt pins the first three plugins; Trace Bell has an explicit pin. Download outer artifact ZIPs without extracting:
- Afterimage Choir 0.3.1: artifact 15148180211, source d09540c3870ef3684022ed17358c3d5556d70064.
- Three Winters 0.2.1: artifact 15156181930, source 4d7dbfe0ff330b50e52d70920407eb519748c503.
- Receipt Fold 0.3.0: artifact 15145497011, source 2cee431826772547699f43bf4d4e598cfbe7162e.
- Trace Bell 0.1.0: artifact 15195705883, source d996a0b8c457630e3d18a4b2a06393640f8d3fbf.
- Host evidence with four-track score, MIDI, preset and WAV stems: artifact 15194909235, run 45994220931, SHA256 e9300c376c22bc937899d2eed1e5045cf3be8b922c0c08cd88d202d69bc2c6d9.

Run: python package_audition.py --afterimage AFTERIMAGE.zip --winters WINTERS.zip --receipt RECEIPT.zip --trace TRACE.zip --host HOST.zip --out MHAC-ACCEL038-Windows-audition-suite.zip

Local execution twice produced byte-identical 109-file ZIP, SHA256 ee3edf0be0a74fa96a1c7b79af3add5e9eb5499ec4103803df57c98d662d5633. All 108 per-entry hashes independently rechecked; duplicate casefold names and four path traversal/absolute/Windows path variants rejected. Four AMD64 PE binaries, eight unique class IDs, exact outer/inner/binary digests, source and SDK version pins verified. All seven reference WAVs 48 kHz stereo PCM16, 576000 frames; sum of four stems differs from dry reference by at most one LSB. Seven session presets plus four MIDI tracks preserved; both wet comparisons differ from dry. The session includes only Afterimage, Three Winters and Receipt Fold; Trace Bell is an optional additional effect and is not used in those reference mixes. No new combined four-plugin live render is claimed. Original per-plugin licences and receipts retained; no Foundry changes, additional CI jobs, research changes, main merge or human gate bypass. Next: original catalogue expansion, not another Trace Bell qualification loop.
