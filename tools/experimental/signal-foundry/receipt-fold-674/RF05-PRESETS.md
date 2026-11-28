# RF05 preset bank — FX-009P (2026-11-27)

Refs #674 / draft #339 (f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64). Creative DSP interpretation; no human or scientific acceptance claim. No DSP, adapter or SDK pin changes.

Receipt Fold 0.4.0 binary source 760572c88c47da7d7faa8debd2ec52609d6cb9e4 passed Windows exact SDK build, official validator 47/47 with no explicit ERROR lines, and packaging (run 45912342287, artifact 15160901593, SHA256 c6a36c2e553a9728eed5b04c4102ec68d0097b2568b522b844203b8860deb5ce); integrity 45912342297 succeeded. Official tag v3.8.0_build_66 resolves to 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; all seven SDK-PIN.txt dependencies match the hosted checkout and freshly retrieved commit identities. Local checkout DNS blocked. No substitute.

Native reproduction:
```
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
# executable may be under build/Release on Windows
./build/receipt_fold_rf05_preset_probe output-dir legacy-preset-dir
```
Optional legacy directory must contain the previous canonical component-only preset files. Reader deliberately accepts only 92/96/104-byte containers, not arbitrary third-party presets. RF05 uses 48-byte header, 28-byte component payload and 28-byte list; no controller chunk. Older binaries cannot load RF05. Back up projects and copy complete bundle with DAW closed.

Eight RF05 candidates 26–33: coarse matching, balanced, preview, known-action reference, fine fast/slow, alternate geometry and dry reference. All use 80% wet; dry reference bypasses. One-second logarithmic sweep 40–12000 Hz at 48 kHz, 0.8 FS anti-phase stereo, measures peak/RMS/dry difference. GCC 14.2 CTest 16/16; Clang 17 ASan/UBSan direct probe passed; 1728 RF05 roundtrips, 608 rejected container mutations, 25 actual legacy presets compared to previous native single-pair engine, 3,168,000 paired stereo frames per full bank+legacy invocation across float32/64. Eight new preset files reproduced identically across the two builds. All previous presets kept unchanged. Native silence, state restoration and dry reference exact. Desktop DAW preset-file import, independent Windows 0.4.0 host comparisons, actual callback deadlines and subjective listening outstanding. Same-agent qualification, Draft/HOLD. No merge.
