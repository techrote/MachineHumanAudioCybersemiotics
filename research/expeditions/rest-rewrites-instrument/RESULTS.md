# Qualification ledger — 2026-11-24

Executed by ChatGPT, no independent human evaluation.

* Base: 495a98ca12bae467a507031f04931aa4254b1866.
* lab.js blob dc11c95b58324fd9134ec917549e90580d4400b4; executed in V8 before committing and from retrieved source after replacing the final console log with a return of the same experiment. Both returned identical counts: 365 configurations, 374648 allocations, 130923 residue vectors, 506845 assertions.
* render.py blob 3c266eb0d34fb2be4ae7a45d039fcad731c0155c; local executed blob equals GitHub-fetched blob. Four WAVs generated and reopened, deterministic duplicate PCM synthesis, 16 attack-block frequency/peak checks, every declared gap digital-zero check, mono 16-bit 24000 Hz, 105600 frames each. No physical playback/listening verified.

| WAV | SHA256 (local render; platform math library may affect rounding) |
|---|---|
| concentrated.wav | 075a555a95059e5104f96b991d2c4454c16d165e0de6f83721f3ae24d2f669f6 |
| distributed.wav | fa0ac641a6bc450f67ac758cfe2f90f7eb36df78a088813a04787d7f13b9d911 |
| deferred.wav | daf6ef4d4fc858c1d3995f3ac19fcc9222863cd4e430b002bc5993921e2ce5e7 |
| frozen.wav | 0c64e0ebc3ff067ac9a138fbf60a927c16226c0c4467967f535b71c40b1794ef |

Run node lab.js and python render.py from the expedition directory. Audio files are generated, not tracked. The renderer writes files adjacent to itself; use a disposable copy if desired. No full repository CI claim; inspect exact final head before landing. No changes to protocol, live research records, or shared manifests.
