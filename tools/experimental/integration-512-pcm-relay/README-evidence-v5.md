# Evidence-clock relay v5 — causal return scheduling

Refs #512; cumulative Draft/HOLD #513. 2026-11-25. Synthetic engineering, not production or human evidence. One AI agent, no subagents. No canonical records, licences, other branches or firmware repositories edited.

## Reconciliation and provenance

Main 495a98ca12bae467a507031f04931aa4254b1866; parent 45c8f1b1432172d70ec5b05716150c5ec2a5a894, exact-head Research integrity run 45595943947 successful. Read AGENTS, RAG, programme, runbook, experiments, human gates, #512 and its six comments, first 100 open issues and PRs, scoped branch search. User-authorized experimental integration remains separate from the frozen research programme. No merge or self-approval.

The local predecessor archive's relay.cjs, bound-v2.cjs, scheduled-v2.cjs and stream-v4.cjs Git blob hashes match those fetched at the exact parent: 3ba457f85f496e4d57d9789a2dc3b7d68fe2c071, 2aa2905d4f4d756276814d5ca941c02c51e63f97, 60983bd9369729fb7dcc8f548c5371a74d02c7aa, 31769f808469b4416412be25a41eb238bfc1fdde. Only the existing integration wire and Stream are executable dependencies. This new runner adapts its scenario and channel conventions from scheduled-v2, without modifying it.

Refreshed draft PR metadata, exact-ref READMEs (relevant model/contract sections), and successful exact-head workflows: Measurement #443 8b562f603acb1c621d701d8aaeff8369e5439bec (45599024815); Adversarial #449 705278b95b576d4434e131b7317dda0d63f8f575 (45602650442); Grammar #453 47b99f00cda01cf9a30b0c3ad5a7337667f2a06f (45604059147); Interaction #457 52b72a2a6c76ba084dab6291cbeb5f97c7ac45b1 (45597048520). Foundry intake metadata only: #543 7487d3dfd1398af70a49926ed974efa52f6bc468, #537 6652aac19a2be3342bd78f9edfaaf710d2c118a3; their two workflow runs each succeeded. No foundry DSP reused: it would change the controlled receiver comparison. No new upstream code imported. Draft results are not accepted science. Root LICENSE not found at main. FM-1-MHAC README at 16c698d9e244559064a9a9a22f834d36912bf498 and FM-1-CYDaux README at e65a0b880b5c13c9aa3ce734c6e3eaa4b11fc969 read; LICENSE requests returned 404. No license grant inferred, no third-party import or firmware writes.

## Contract

The v4 receiver previously emitted successful interpretations 426–538 samples after old 32,000-sample slot boundaries. In v5 actual Stream callbacks drive the receiver's receipt decision and ACK queue, and recovered ACKs drive the sender ledger. No slotReceiver or future PCM is passed into decisions. Shared nominal transmit epoch grid, simulated context and route policy remain out of band; onset and content come from PCM. Queue readiness is max(actual evidence timestamp, inferred epoch + delay periods); expiry is inferred epoch + TTL periods. Current revision offers occur at fixed wall-clock sample indices, before evidence at the same index. Every non-fixture return has prior accepted evidence; evaluator receipt history is consulted only after sender acceptance. Fixture forgeries are explicitly injected, not trusted receipts. No action or resolution asserted.

Compare 0 versus 640 additional guard samples (0/40 ms) on a common 320,000-sample (20 s) horizon, 16 kHz mono PCM16, 31,360-sample packet, 32,000-sample transmit window. 10 versus 9 opportunities; idle and tail time consume budget. Both use the same offered workload, deterministic channel fault rules and two attempts/record, four pending returns. Delay, TTL and retry timeout are in periods, so guard changes those absolute durations as well: this is a comparison of two timing contracts, not isolated causal attribution to silence alone. Eleven cases x three policies x two guards. Revision fixture has one new A offer at 2 s (not the older v3 four-offer revision); no direct aggregate comparison to v3. Cases: clean, data/ACK loss, persistent loss, drift, delayed return, expiry, revision, matching forgery, wrong actor, replay. Previous mixed-fault and splice witnesses remain in v4/v2; this narrower suite is not their replacement. Phase and offset are deterministic by opportunity index, not randomized or byte-matched across differently scheduled messages.

## Native results

