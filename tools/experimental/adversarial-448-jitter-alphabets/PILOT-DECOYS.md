# Pilot decoys — Adversarial #448/#449, Run 068

Synthetic cross-lane falsification of Measurement #443 at 2dab493e14107adb2fefce097aba59a13026d2a4 (acquisition-rank.py), transport at 8656394a04100f9dd6d835397cd2831f58356b36 (selective-transport.py). Both are SHA-256 pinned by the executable. Main at intake 495a98ca12bae467a507031f04931aa4254b1866. Draft/HOLD; independent review remains with Mergedown.

Run with Python 3.13.5 / NumPy 2.3.5: OPENBLAS_NUM_THREADS=1 python pilot-decoys.py acquisition-rank.py selective-transport.py NEW_OUTPUT. Seed 4480681. Continuous white noise across capture including padding, random carrier phase, off-grid integer-sample arrival, fixed frame ID and capture length. Target peak 1600 counts, noise RMS 1000 counts, competing pilot amplitude 800/1600/2400 counts. Matched target and noise, not total energy. Compare pinned one-best acquisition to four non-max-suppressed candidates (2 ms / 20 Hz radius), withholding on multiple distinct CRC-valid values. Oracle knows actual timing, frequency and presence. No equal CPU budget.

54 fixtures each; correct/wrong/withheld:

| Condition | Pinned | Bounded4 | Oracle |
|---|---|---|---|
| Target | 54/0/0 | 54/0/0 | 54/0/0 |
| Pilot only | 0/0/54 | 0/0/54 | 0/0/54 |
| Decoy 800 | 54/0/0 | 54/0/0 | 54/0/0 |
| Decoy 1600 | 27/0/27 | 54/0/0 | 54/0/0 |
| Decoy 2400 | 2/0/52 | 13/0/41 | 45/0/9 |
| Stale only | 0/54/0 | 0/54/0 | 0/0/54 |
| Target and stale | 16/17/21 | 3/3/48 | 32/0/22 |
| Noise only | 0/0/54 | 0/0/54 | 0/0/54 |

432 matched PCM groups, 1296 policy decisions, 24 group recounts; all verified twice, byte-identical output directories. Nine WAVs at common 0.25 scale, maximum peak 1587 counts; opt-in playback. Frame 2 decoy2400: first candidate (-32 samples,+70 Hz) rejects, third (+48 samples,-50 Hz) recovers [2,92]. This is bounded recovery of weaker pilot, not proof of robust synchronization. Same-ID stale header is deliberately valid: failure of freshness, not random noise corruption; oracle uses presence information unavailable to real receiver. Stronger candidate search trades false admission for withholding in competing valid packets. No body, streaming, authentication, physical transport, human evidence or whole-repo local qualification. Direct Git DNS failed; use guarded connector publication only. Next: independent stream-liveness suspension/reacquisition from Run064 remains open; Measurement should address freshness and pilot decoy resource limits before adopting bounded4. No shared or frozen changes.
