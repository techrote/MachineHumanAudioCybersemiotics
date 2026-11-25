# Execution receipt

Date: 2026-11-25. Model executed in the available JavaScript tool environment (not a browser or Node runtime). The code generating the HTML's embedded makeModel function was executed before commit; the subsequent visual-only lever angle edit does not alter it.

- 262425 passed assertions; 140 visual schedules
- 156000 PCM16 mono frames, 24000 Hz, 6.5 seconds
- Peak magnitude: 15704; nonzero samples: 50042
- Word-wise FNV-style checksum: 8c880489 (not cryptographic; engine floating-point rounding may vary)
- Negative cases: unsupported body, out-of-range offset, invalid omission, nonfinite offset
- Reproduce: node check.cjs from this directory; compares repeated generation and enumerated schedules. Node reproduction not run here.
- Browser display, audio playback/export, actual timing, human reception, full repository validation, exact-head CI and independent review remain unverified.

## Native follow-up, same committed source

- Local Git blob hashes matched the retrieved index.html (be87301f4100fec3675cffd18138cd414e1c7575) and check.cjs (d8f9dd522c05fc63bca73f8061b9cc47021f57cd).
- Node v22.16.0: exact same 262425 checks, frame count, peak, nonzero count and checksum.
- Headless Chromium 144.0.7559.96 via Playwright: local file navigation was refused by the environment; the exact HTML was loaded as test markup instead. Muted playback exercised four bodies, zero and +150 ms lag, omission of contact 4, stop/restart and natural completion. AudioContext running state and UI contact counts confirmed; no page errors. Four WAV exports matched byte-for-byte. Python wave readback: mono PCM16, 24000 Hz, 156000 frames. SHA-256 f7f7e7958c053d3d1732c6430aff63ba0fa62d80a3e1037a135e0ff32f4500ef.
- Screenshots inspected for stage and timing lanes. Physical sound output, audible quality, actual audiovisual latency, file-URL navigation, Firefox/Windows and human reception remain unverified. This is software smoke qualification only.
