# Execution receipt

Date: 2026-11-25. Model executed in the available JavaScript tool environment (not a browser or Node runtime). The code generating the HTML's embedded makeModel function was executed before commit; the subsequent visual-only lever angle edit does not alter it.

- 262425 passed assertions; 140 visual schedules
- 156000 PCM16 mono frames, 24000 Hz, 6.5 seconds
- Peak magnitude: 15704; nonzero samples: 50042
- Word-wise FNV-style checksum: 8c880489 (not cryptographic; engine floating-point rounding may vary)
- Negative cases: unsupported body, out-of-range offset, invalid omission, nonfinite offset
- Reproduce: node check.cjs from this directory; compares repeated generation and enumerated schedules. Node reproduction not run here.
- Browser display, audio playback/export, actual timing, human reception, full repository validation, exact-head CI and independent review remain unverified.
