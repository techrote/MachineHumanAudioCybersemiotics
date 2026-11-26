# FX-009E — preset bank and signal probes (Refs #674)

Windows 0.1.0 binary qualified at f607babd77086e1cb6ca02eef6bb12805b83c4df, run 45821178550 / artifact 15117957408; strict official validator 47 passed, zero failed, no explicit errors. Integrity 45821178560 succeeded. This follow-on does not change plugin, DSP, RF01, SDK pins or shared workflows. Source scope: offline tooling only. Main 495a98ca12bae467a507031f04931aa4254b1866; sibling #681 read-only. Source research #338/#339 at f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64 sections 2–3. Direct restricted discrete model and creative audio extension; no scientific, human or listening claim.

Build the existing native project using CMake (SDK optional), then run receipt_fold_preset_probe [output-directory] (Release/ on multi-config builds). No argument runs self-tests; directory argument also writes eight component-only .vstpreset files and sweep.csv. The 92-byte format has a 48-byte header (VST3, version 1, 32-byte ASCII processor CID, chunk-list offset 64), 16-byte RF01 state and 28-byte List with one Comp entry (offset 48, size 16). Little endian. Compared with official SDK 3.8.0 public.sdk a3911a4615dabbfdfd9d181ee26b05c70c289a95 source/vst/vstpresetfile.cpp and recovered Windows moduleinfo CID 302FA8177F104E13BFC8A3EF4356888E. Strict reader deliberately recognizes only this generated layout. No claim of arbitrary preset support or corruption checksum. Actual DAW preset import remains untested.

Install the complete MHACReceiptFold.vst3 folder in C:\Program Files\Common Files\VST3 and rescan. Insert on an audio track, start with low monitor level. Import the presets via the host's VST3 preset loader if supported, or set controls manually as below (pair parameter rank lexicographic, normalized rank/27; modes absent/fixed/preview/full at 0,1/3,2/3,1). Preview and full recover identical quantized indices, not continuous input. No oversampling; discontinuity and aliasing intentional.

| Preset | Pair lo/hi | Receipt | Wet | Bypass |
|---|---|---|---|---|
| Selective Collapse | 0/7 | Absent | .35 | No |
| Ambiguous Parity | 2/6 | Fixed | .6 | No |
| Preview Recovery | 2/6 | Preview | .6 | No |
| Reference Quantizer | 2/6 | Full | .6 | No |
| Positive Fold | 4/7 | Absent | .8 | No |
| Negative Fold | 0/3 | Absent | .8 | No |
| Fixed Bit Witness | 1/6 | Fixed | 1 | No |
| Dry Reference | 2/6 | Full | 1 | Yes |

Probe: 48 kHz, 1-second log chirp 40 Hz–12 kHz, +/-0.9 FS stereo, 240 silent frames to settle the mix. Compare direct native processing to preset-restored Host with 127-frame blocks and final partial block. RMS and error RMS across both channels are signal measurements, not perceptual scores. Also single impulse and 1024 zero frames. GCC 14.2 Release CTest 5/5; Clang 17 ASan/UBSan preset probe passed; 896 RF01 roundtrips, 640 rejected structural mutations, 768000 paired stereo sweep frames, 16 zero-tail probes. Preview/full sweep metrics identical, dry error RMS zero. No callback timing or actual host tests. New-head Windows qualification outstanding. No SDK substitute or new license. Draft/HOLD, same-agent tests.
