# Pilot acquisition and finite-domain rank — Run 067

Refs #442/#443; synthetic-only, Draft/HOLD. AI-assisted implementation and self-check, not independent acceptance. Comparator: selective-transport.py at 8656394a04100f9dd6d835397cd2831f58356b36 (SHA-256 2f79f974bc6292cc224ad16660f2a98b6331fbfad49cb69cc5512f5b603002cf); adversarial witness b1430d799ea2858f0b548705b4e2d3289e98711e. Accepted main at intake 495a98ca12bae467a507031f04931aa4254b1866.

Run: OPENBLAS_NUM_THREADS=1 python acquisition-rank.py selective-transport.py NEW_OUTPUT. Seed 4426701. Bounded joint delay/frequency search, three known pilot tones, threshold 600 PCM counts for weakest pilot component. 21 arrival candidates x 17 frequency candidates; fixed and oracle comparators share exact captures. Noise 1000 PCM counts RMS, 1600 peak nominal, 16 kHz. Per format 1512 target captures plus 54 absent controls; fixed/oracle/pilot decisions. Noise is reused across timing/drift conditions; counts are not independent error probability estimates.

| Header | Fixed correct | Pilot correct | Oracle correct | Wrong (all policies) | Duration with pilot |
|---|---:|---:|---:|---:|---:|
| Hash16 | 333/1512 | 1512/1512 | 1512/1512 | 0 | 220 ms |
| Rank7 | 346/1512 | 1512/1512 | 1512/1512 | 0 | 180 ms |

All 324 absent decisions withheld. At each of 28 target conditions both pilot receivers recover 54/54. Rank is the lexicographic index in the 108-element fixed-depth domain, transmitted in one byte. The four previously found hash collisions are independently enumerated and have distinct rank values. This does not authenticate the sender or protect untested recursive domains. This experiment qualifies header recovery only, not body admission, full retry, arbitrary timing, or blind continuous streams. Capture lengths and expected frame IDs supplied. Padding is zero, not continuous interference. No equal-energy or CPU-parity claim. No physical or human evidence.

Local execution: 9396 status replays, 3132 matched capture hashes, 174 aggregate checks, repeated output byte equality, 3 inherited symbolic unit tests. Two original scaled PCM WAV examples, offline HTML, trace and receipt hashes emitted. Direct git DNS unavailable; exact connector readback required before guarded update. No merge or shared manifests.
