# MHAC Partial-Observation Laboratory v15

Refs #512, cumulative Draft/HOLD #513. 2026-11-25; one AI agent, no independent review. Accepted main 495a98ca12bae467a507031f04931aa4254b1866; pinned integration parent 20b8bbd684f140886d5f17ec256d9272e7898c7b. Original synthetic stimuli. No human evidence, production claims, license grant or wire changes.

## Run

From this directory run `node test-partial-v15.cjs partial-v15-output` (Node 22, no npm dependencies). Open partial-v15-inspector.html, load the generated receipt.json and matching WAVs; start optional playback at low device volume. The inspector is a trace viewer, not a live decoder. Missing samples are represented as zero solely for audition; gap metadata is in the receipt. The latent-clean and latent-altered files represent fully observed hypothetical completions, not reconstructed missing samples.

## Estimator and boundary

For each body frequency, fit cosine and sine on the original sample coordinates restricted to the observed subset. Score = projected energy / observed energy via the two-by-two Gram matrix. No missing sample is read; sample coordinates are not compressed. Require at least 75% observed coverage, observed RMS >=250 PCM counts and determinant >=0.05*k^2; the thresholds are engineering choices, not optimal or calibrated probabilities. Retain existing 0.85 score and 0.2 margin, GF(17) erasure/parity, grammar and binding checks. Preamble handling remains whole-window conservative; complete windows use the original scorer. The new estimator uses O(1) working scalars per fit, no added persistent PCM array; work O(n) per frequency hypothesis, actual CPU profiling and embedded qualification pending. Inherited typed-array storage 460804 B, excluding runtime overhead. All diagnostic events remain authority:false and no earlier than their logical evaluation/host notice; strict receiver alone drives interaction. No new action/authority path.

## Matched PCM results

Four carrier-phase seeds, twelve two-message conditions per seed, 48 fixtures/96 intended packets. Strict 56/96, v14 whole-window diagnostic 68/96, partial-window diagnostic 84/96, naive zero-fill 80/96. No unexpected packet identity in this corpus. Each row below is out of 8 intended packets per condition, including the unaffected second packet.

| Condition | Strict | Whole | Partial | Zero |
|---|---:|---:|---:|---:|
| Clean | 8 | 8 | 8 | 8 |
| One missing slot | 4 | 8 | 8 | 8 |
| Two missing slots | 4 | 8 | 8 | 8 |
| Three 16-sample holes | 4 | 4 | 8 | 8 |
| Three 40-sample holes | 4 | 4 | 8 | 8 |
| Three 64-sample holes | 4 | 4 | 8 | 4 |
| Three 80-sample holes | 4 | 4 | 8 | 4 |
| Three 81-sample holes | 4 | 4 | 4 | 4 |
| Three 120-sample holes | 4 | 4 | 4 | 4 |
| Preamble 16-sample hole | 4 | 4 | 4 | 8 |
| Post-frame gap 32400 | 4 | 8 | 8 | 8 |
| Post-frame gap 32416 | 8 | 8 | 8 | 8 |

The 80/81 boundary is an implementation coverage threshold, not a physical minimum or general acoustic guarantee. Eighteen overlapping v14 fixtures reproduce both WAV hashes and complete v14 event traces exactly. 18 mixed-tone Gram-Schmidt reference comparisons agree within 1e-10; 75 synthesized single-tone controls test phase, coverage and hidden-value invariance. No population inference.

## Retained indistinguishability witness

Seed 45319, three 64-sample missing intervals [1100,1164), [2380,2444), [3660,3724), total 12 ms. Full clean capture accepts A at 32410; a full capture with those samples replaced by a 4096-count 1900 Hz tone instead prefix-refuses A at 3866. Both accept B. After applying the same mask the captures are observationally identical and yield identical events; partial diagnostic accepts reconstructed A at 32410 and B at 68522, strict only accepts B. This is a counterexample to equating a masked fit with the full-capture receiver's decision; not a claim that the altered world has a different intended semantic message or that the diagnostic emits a wrong identity. No rule using only this observation can reproduce both differing full-capture decisions. A future association certificate must make the assumed completion model explicit, not equate fitted content with complete evidence. Witness WAV hashes: clean 60f35b7c708ddbfabbcda49f034e4ced95ed8fad54f6c187c91ba130bea0f870; altered 044a937890aa53bb8b1a730a50bf0c72367073fd02d23fbe55dba4138d841992; masked f9032ab7e170cc661c0a2a26890444731cc0178be26ace1fa8b54e82f3566959.

## Qualification and limits

Native Node v22.16.0 Linux, 448 counted assertions plus per-observed-sample read guards, 24.27 s elapsed, 153528 KiB max RSS on this host. 54 original WAV files independently verified via Python wave/SHA-256, maximum PCM magnitude 4096/32768. Three causal scheduler cases (clean, revision, forged) compare strict-only trace, metrics, evidence and waveform exactly; three exported masked PCM rescans exact. Genuine confirmations 2/2/0, false 0/0/1. No throughput gain; forged ACK unresolved. Chromium 144.0.7559.96 actual file inputs, 54 records, muted playhead and exact JSON export, no page errors; ordinary file navigation blocked by administrator, fresh-page set_content fallback. Git ls-remote DNS failure prevents whole-repo native tests; no Windows, physical listening or embedded execution. Native-tested blobs: partial-v15.cjs b3bd2f9ea31c13437aef52d12b3f937e800bd915; test-partial-v15.cjs 72f72c4bd99a5ca97422b6caa25056ded05cb2ba; partial-v15-inspector.html e0d4d3d91a7d1e7313a153ad52123abb51f84ac7. Eight inherited source blobs verified against pinned parent.

Upstream refresh: #443 92db2601aae859f0860eecb0acd03f44049688db (measurement README), #449 334c1581798636331469f6b49734f0ed98de7163 (adversarial README), #453 d0a7c818b1ec9070cb539422a04b01c5d0c63d64 (transaction-leases source), #457 b44f11b425a0e42d2ed245057c8afbb42d4e0cec (endpoint timing README); structural workflows 45699548702, 45702729268, 45704355402, 45697860683 respectively succeeded, not substantive acceptance. Prior integration run 45696334320 succeeded. Foundries inventoried, no code imported; no repository-wide LICENSE found at root, no external code reuse. Read-only FM-1-MHAC and FM-1-CYDaux README compatibility; no firmware edits, physical flashing or claims. No canonical records or other branches changed.

Next: explicit completion-model-dependent association certificate and worst-case missing-window spectral bounds; compare with conservative diagnostics, not automatic receipt promotion.
