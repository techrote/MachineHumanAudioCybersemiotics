# FX-011V — Budget Performance bank (Refs #748)

Additive original audition material for Harmonic Memory Bank 0.3.0, not a new plugin or research result. Same component ID, HM02 state and automation IDs as FX-011U. Five 121-byte component-only VST3 preset candidates, each using the same four frequencies (110/165/220/330 Hz), gain 80%, peak mix 100%, selectivity 17.7/44.8/71.9/99.0% and wet 100%. Budget and objective differ. Capture starts open; the preset does not save memories or momentary commands. Existing four HM01 presets and legacy audio paths remain intact.

| Preset | Budget | Objective | Selected bands in fixture |
|---|---:|---|---|
| 01 Persistent Quartet | 0 | Count | None |
| 02 Count Cut | 4 | Count | 3, 4 |
| 03 Energy Cut | 4 | Energy | 2 |
| 04 Half Budget | 8 | Energy | 1, 2 |
| 05 Full Erasure | 16 | Energy | 1, 2, 3, 4 (12 reserved) |

Use a 48 kHz stereo session, load a preset with processing stopped or reset, place Excitation.wav at sample zero and leave track/fader/input gain unity. Use step automation: all four Capture parameters to 0 at sample 12000 (250 ms); Admit budgeted erase to 1 at sample 24000 (500 ms), back to 0 at sample 24001. Keep other erase commands off. automation.csv carries exact normalized IDs/offsets; it is a reference, not an automatic DAW session import. If the host cannot provide one-sample automation, return to zero later without issuing other commands. To compare, reset/reload before each take. Reference audio is attenuated by 0.5 with short external start/end fades for safe audition; this is not a change to the effect or an exact gain-matched desktop DAW render. Persistent memories can continue indefinitely: lower monitoring gain and reset after audition.

Native generation: build with the existing CMake project and run counterfactual_bank_performance without arguments (CTest), or pass an output directory containing empty Presets and Audio subdirectories. Generator checks 34 budget/objective roundtrips and rejects 83 single-byte header/chunk/state mutations. Five 144000-frame stereo renders compare direct DSP with native Host state restore and 257-frame vs single-sample processing, sample exact. For the fixture, budget 4 count-first chooses mask 12 (two bands, energy 32) while energy-first chooses mask 2 (one band, energy 64). Energy means integer squared lattice coordinates, not RMS or perceived loudness. Full erasure has exact final 50 ms silence. Original 117/168 Hz input is PCM16-representable, 48 kHz, three seconds including silence; outputs are original native stereo PCM16. GCC 14.2 and Clang 17 ASan/UBSan pass, all 12 generated files byte-identical. Native comparison uses the same implementation, not independent scientific validation. Windows candidate build and actual desktop preset import remain gates. No new SDK dependency or substituted SDK; pinned 3.8.0 notices retained. Draft/HOLD.