| Policy | Extra guard ms | Offered | Genuine confirmed | Retries | Late releases | False confirmations |
|---|---:|---:|---:|---:|---:|---:|
| data-first | 0 | 20 | 14 | 18 | 63 | 1 |
| data-first | 40 | 20 | 14 | 8 | 0 | 1 |
| ack-first | 0 | 20 | 15 | 11 | 51 | 1 |
| ack-first | 40 | 20 | 15 | 5 | 0 | 1 |
| reserve | 0 | 20 | 14 | 18 | 63 | 1 |
| reserve | 40 | 20 | 14 | 8 | 0 | 1 |

Each guard cohort: 60 offers, 51 unique receipts, 43 genuine confirmations, three matching-forgery false confirmations, three stale DATA refusals. Retries 47 -> 21, ACK transmissions 85 -> 55, total DATA attempts 107 -> 81, opportunities 330 -> 297; late evidence 177 -> 0. This is an efficiency gain in these deterministic fixtures, not a general scheduler ranking or reliability estimate. No accepted decision required horizon EOF (0/298 at sample 320000).

Clean ACK-first witness: A's evidence at sample 32426 is too late for sample 32000, but available before 32640. Zero extra guard: ACK A starts 64000, confirmations at 96458 and 128474, redundant B retry at 128000. Guard 640: ACK A starts 32640, confirmations at 65082 and 130394, no retry. First confirmation improves, second is 1920 samples (120 ms) later: throughput, energy and individual latency are not interchangeable. Revision at sample 32000 invalidates A before evidence at 32426 under both guards even though active carrier ended earlier. Extra turnaround slack does not preserve old context. Matching forgery still confirms without receiver receipt. Short TTL still gives no confirmations. Receipt is not action, identity is not authority, checksum is not authentication.

Independent dense-packet stress, motivated by #449's 70-stream audit (read issue comment; not a full reproduction): gap-v5.cjs uses two distinct legal frames, phases .19/.38, gap 0/80/160/240/640 samples, trailing silence. At 0, 5 and 10 ms both candidates ambiguous; at 15 and 40 ms both recover. 10 ms witness inferred first end 31517, second start 31504; both decisions at 63882. 15 ms first decision at 32410. This differs from #449's seed-dependent 10 ms successful but delayed witness; preserve both. No general 15 ms threshold or guaranteed 40 ms turnaround. V4 overflow/terminal-completeness weaknesses unchanged.

## Reproduce and audition

From the integration directory, Node 22.16.0 on Linux x86_64:

    node evidence-v5.cjs evidence-v5-output
    node verify-evidence-v5.cjs evidence-v5-output
    node gap-v5.cjs gap-v5-output

Native 603 runner assertions, 530 verifier assertions, 66 sessions (independent full WAV rescans at chunk 997, all exact events match); three chunk-partition comparisons 127/997 with identical PCM/evidence/trace. 298 accepted packets, 0 terminal-at-horizon; max session peak 4096/32768 (-18.06 dBFS, not SPL). Independent Python wave/hash check 66/66. Five additional dense-gap WAV specimens, exact two-frame outcomes asserted. Export manifest contains SHA-256 per WAV, sample count and peak; JSON includes complete trace and acquisition hypotheses. Package includes previous negative witnesses and all new exports. Open evidence-inspector.html and load corresponding JSON/WAV (start with clean-ack-first-g0 vs clean-ack-first-g640). Waveform, transmission and release timeline, packet tree and hypothesis evidence, trace export. Use low device volume; no autoplay. Inspector is a trace viewer, Node is the actual decoder. File pairing is manual; hashes are verified by CLI, not browser.

Chromium 144.0.7559.96 headless set_content qualification on final HTML: file selection, 20 s media duration, event selection/details, muted playhead advancement and JSON download reread passed. file:// ordinary navigation blocked by administrator; no physical sound/listening, native Windows or embedded timing claim. Git checkout failed DNS; full repo local checks unavailable. Source blobs fetched back match native-tested files. Independent review and new exact-head CI remain separate gates.

## Limits and next action

This is a centralized synthetic half-duplex simulation; not a distributed clock, real-time CPU deadline measurement, bounded embedded application, acoustic hardware or human study. The receiver itself remains bounded as v4; exported session arrays and trace storage are offline. The guard is paid with an opportunity and longer timers. Next compare equal absolute deadlines and adaptive listen/turnaround policies, isolate expiry versus evidence-latency effects, and retain dense-frame late association/overflow and EOF-erasure witnesses. Then pursue local timing path recovery and compact framing, keeping packet integrity checks and the prior collision/forgery counterexamples. No shared manifest updates or scientific status promotion.
