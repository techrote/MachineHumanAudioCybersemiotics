# RF03 preset and upgrade qualification — FX-009H

Refs #674, #338/#339 (f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64 §§2–3). Direct restricted pair-collapse index law; creative audio rendering. Offline utility, not a new audio callback or scientific claim.

Windows 0.2.0 exact source 320e1cdf6594be64177e0702ee6786f250b42b0a, run 45851452153, artifact 15132659258, strict validator 47/47 with no explicit errors; integrity 45851452107 succeeded. SDK 3.8.0 tag v3.8.0_build_66 re-resolved to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; all seven archived recursive gitlinks match SDK-PIN.txt. Windows x64 binary SHA256 baa7307a7777215b51645f48286fb70aa3e81c71363ebe8e9eed2cfff0834158. Independent lane #633 run 45853698810 has a successful Receipt Fold legacy migration/extended transfer step; overall run failed on Three Winters, not Receipt Fold. See artifact 15134612214, receipt-upgrade/receipt-upgrade.json. No DAW preset-file import or listening claim.

## Build and use

Run the existing native CMake/CTest instructions; receipt_fold_rf03_preset_probe OUTPUT_DIR creates nine minimal 92-byte component-only VST3 preset candidates and sweep.csv. The existing RF01 tool and presets remain unchanged. New presets use RF03 and require 0.2.0 or newer. Save project backups before replacing the bundle; older versions do not load RF03. Do not install two bundles sharing the same CIDs.

09–17: Coarse Collapse, Fine Distortion, Budget Ambiguity, Budget Witness, Preview Recovery, Full Reference, Adjacent Expansion, Legacy Geometry, Dry Reference. Compare 11/12/13/14 at identical endpoints and wet levels: 4 low bits collide for 96/176; 5 distinguish them, as do preview/full. The 15 upper-edge coincident pair exercises the adjacent expansion rule. Dry is bypass. File structure is the pinned SDK component-only format already used for RF01; the strict reader only accepts this generator's canonical layout. It is not a general VST3 preset parser or a checksum.

## Verification

GCC 14.2 Linux Release CTest 8/8; Clang 17 ASan/UBSan direct RF03 regression PASS. 864 RF03 roundtrips and normalized control rebuilds, 28 RF01 migrations, 720 structural mutations rejected, 864000 paired stereo sweep frames (float32/64), 18 zero-tail probes; budget witness/preview/full identical measured sweep energy and error, dry error zero. No DSP, adapter, ID, SDK pin or shared workflow changes. Actual host preset import, callback deadline distribution and listening still outstanding. New-head CI not claimed complete. Local SDK DNS blocked; no substitute. Same-agent source implementation and native qualification; independent host evidence attributed to #633, not independent human or scientific review.
