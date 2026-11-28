# Mergedown: OBS-AFFINE-001

Refs #607, #442, #443. Bounded experimental software snapshot, not accepted scientific evidence. Reviewed by a separate AI-assisted consolidation run (not independent human review). Original files copied byte-for-byte from #443 at 5a1e3a857389ce8f6763c66847c9522179dcbf59; do not edit the source lane. The copied namespace is an isolated promotion/audition candidate, not a proposed second permanent implementation. Decide canonical location with the source lane before eventual promotion. No license decision or new redistribution rights asserted.

## Run locally

Open `affine-snapshot/index.html` beside `core.js` on an ordinary offline desktop browser. Choose receipt-relative or fixed external frame; click Recompute. WAV exports, condition manifest, full factorial and self-tests are exposed. No autoplay; start with low hardware volume. No calibrated SPL or human evidence.

Native CLI from an empty output directory: `node /path/to/affine-snapshot/core.js`. It writes receipt.json; the tested output hash is in promotion-ledger.json. Requires Node.js 22.16.0 as tested; no npm dependencies.

## Qualification receipt, 25 November 2026

Git retrieval failed with “Could not resolve host: github.com” (exit 128); connector source transferred verbatim, both local Git blob identities matched upstream. Actual native Node CLI returned {"assertions":1036,"status":"PASS"}, wrote complete receipt. Independent Python Fraction oracle compared all 1,152 deletion rows and 288 partitions using exact rational half-up rounding. Receipt-relative 66/144 ambiguous, 57 with one bit entropy, mean optimal index accuracy 0.7864583333333334; fixed 0/144 ambiguous, accuracy 1. The known 144/89, 8 kHz, 800 ms condition has two equivalence classes [1,3] and [2,4]; deletion 2 and 4 share onset indices 800,4755,7200 and identical WAV bytes.

Chromium 144.0.7559.96 file:// navigation was refused with ERR_BLOCKED_BY_ADMINISTRATOR. Real headless DOM test via Playwright set_content with the verified external script inlined for test purposes: four rows and 2/4 receipt status, no audio source initially, downloaded deletion 2/4 WAVs byte-identical and native SHA256 matched CLI, PCM16 mono 8 kHz 8,000 frames, peak 2962 counts (9.04% FS), switched fixed frame and recomputed 4/4, downloaded condition JSON, browser self-test returned 1036, invalid p=0 rejected, zero page errors. Not a normal file navigation or physical listening test.

## Boundaries and next batch

Only core.js/index.html are included (no external runtime dependencies). The other 23 additive files in frozen #443 are deliberately deferred, not deleted; these include full generated qualification.json, phase.html, other visualizations and 16 further CJS apparatus modules. The original entire candidate and generated evidence remain retrievable at the frozen source SHA. Full workbench, phase, selective-transfer, actual desktop launch, Windows, physical audition and independent human review are not qualified. The separate source PR remains HOLD. No shared manifests, canonical research or frozen protocols changed. Research integrity CI is not runtime qualification; candidate exact-head CI must be checked before owner promotion. Owner authorization of this specific candidate remains required; no merge action.

Next: verify dependency closure and native export of legacy-workbench and selective-transfer, retain per-file hashes, test real DOM with actual outputs, and coordinate a single stable module location. Ledger records other principal candidates at intake; do not chase advancing heads.
