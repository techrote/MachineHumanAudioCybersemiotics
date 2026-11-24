# Instrumental proxy results (reproducible, fictional)

Data: `generated/SUMMARY.json` (SHA-256 input manifests and output PCM hashes); `python model.py` prints the complete 10 × 10 cue/transform features and **45 pair vectors per transform**. These are measured **on software-generated waveforms**, not people, rooms or devices. Predeclared diagnostics are engineering sensitivities without any validated perception thresholds.

| Condition | P_FAST vs P_SLOW pulse-group difference | F_LOW vs F_HIGH projection contrast (dB) | S_LEFT vs S_RIGHT ILD difference (dB; `null` means undefined) | P_ALT detected groups |
|---|---:|---:|---:|---:|
| Identity | 2 | 240.000 | 26.129 | 4 |
| Half gain | 2 | 240.000 | 26.129 | 4 |
| Mono fold-down | 2 | 240.000 | **null** | 4 |
| 13-tap lowpass FIR | 2 | 143.958 | 26.129 | **6** (artifactual extra groups) |
| 320-sample reflection | 2 | 240.000 | 26.129 | 4 |
| Masker | **0** | 240.000 | 24.297 | **1** |
| Fast compressor | 2 | 113.812 | 8.941 | **3** |
| Slow compressor | 2 | 138.253 | 14.474 | 4 |
| Hard noise gate | 2 | 240.000 | **null** | **2** |
| Mute | **0** | **null** | **null** | **0** |

**Interpretation by axis:** Masking destroys the predeclared pulse-count separation in this frame detector, despite the fact that physical signal energy still exists. Mono makes source-location *proxy* undefined and hashes the left/right fictional pair identically. Fast vs slow compression produce different *instrumental* ILD values, not a device-performance ranking. A severe FIR can create false frame transitions and can change spectral contrasts. The destructive mute is a negative control, not a realistic deployment condition.

**Explicit pair-ranking reversal:** before gating, `P_ALT` (4 detected pulse groups) equals `P_WIDE` (4) and differs from `P_SLOW` (2); after the `noise_gate`, `P_ALT` has 2 groups, matching `P_SLOW` and differing from `P_WIDE` (4). This is an actual inversion of the nearest neighbour under the predeclared frame-group proxy (adversarial case C25), **not** a human confusion estimate.

**Concrete non-monotonic countercase:** the `noise_gate` reduces `P_ALT` late-window RMS from **0.017678 to 0.000000**, which might look favorable for a silence-floor proxy, while simultaneously reducing detected pulse groups **4 → 2** by removing quiet pulses. This is not evidence that noise reduction improves perceived intelligibility. It specifically falsifies treating reduced background energy as an unqualified communication gain. A second countercase: processing may improve audibility in real studies (Kowalewski et al., 2020) while compromising temporal features in a toy diagnostic; neither outcome substitutes for the other.

**Limitations:** The projection ratio is bounded by a relative computational floor, so values around ±120 dB per source and ~240 dB between pure-tone pairs are numerical artifacts of the chosen bins, **not meaningful hearing dynamic ranges**. The gate is instantaneous, the FIR is a boxcar, and reflection is a single echo; no calibrated SPL, room impulse response, masking threshold, ITD, headphone, listener or manufacturer algorithm is modeled. Reproducible source separation says nothing about authentic source identity, consent, action or safety. See `DECISION.md`.
