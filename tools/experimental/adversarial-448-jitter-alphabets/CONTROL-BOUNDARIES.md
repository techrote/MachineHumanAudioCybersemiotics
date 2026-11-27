# Adversarial control boundaries (Run 065, 27 November 2026)

Refs #448/#449; read-only comparator Measurement #442/#443 at 8656394a04100f9dd6d835397cd2831f58356b36. Main intake 495a98ca12bae467a507031f04931aa4254b1866; parent 51ce672ea807bfbccad67237cb32bae3648df9fb. Both predecessor integrity workflows completed successfully (46022836431 and 46029567765).

Run with Python 3.13.5 / NumPy 2.3.5: OPENBLAS_NUM_THREADS=1 python control-boundaries.py PATH_TO_SELECTIVE_TRANSPORT NEW_OUT. The input SHA-256 is checked in source. AI-assisted exploratory synthetic test; independent acceptance outstanding.

54 identities × 4 additive frequency offsets × 7 integer arrival offsets = 1512 captures, 3024 decisions. Fixed alignment correct 335, withheld 1177; oracle correct 756, withheld 756. Zero accepted wrong tags in this grid. At +27 Hz, fixed 54/54 at zero delay, 49/54 at -2 ms, 51/54 at +2 ms, 0/54 at ±5 ms. At 50 and 75 Hz, even exact alignment recovers 0/54. Same per-frame noise across all shifts and delays; oracle is supplied arrival position, not blind acquisition. Delays use zero padding, not continuous clock error.

All 5832 frame/meaning combinations enumerated; four distinct same-frame 16-bit fingerprint collision pairs found (frames 4,20,41,44). All four alternate bodies pass the original direct qualifier checks and exact intended fingerprint after clean PCM rendering, without modifying header. Frame 4: [1,0,1,2,0] vs [3,0,1,0,0], tag [76,221]. This is an intentionally chosen finite-domain collision, not a natural channel-error rate; the test is an isolated header/body admission predicate, not a complete end-to-end exchange.

Executed repeated exports byte-identical (9 files); separate 56 group recounts, 1512 matched input hashes and manifest verified. Five WAVs common 0.25 scaling, max 1031 PCM counts. Browser runtime, native full repository validation, physical transport and human evidence unqualified. Direct git DNS failed. No merge, external publication, gate or shared edits.

Next Adversarial: retain Run064 suspension/reacquisition work; challenge synchronization, finite-domain tag protection and mixed faults under matched work. Measurement: integrity-triggered full replacement, fresh initial stimuli and explicit timing acquisition.
