# INST-010I — Phase Memory host integration (candidate 0.3.0)

Refs #680, #338/#339 (f8b9bddd89c2d174b28f060bf34b42d2ca9a0e64, sections 2–3). Creative synthesis extension of the finite receipt model, not an empirical or scientific acceptance claim. Parent 8b6648c50fc9c014e128f7135e39ee3846e09b42. Single AI implementer, same-agent native tests.

## Control and compatibility

Parameter 1606 Phase memory mix is a four-position automatable control (normalized 0, 1/3, 2/3, 1). The four steps deliberately fit the last two reserved bits of the existing atomic patch word. Effective PM blend equals this value times memory influence and the carrier's Nyquist taper. Capture at note-on, including simultaneous automation before note events; existing notes and forced fades retain their original blend. All previous IDs and both CIDs are unchanged. AC01/AC02 patches continue to decode and encode byte-identically when phase mix is zero. AC03 (still eight bytes) requires nonzero bits 30–31; mismatched format/version and invalid old reserved bits are rejected. Older plugins cannot read AC03; keep project backups. History/cancel are transient. A reset clears performance history but preserves patch controls. No SDK version substitution.

## Reproduce

```
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

Run `afterimage_phase_host_test --render <existing-dir>` for four original four-second mono WAVs using the same note score and identical receipts. Run `afterimage_preset_bank <dir>` for 13 component-only VST3 preset candidates (ten previous files unchanged). Start with Archive Choir, Phase Veil, Phase Alloy, Phase Archive; notes 57,59,62,48,60,61,62,48, 375 ms held per note, 500 ms spacing, velocity .85, full receipt, zero minimum, memory 100%, depth 3. The native score cancels every fourth release; in a DAW automate cancel gate at these release offsets or use ordinary releases for free playing. Preset files do not include the transient history. Actual desktop DAW preset import remains untested.

Use `afterimage_phase_host_test --bench` in a Release build for the native timing stress test (eight sustained voices, eight replacements every ~6 ms, mixed phase level 2, up to sixteen oscillator banks, 2 s per rate/block combination). Reports per-block elapsed wall time as percent of its audio duration; this is not a real-time host test. Native Linux measurement exhibited individual deadline overruns, including at 96 kHz; do not claim real-time deadline qualification. Next optimize oscillator cost/transition admission and measure on native Windows host. Existing official SDK lock and strict Windows workflow are unchanged. Local SDK retrieval blocked by DNS; adapter compilation/validator on this revision pending.
