# Bounded out-of-order receipt v32 — Refs #512 / Draft-HOLD

AI-assisted GPT-6.2, 2026-11-26. Synthetic experimental integration; no human, hardware or production claim. Parent 60af5af94f3d029912662339d081311af7372832; main 495a98ca12bae467a507031f04931aa4254b1866. v30/v31 unchanged. New receiver is a separately retained v30 fork; window=2 accepts an unseen generation at most two below highest recorded for that source/epoch. Exact duplicates and conflicting same-key payloads are checked first. Four records per epoch, eight total, no eviction within active epoch, 8 KiB input limit, local closure grants and isolated replay credits unchanged. Forward leaps remain admissible. No wire change. Gap evidence is implicit in exact records, not cumulative ACK or a moving eviction window.

## Native matched corpus

Run `node reorder-v32.cjs reorder-v32-output` and `node test-reorder-v32.cjs reorder-v32-controls` in this directory under Linux/WSL with Node 22.16.0; no dependencies. Seeds 71/113. The scheduler forks v31, unchanged timing, offers, horizon, losses and queue bounds; the window policy uses response-first scheduling. 20 old baseline rows reproduced exactly including WAV SHA-256. 30 scheduled sessions, 1196 counted checks, 528 PCM comparisons via 70 actual acquisitions with bounded exact-byte memoization. 20 standalone sessions, 340 checks, 144 uncached exported slot rescans. All 50 WAVs independently verified (16 kHz mono signed 16-bit PCM, peak 4095 counts).

| Policy | Confirmed / 56 | Old settlements / 20 | Occupied slot seconds across 10 sessions |
|---|---:|---:|---:|
| Response-first | 48 | 20 | 615.296 |
| Ordered response-first | 52 | 20 | 608.304 |
| Window response-first | 54 | 20 | 622.288 |

Pressure: older C/newer E confirmation seconds: strict none/41.952, ordered 55.936/62.928, window 62.928/41.952. Recoverable loss: none/48.944, 73.416/80.408, 80.408/48.944. Persistent C loss: E confirmed 41.952 by strict and window, not by ordered. Same 104.88 s horizon per session; occupied slot time includes guards, not physical audio duration. No universal ranking.

## Negative controls

Actual PCM gap fill, exact duplicate after reopen, conflicting same identity, inclusive distance two versus outside distance three, capacity refusal and public future-generation poisoning all reproduced. Order-dependent evaluator witness: generation 1 stopped arrives before generation 0 open; window accepts both, arrival-order assignment yields open while occurrence-order assignment yields stopped. This evaluator-only state assignment is not a real device action. The durable receiver commits a counter, not an ordered application engine. Transport admissibility cannot establish safe semantic execution. Distinguish independent events, superseding state and ordered effects. No power-loss, concurrent writer, rollback resistance, authentication or distributed arbitration qualification.

## Cross-lane context

Refreshed draft pins: measurement #443 0f95cd4514202521058e6ce43518a8a71e0124a0 (candidate-retention.py); adversarial #449 5efb84b938c2bf69f11ef3c5864221f041077c3b (migration-faults.py); grammar #453 f215e18d8cbcbaa7c19fd5f199cd69bb510c1c22 (transaction-leases.cjs); interaction #457 c391e0c5bd1cfe6a8c5e44c05decb83849ad153d (gap-repair.py, service-debt.js). All four exact-head structural workflows completed successfully; prior #513 structural workflow passed. No repository-wide license declared, no upstream code imported. Interaction gap-repair buffers until contiguous floor before applying ordered tile effects; this experiment deliberately preserves a different approach, immediate application of a commutative counter after exact receipt. FM-1-MHAC main 16c698d9e244559064a9a9a22f834d36912bf498 and FM-1-CYDaux main e65a0b880b5c13c9aa3ce734c6e3eaa4b11fc969 inspected read-only (README; hardware unqualified).

Native elapsed 8.61 s scheduler / 15.01 s controls; max RSS 130904 / 126292 KiB. Local inspector tested in Chromium with document injection after ordinary file navigation blocked by administrator policy; file selection, waveform, muted playhead and exact paired JSON export passed. Windows and physical listening unqualified. Receipt SHA-256 scheduled aef37f1c847e4fb9eb16fe8b4b7c40e2ead47d67826a5419fcf2f05f464933fb; controls adb35bfc921f8b2433bab136213ae903bdf252eee819d84993ec38b271da8092. Local distribution carries WAVs and receipts. Next: compare selective receipt against ordered commit and version-aware supersession, with missing dependency deadlines. Independent review and exact-head checks remain required. No merge or frozen/shared changes.
