# MHAC Reset Choir 0.1.0 — experimental instrument
Refs #484; research #424 / draft #425 at 6e94988ab4e6efb4779f4483983a3761e94b2c4b, research/expeditions/reset-score-424/README.md, Model and result / Proof: reverse records / minimum cost. The eight-register compiler is a direct finite realization; mapping registers to pitched harmonic levels is a creative choice, not a validated perceptual hypothesis.

## Play
A note triggers a balanced sequence of 16–40 broadcast +/- commands. Registers of capacities 1–8 clip at their bounds, eventually reaching the requested score regardless of initial values. Eight harmonics follow normalized register states with 5 ms slew. The final spectrum sustains until note-off; 5 ms attack and 20 ms release, 16 voices, excess notes rejected rather than stolen. No input audio. Mono or dual-mono stereo. Harmonics taper between 0.40 and 0.45 of sample rate; soft bounded output <= 0.5 FS. Extreme sample rates are accepted but pitches above the anti-alias band may be silent. No pitch bend, sustain pedal, custom GUI, or tempo sync yet.

| Control | Normalized value / behavior |
|---|---|
| Target score | 0..255 discrete mask, divided by 255; each LSB-first bit sets the increment of a target register |
| Initial spectral fill | 0..1; each register starts at nearest integer fraction of capacity |
| Step interval | 15..120 ms, captured at note-on |
| Spectral colour | 0..1; dark 1/h^2 to flat harmonic weights before anti-alias taper |
| Gain | 0..1 global smoothed level |

Score, initial fill, interval and colour are captured per note; gain is live. Parameter IDs 300–304, state RC01 little-endian Q24, no transient voice state. Suggested patches (normalized): Converging Dark [85/255,0,.25,.2,.7]; Converging Bright [85/255,1,.25,.8,.7]; Ascending Organ [1,.5,.25,.8,.7]; Vanishing [0,1,.5,.7,.7]. To compare convergence, keep every control identical except initial fill; hold the same note at least 5 seconds. The 0 score converges to silence. Different scores are not guaranteed distinguishable for human listeners or at all pitches/rates.

## Build and audition
Standalone: cmake -S . -B build-core; cmake --build build-core --config Release; ctest --test-dir build-core -C Release --output-on-failure. Run choir_test (on Windows build-core/Release/choir_test.exe) with any argument in a writable directory to generate three original WAVs. Recipes: MIDI 48, velocity .8, interval normalized .25, colour .8, gain .7; 3 s at 48 kHz, release at 2.75 s. Two alternating profiles use seed 0 or 1, third ascending mask 255 seed .5.

Native plugin: checkout official SDK tag v3.8.0_build_66 and immutable root 9fad9770f2ae8542ab1a548a68c1ad1ac690abe0; initialize all recorded gitlinks recursively, do not update to other revisions. CMake rejects a wrong root, absent/mismatched recursive gitlinks and dirty checkout. Configure -DMHAC_BUILD_VST3=ON -DMHAC_VST3_SDK=/absolute/sdk/path, build Release target MHACResetChoir and validator. Scoped Windows workflow builds and validates exact source and packages notices. If qualified, extract entire MHACResetChoir.vst3 folder to C:\Program Files\Common Files\VST3, rescan in DAW, load MHAC Reset Choir on instrument track. Use host parameter editor. No installer required. Native plugin availability/compatibility is gated by actual build and validator receipts; see QUALIFICATION.md and exact-head CI. No physical DAW audition yet. Linux/macOS intended, not plugin-qualified.
