# Joint spectral completion bounds v17

Refs #512 / cumulative Draft/HOLD #513, 2026-11-25. Parent e06897558d142d13cfad1200693bc96d40816550; main 495a98ca12bae467a507031f04931aa4254b1866. Single AI-assisted worker, no independent reviewer or human evidence. Additive diagnostic only. No wire, scheduler, frozen record, or authority changes.

## Model

For the fixed v16 clock/body window, let z be the observed Fourier sum, r its magnitude, H missing coordinates, M the assumed absolute missing-sample bound, and E observed energy. Projection onto z/r gives a lower magnitude bound max(0,r-M sum_H |projection(u_i,z/r)|). Triangle inequality gives upper r+|H|M. Intersect these with the previous rectangle bounds. For target and rival squared magnitudes L and U, a nonnegative difference L-U can be divided by the common maximum completed energy E+|H|M², rather than bounding two normalized scores independently. Keep the previous bound as an alternative. Energy gate and score threshold remain required. These are sufficient real-arithmetic inequalities; padded floating-point evaluation is not formal interval arithmetic. No missing sample read. Missing cap not inferred from data. Failure to certify is inconclusive. No association certification, authenticity, or receipt authority.

## Native results

Node 22.16.0 Linux: 5832 counted assertions, including 4650 exhaustive small completion decision checks across 90 quiet/tone windows (90 certificates; zero contradicted). Replayed 21 original v16 two-packet fixtures plus masked latent witness; 22 source hashes and stripped traces exact, alternative chunks 511/127 exact. No old certificate lost on the test corpus. Same 207 affected observations and 69 hypotheses, not independent packet trials.

| M (PCM counts) | v16 stable | v17 stable | v16 all-window hypotheses | v17 |
|---:|---:|---:|---:|---:|
|128|131|135|41|45|
|512|91|94|30|30|
|1024|90|90|30|30|
|4096|45|45|15|15|
|32768|0|0|0|0|

Modest improvement under small assumed caps; no unrestricted certificate. Latent indistinguishability witness remains uncertified at all caps. Post-frame association dependency remains unresolved. Three actual PCM scheduler sessions match strict-only waveform, trace, evidence and metrics exactly, with independent in-memory re-feeds; genuine confirmations 2/2/0, false 0/0/1. No throughput gain. No new audio stimuli beyond regenerated predecessor scenarios. 25 WAV files verified using Python (PCM16 mono 16 kHz, peak 4096, hashes); Chromium file selection, muted playhead and exact trace export passed with set_content fallback; ordinary file navigation blocked. No Windows, embedded, physical listening or human qualification. Full checkout DNS blocked. Native replay 10.90 s, peak RSS 130724 KiB on tested host; additional temporary O(n) missing-coordinate array per frequency. No claim of embedded suitability.

## Reproduce

From this directory run node test-joint-v17.cjs. If v16 receipt absent, it regenerates it using test-bounds-v16.cjs. Clean scratch directory regeneration was tested and produced byte-identical v17 receipt. Native-tested source blob IDs: joint-v17.cjs 87d7dd0d2e2ea4a34c4e24c0fde5d2d1c392032e, test-joint-v17.cjs b8dc80533082ae75c776c498f67f9c1ee8e3d55c. Both verified at 2fb3f3e11d9fd771374d4ecf1f43bff239c0084b. Eleven inherited source blobs matched pinned parent.

Upstream reconciliation: #443 272a9922996a858acd5661a6263dd669e4990736 (affine timing quantisation), #449 a126f8ffd9a14899a6d15d332696820d54461b6a (bounded quadratic observation sets), #453 7f06ab778df0c3d43f2bcad8bda5a7a70acb8d68 (integrity), #457 d70aa68fb60608efab8ff34089e8e3dc66fe2d11 (service debt), all draft with successful structural workflows at intake; respective reports inspected, no external code imported, repository root LICENSE lookup 404 (not a grant). Foundry PRs inventoried; FM-1 repositories read-only README compatibility review, no hardware work. Prior v16 structural check 45714518450 successful. Independent substantive review outstanding. Next: stop optimizing tiny-cap bounds absent a justified completion model; use diagnostic hypotheses for bounded clarification requests, explicitly not ACKs or actions, compare cost/latency and false-trigger debt.
