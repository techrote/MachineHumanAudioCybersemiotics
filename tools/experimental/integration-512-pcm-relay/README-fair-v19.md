# Fairness and request leases — v19 (Refs #512)

Draft/HOLD; synthetic-only, one AI-assisted worker, 2026-11-26. Parent d3a2fa118db659c845fe0962201be47a08692a6d; main 495a98ca12bae467a507031f04931aa4254b1866. Eight inherited executable blob IDs match parent. No external code imported (root LICENSE lookup 404). No changes to shared/frozen records or firmware.

## Contract
Separate fixed-slot scheduler reuses v18 scan/request, v2 render and v1 grammar. Nine 33600-sample slots at 16 kHz; two DATA attempts/record, one local request/session, nominal full-frame duration 31360 samples. Compare timeout, eager request-first, and fair-lease (ACK first; allow one fresh DATA to bypass a pending request; prefer fresh DATA when selecting from ready records). A matching strictly decoded request is eligible only in the outstanding first-attempt state; fair-lease additionally checks one acceleration and a half-open release-time window [(first+1)*STEP,(first+4)*STEP). Timeout remains at first+5 slots. Diagnostic interpretation can queue a request only, not receipt or ACK. Fixture transmissions consume channel slots; evaluator receipt set labels genuine confirmation, not sender authority. Fixed two-route shared capture monitor and host gap notices; no independent clocks, tag allocation/reuse, durable lease state, authentication or compact control format.

## Evidence
Node 22.16.0 Linux: `node test-fair-v19.cjs fair-v19-output`; `SEED=113 node test-fair-v19.cjs fair-v19-seed113-output` (PowerShell: `$env:SEED='113'; node test-fair-v19.cjs fair-v19-seed113-output`). Two seeds x seven cases x three policies = 42 sessions, 224 assertions (112 each), 42 alternate-chunk rescans exact. Python independently checked 42 WAV hashes/formats/peaks (4096 counts max); 8 common seed-71 timeout/eager waveform hashes and evidence arrays match archived v18. First runs 25.81/25.69 s, RSS 85424/85520 KiB. Identical initial conditions per scenario, not identical later PCM. Results identical in both seeds at sample resolution:

| case | timeout | eager | fair-lease |
|---|---|---|---|
| gap, source 1 confirmation sample | 234022 | 133222 | 133222 |
| competition, source 1 | 234022 | 133222 | 200422 |
| competition, source 2 | 99622 | 200422 | 99622 |
| late forged request (slot 4), honored | 0 | 1 | 0 |
| early forged request (slot 1), honored | 0 | 1 | 1 |
| replay (slots 1/2), honored | 0 | 1 | 1 |

Competition: fair-lease retains source 2's timeout latency, advances source 1 by 2.1 s (eager 6.3 s), equal last confirmation to eager. Both request policies reserve 188160 vs 156800 samples. Single-source gain 6.3 s costs 31360 samples. Late forgery is expired but eager acceptance would have scheduled the already-due timeout retry: no latency/traffic improvement from refusal in that fixture. Early forgery advances both request policies; second replay refused by inactive/ready guard in both, not a demonstrated new anti-replay benefit. Lost request falls back to timeout; persistent gap never confirms. No false confirmations in these seven cases, which do NOT include the known forged ACK witness (retained v18). No universal fairness, security or human claim. ACK/fixture priority can still starve repair; no source arrival sweep.

## Operation and next work
Open fair-v19-inspector.html (or Open Inspector.cmd in package), choose either receipt and select WAVs; default playback 0.12. Chromium 144 via set_content fallback: selected actual files, three panels, muted playhead and exact trace export; file navigation blocked by administrator. No Windows/hardware/listening qualification or independent review. Upstream draft #443 ed648880b0588b2852a0b691a8f603a2a0a49a13, #449 92325206f21934a1a517d8876ba26e6ccaafccf8, #453 7773a123a29881a22d7c1893df1dd609c4ef25d1, #457 a51d73f23306b6974542dce54840b8b52520b996; all structural checks passed. Read #457 service-debt report (synthetic scheduling, not PCM reception) and #453 transaction-leases code (bounded lifetime tag reuse, not this simple outstanding-state lease). Next separate request duration from arbitration, then vary arrivals and ACK pressure; test stale transaction aliases across session boundaries before any security claim.
