# Candidate-aware rearm v9

Refs #512 / draft #513; 2026-11-25; AI-assisted single-agent experimental integration, no human or independent review. Parent f001f6b2f39428eb4c9c174fa2b001ad3cb2332e, base 495a98ca12bae467a507031f04931aa4254b1866. AGENTS/RAG, programme/runbook, integrity, validation, experiments and human gates read; issue #512 and all comments read. Up to 100 search entries per open issue/PR query (connector returned overlapping lists); active integration branch verified. Parent and current upstream exact-head Research integrity success: #443 01adf34a0c6cfd879b7e07ca8ebfe3491d142ef5; #449 14ec1dba7560f34b0c16f6c35813e860f490ac0e; #453 09bba7545e3cfb5b469eca46b50ccb8e9da338f5; #457 c0db9ebcada623ad466f30ff298df25706e187f7. Other lane titles inventoried; not requalified or imported. Read #449 history-budget-audit.cjs in full at pinned head. Root LICENSE not found; no upstream code vendored or license granted. FM-1-MHAC / FM-1-CYDaux README read-only on main (blobs 339ab507dca807a2c41f5cf20d8bfb24d23eb890, 8545f692f180068af15f4a076255500b4408b1a8); no firmware writes or hardware claims.

## Mechanism

While overloaded, use a separate bounded observer of the existing ordered preamble, with the v4 13 clock hypotheses, energy/correlation thresholds and 16-sample scan stride. A hit is not a valid packet. Wait 1600 samples (100 ms) since overflow or latest observed preamble hit, then rearm with the most recent 4096 samples (256 ms); no evidence backdating or EOF flush, full v4 validation unchanged. Observer is seeded with the last 1024 observed samples. Candidate history allocation 8192 bytes plus 4096-byte mirrored observer ring and 153600-byte receiver ring = 165888 bytes of PCM storage while overloaded, excluding runtime/transient allocations; worst-case observer recurrence work bounded by about 8.45 million steps per second of blocked input, not an embedded CPU qualification. New receiver is an additive v8 adapter and uses existing deadline-epoch-v8 scheduler hooks. Compare same 4096 history with blind 20 ms cooldown, as well as 1920 samples, v8 history, fresh cooldown and peak512. Does not establish silence, channel availability, authenticity, semantic restoration or resolution.

## Native synthetic outcomes

Run node test-candidate-v9.cjs candidate-v9-output. Node 22.16.0 Linux x86_64; 516 assertions, 20 stress waveforms x six policies, 12 scheduler sessions, 12/12 exact exported PCM event rescans, candidate stress chunk sizes 127 and 511 equal. Independent Python checks 32/32 WAV files SHA256, 16 kHz mono PCM16 formats, peak <=4096 counts. Timed corpus execution 13.17 s / max RSS 69484 KiB on host only. Reused v8 inspector displays 132 records; Chromium 144 native local file selection, muted media playhead and trace export/reread passed using set_content in fresh page after ordinary file URL blocked by administrator. Windows, physical audition, embedded real-time, full checkout (GitHub DNS failure), independent review outstanding.

Exact intended sequence recoveries per condition (boundary 12 trials, remaining columns 2 each):

| Policy | Boundary | Early weak | 45 dense preambles | 70 dense preambles | 100 sparse preambles |
|---|---:|---:|---:|---:|---:|
| Cooldown | 2 | 2 | 2 | 0 | 0 |
| History640 | 6 | 2 | 0 | 0 | 0 |
| Peak512 | 0 | 0 | 2 | 2 | 2 |
| Fixed1920 | 12 | 2 | 0 | 0 | 0 |
| Fixed4096 | 12 | 2 | 0 | 0 | 0 |
| Candidate | 12 | 2 | 2 | 2 | 0 |

Boundary seeds 29473/85159 intentionally reproduce #449, not held out; offsets -960/-640/-480/-320/0/+320. First five seed-29473 hashes exactly match published upstream values. On that overlapping ten-trial subset history640 4/10, fixed1920 10/10, reproducing the key comparison. Long-45 uses B rather than upstream A, so not a byte-identical reproduction. Longer history alone worsens reset exhaustion; same-history candidate comparison isolates the new waiting rule at 4096. With 70 dense partial preambles (80 ms onset spacing), seed 29473 candidate overflow 11594, rearm 90932, accepted B at 146286; fixed4096 exhausts by 42306. New counterexample: 100 partial preambles spaced 160 ms. Candidate exhausts four rearms by overflow 103746, whereas peak512 rearms at 262395 and accepts B at 312677. The observer's lack of recent hits is not evidence of an end to sustained interference. No universal policy winner. No unexpected accepted packet identity in stress trials. Keep counterexamples rather than fit timing constants.

Scheduler clean, ack-loss+overload, revision+overload: two genuine confirmations each in history, fixed4096 and candidate; each has one false confirmation in forged. No aggregate interaction improvement over v8 on these workloads. Interference replacement is slot-relative; stress waveforms are strictly matched across policies. Preserve known checksum collision, mixed timing and forged ACK limitations. No shared manifests, frozen records or other branches changed. Package uses original generated WAVs and existing epoch-v8-inspector.html; choose candidate-v9-output/receipt.json and matching WAV files. Start at low device volume; no human perception claim.

Next: measure admission and recovery over onset density / candidate confidence distributions with fixed recovery budget; explicit host discontinuity and terminal uncertainty semantics; investigate retaining selected hypotheses without replaying the entire overload tail. Draft/HOLD, no merge.
