# MHAC Integration Regression Corpus 002 — scheduled PCM

Refs #607, #512, #513; Draft/HOLD. Synthetic software evidence only. Source pin #513 `0bbe9efc7704c66d526bf56c14218503f0b217c6`, accepted main `495a98ca12bae467a507031f04931aa4254b1866`.

Frozen input Git blobs (original Integration lane attribution, no new license grant): `relay.cjs` 3ba457f85f496e4d57d9789a2dc3b7d68fe2c071; `bound-v2.cjs` 2aa2905d4f4d756276814d5ca941c02c51e63f97; `scheduled-v2.cjs` 60983bd9369729fb7dcc8f548c5371a74d02c7aa. The first two already exist in #736 at `1970d452d6764dd9de247ae8fccda78c78965937`, under `tools/experimental/mergedown-607/integration-001/`; copy them from that exact snapshot into a separate scratch directory with scheduled-v2.cjs and audit_schedule.py. No live-branch dependencies or duplicate codec source in this PR. This batch depends on #736 for eventual repository promotion, not on it being merged for package operation. The portable ZIP includes all three source files. All v3+ experiments, original inspector, and bound-v2 witness corpus are excluded from this batch.

Native Linux Node 22.16.0 and Python 3.13.5, no external dependencies. Run in a fresh directory:

```sh
node scheduled-v2.cjs fresh-output
python -B audit_schedule.py fresh-output
```

Two generator executions, 483 assertions each, 91 generated files byte-identical across runs. Frozen upstream manifest SHA256 `0ac5726c7ef1c52212d3910da5d636ffe6abe422801f2d7b5486aa0ba9344bad` matched; it pins all 45 WAVs, not the individual trace JSON files. Separate Python audit verifies all WAV hashes, PCM format and peak, replays scheduling/causal ledger from decoder hits and offers, compares events, queue/current state, continuous packet sequence and 23 metric fields per session (450 slots, 1035 fields). Audit SHA256 `3e5c18e96fd27235f1251285d21e22be8e632a9d201951310dbd06e37299ba16`. Four altered trace controls (genuineness, invalid metric, sample timestamp, origin) refused. Generator uses original decoder; independent audit does not independently decode PCM, regenerate fault waveform, or establish blind acquisition. Trace bytes match between these two executions, not a frozen upstream trace digest.

Genuine confirmations: data-first 23, ACK-first 25, reserve 23 of 29 offers each; one false confirmation per policy. Fresh genuine confirmations 22/24/21 respectively. These are finite synthetic fixtures, not statistical inference, authenticated origin, execution evidence, or human comprehension. Audio files are mono PCM16 at 16 kHz, 20 seconds each, peak <=8192/32768; no SPL claim. No browser/Windows/physical playback tested. Full clone DNS blocked. Formal independent PR review and exact-head CI pending. No change to accepted main, source branches, canonical records, or human gates.
