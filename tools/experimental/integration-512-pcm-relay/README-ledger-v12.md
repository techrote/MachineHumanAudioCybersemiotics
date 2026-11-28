# MHAC integration — causal loss ledger v12

Refs #512, cumulative Draft/HOLD #513. 2026-11-25. Predecessor 51b32dd3f75d3e22233f62f0fe1adcd80dc355e5. Single AI-assisted worker. Synthetic experiment, not production or human evidence.

## Reconciliation

Main 495a98ca12bae467a507031f04931aa4254b1866. AGENTS/RAG, programme/runbook, experiments/human gates and issue history inspected. Measurement #443 53eb42dd0103abccfb08111a0e6ec112b55e7750, Adversarial #449 8c6a4ac9b414cef5383b60c47d3e5a04a7f4381d, Grammar #453 be40e7795877599a02a151359f07adfa34036514 and Interaction #457 ab30661ed840795f0bff100fbdbe1d2e16470ccd remain drafts. Structural workflows succeeded for #443/#449/#457 and #513 predecessor; #453 exact-head workflow not returned at inspection. Read the pinned loss-ledger-audit.cjs and relevant measurement, grammar and interaction reports. Foundry candidates inventoried, no code imported. FM-1-MHAC main 16c698d9e244559064a9a9a22f834d36912bf498 and FM-1-CYDaux main e65a0b880b5c13c9aa3ce734c6e3eaa4b11fc969 inspected read-only. No new license or vendored code. Full Git checkout blocked by DNS.

## Mechanism

The v11 lifetime hull conservatively spans all discarded acoustic hypotheses. v12 retains a bounded sorted union of half-open intervals, merges the nearest gaps when capacity is exceeded, and retires intervals whose end is at or before the minimum of next scan, active cluster start and every pending candidate start. Queries below the retired frontier and nonmonotone frontiers fail explicitly. This assumes future candidates cannot begin below that frontier; a discontinuous host or retrospective scan needs a different contract. Eight-candidate capacity, waveform, parity, packet binding and readiness unchanged. Oldest and incoming eviction remain alternatives; reserve protects earlier unfinished work and admits a new candidate by evicting the newest unfinished candidate when available.

The conditional safety argument: union and gap merging never remove a covered point; removing an interval ending at/before the watermark cannot affect a future half-open query beginning at/after it. The all-history oracle is evaluator-only. No claim that all acoustic ambiguity is detected.

## Native experiments

Node 22.16.0 Linux: node test-ledger-v12.cjs regenerated-output. 24,383 assertions, 18,000 interval queries, zero missed true overlaps, 717 conservative extras. Five published #449 stimulus hashes reproduced for seed 53813. Ten upstream streams x three policies: oldest hull and one-/four-range ledgers each recover 8/10 exact sequences, 12 packets, 132 evictions and 2 association abstentions. Two adjacent failures remain. No live ledger exceeded one range.

New gap witness: two plausible-prefix bursts, four seconds quiet before the central frame, extra onset near its end, second burst, four seconds quiet before tail frame. Six fixtures (two seeds x offsets 0,160,480 samples). Permanent hull + incoming rejection 2/6 complete sequences, 8/12 packets; incoming1, incoming4 and reserve4 each 6/6, 12/12 packets. All 208 evictions per policy. Hull four false-withholding decisions versus zero for retiring ledgers under the explicit discarded-extent oracle. No observed advantage for multiple live ranges or reserved admission. No unexpected/repeated accepted identities in these fixtures.

Seed 53813 gap-160: actual central extent [95984,127501), first burst hull ends 62582, second burst first lost extent starts 136288, yet permanent hull spans both. Both decide at 159562; hull withholds, retiring ledger accepts. No backdating. WAV SHA256 79d0db15621b8a2b4d410d9925bf033630b1fea4da9f70744db6900486600e89. At 480 samples both recover: retained boundary control.

15 adaptive-deadline scheduler sessions (clean, revision, forged x five policies), 15 exact independent exported file rescans and causal returns checked. Clean and revision produce two genuine confirmations each; forged produces one false confirmation and zero genuine confirmations in each. No additional end-to-end throughput gain. No authentication, action or resolution claim.

## Qualification and operation

Native full run 17.73 seconds, peak RSS 70636 KiB, host-specific observations. Python independently verified all 31 WAV hashes, PCM16 mono 16kHz headers, frame counts and peak <=4096. The existing parity-v11-inspector.html supports v12 receipt; packaged title-only variant tested in Chromium 144.0.7559.96 via muted set_content, 69 records, actual WAV file selection, advancing playhead, exact JSON export, no page errors. Ordinary navigation not qualified in this run. Windows, embedded, physical playback and independent review outstanding. No frozen records, shared manifests, other branches or firmware writes.

Native source blobs ledger-v12.cjs 538bf2e28da108bfe9751cab6720e21325c55be1 and test-ledger-v12.cjs bd8224d2e1be13cf3624a08a3fd4f9448b40d514. Next: quantify the causal frontier invariant under discontinuity, and prioritize latency-aware association rather than increasing interval count. Preserve the permanent hull, single-range and multi-range alternatives and the matching forged-ACK counterexample.
