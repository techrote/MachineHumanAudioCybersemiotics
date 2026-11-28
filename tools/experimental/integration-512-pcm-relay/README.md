# MHAC Integration Lab — PCM-bound relay v1

Refs #512. 25 November 2026, exploratory synthetic-only Draft/HOLD. Single AI author; no human evidence, independent review, device operation or production reliability claim.

## Operate

Node 18+ (tested native Node 22.16.0, Linux x86_64). Run `node relay.cjs output` and `node inspect.cjs output` in this directory. No npm dependencies, network, microphone or device control. Generates 28 original WAV/JSON pairs, stimulus SHA-256 manifest and qualification receipt; second command reads and checks all files, rescans complete sessions and generates splice.wav. Open index.html in a desktop browser and select matching local WAV/JSON pairs. Inspect waveform, AST, capture timeline, scan score, decoded symbols, receipt decisions; switch policies and export trace. Playback opt-in, low hardware volume; digital amplitude is not SPL. Viewer displays stored decoder evidence rather than rerunning acquisition.

## Intake and authority

Accepted main 495a98ca12bae467a507031f04931aa4254b1866; AGENTS, RAG, programme/runbook, integrity, validation, foundations, experiments/human gates read; first 100 returned open issue and PR titles surveyed, targeted integration and branch searches, #452/#456 issues/comments and #512 (empty comments) inspected. Explicit owner Draft/HOLD requirement governs rather than normal merge mandate. All changes isolated; no canonical records, shared manifests, frozen protocols or other workers edited.

| Input (all draft) | Pinned head | Reading/use |
|---|---|---|
| #453 | 5a84700b34e4b54ecba908946848b1d552456d47 | Read recursive.cjs, integrity.cjs, acquisition.cjs; independently implement protected wire contract; cross-check codewords/PCM. |
| #457 | f1a966c77c3315108341af6209ed57e6df8fd8ca | README and issue history; separate receipt, confirmation, repair, half-duplex concepts. |
| #443 | c01f4d294e16b06c08783e8014bbf2dee010cf72 | README; retain PCM versus timestamp oracle distinction. |
| #449 | 6e6cf62ec7f1d74542dc3021d8c50c9fb30f18b6 | False-onset report; preserve out-of-model faults, do not transfer jitter guarantees. |

All four exact heads returned successful Research integrity workflows; structural CI not scientific acceptance. Root LICENSE at main returned 404; no upstream source vendored or external dependencies copied, no license granted, not exhaustive rights audit. FM-1-MHAC README (main 16c698d9e244559064a9a9a22f834d36912bf498), FM-1-CYDaux README (main e65a0b880b5c13c9aa3ce734c6e3eaa4b11fc969) inspected read-only; no hardware validation or downstream changes. Foundry #447/#439 discovered, not imported; no VST build.

## Wire and state contract

16 kHz mono PCM16; ordered 2300/2700 Hz 20 ms preamble halves; 16 slots of 80 ms (60 ms active), 17 carrier frequencies 400–2000 Hz in 100 Hz steps; peak nominal 4096 counts. 21,120 samples / 1.32 s per frame. Two independent GF(17) blocks: six metadata symbols (kind DATA=0 or ACK=1, claimed source, version, actor/addressee, event, sequence; non-kind fields 1..16), two check symbols; then #453 protected prefix AST (up to four nodes). Sum and weighted sum mod 17; up to two known erasures per block, no unknown substitution correction. No authentication, version rollover, joint block binding or calibrated probability. Acquisition scans at 1 ms stride, capture bound 12 s, finite template bank, at most 289 erasure fills per block. Known rate/grammar but no oracle start or tokens; correlation score is not probability.

One fictional pending verify(fault) request, configured current context/actor. DATA and automatically generated ACK traverse same modeled half-duplex direction sequence; both recovered from PCM. ACK echoes fields and tree, not proof of action, resolution, human understanding, origin or authority. Bound sender matches all pending fields and AST; latest accepts any decoded ACK. Both have at most two DATA attempts, same initial conditions, not matched actual duration after differing decisions. Retry after unconfirmed round, no real timer or multi-source arbitration yet. Duplicate DATA does not insert identical tuple twice; duplicate ACK uses boolean state, not a complete replay ledger. Fault choice and genuineness labels evaluator-only; receiver current context configured out of band. Simulation passes capture windows; native inspection separately rescans concatenated WAV without boundaries. No overlapping interference, general streaming, action or resolution events yet.

## Qualification and adversarial results

Native Node CLI: 150 assertions; 14 scenario families x two policies, seed 71. Native inspect CLI: 28 WAV headers/hashes checked and whole-session rescans; all 28 accepted packet sequences match windowed results. Upstream pinned read-only connector V8 cross-check: all 2,304 body codewords match, 138 clean directional PCM comparisons (23 trees x three phases x two directions), plus committed relay replay matches native aggregates. Native source Git blob hashes equal repository blobs. See qualification.json and native-receipt.json; generated full traces and stimuli are not committed binary files.

| Policy | Confirmed / 14 | Invalid confirmations | DATA attempts | Capture samples |
|---|---:|---:|---:|---:|
| Bound | 13 | 1 | 23 | 894892 |
| Latest | 13 | 4 | 20 | 763027 |

Bound rejects stale version, wrong actor and conflicting AST ACK then recovers on retry; latest accepts wrong ACK. First ACK loss repaired with one unique data receipt. Persistent loss stays unconfirmed. One erased slot per block recovers on first attempt; substitution, interruption, 1.2% resampling drift need clean retry in these fixtures. Uniform ±900 PCM counts noise succeeds in one fixture. Peak 4988/32768. Counts are deterministic fixture outcomes, not estimated error rates.

**Negative controls:** exact matching forged ACK confirms even with zero DATA receipts. Independently valid FEC blocks may be spliced: metadata from A and quoted-open AST from B decode as one valid packet. Native inspect generates splice.wav, checks decoded AST directly. Joint checksum can address accidental splicing but not establish authority; adversarial forgery requires separately specified trust mechanism. Neither matching nor valid grammar proves source. Preserve these failures.

Native Chromium 144.0.7559.96: file:// launch blocked by administrator. Identical HTML loaded via Playwright set_content for DOM test; three real local WAV/JSON pairs selected, timeline populated, stale policy switched, media duration 2.787875 s, playhead advanced past 0.1 s, paused, exported and reread JSON; zero page errors. Muted headless, not physical listening. Ordinary file launch and Windows unqualified. Full checkout blocked by GitHub DNS failure. No whole-repository local validation or substantive independent review.

## Next

Continue this same PR: joint block binding versus existing blocks; two-source scheduled continuous PCM with bounded return reservations, delayed ACK/replay and interference; independent authority and action/resolution lifecycle; bounded-memory streaming and host-portable fixtures. No merge/self-approval. Keep prior baseline and counterexamples. Exact-head CI and substantive review remain gates.
