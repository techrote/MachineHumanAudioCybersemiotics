# Integration Regression Corpus 001 — bounded packet binding

Refs #607 / #512 / #513. Mergedown lane, Draft/HOLD. Synthetic software evidence, not scientific acceptance.

Frozen source pin: `32eca4f1e1fe16d53422971c7663ae7fd73cca34`; accepted main at intake `495a98ca12bae467a507031f04931aa4254b1866`. The two archived CJS sources are unchanged original Git blobs (`3ba457f85f496e4d57d9789a2dc3b7d68fe2c071`, `2aa2905d4f4d756276814d5ca941c02c51e63f97`). All source imports are local or Node built-ins. See upstream README-v2 at the frozen pin for the original design and attribution (Integration lane, AI-authored). Internal archive only, no new license decision. No later v3–v40 code or 45-session scheduled-v2 corpus is included: this is the smaller nine-witness / two-session binding experiment, not a promotion of all #513.

## Reproduce

Run in this directory, using Node 22.16.0 and Python 3.13.5 (no external dependencies):

```sh
node bound-v2.cjs bound-v2-output
python check_binding.py bound-v2-output
```

Use a fresh output directory for repeat generation. Open index.html with the default output present. No autoplay; digital gain starts at 12%, not SPL. Audio is original synthetic upstream material; no physical listening or Windows qualification claimed.

## Executed Linux results

- Both retrieved source Git blobs exactly matched the native files. Native original CLI ran 45 assertions; receipt SHA-256 exactly matched upstream `8fc53c22966b27e3ec62519271471431fe3b10b0f404c93f9ed9a57121ca450a` (therefore the 11 frozen WAV hashes). Two complete output directories, 12/12 files byte-identical.
- Independent standard-library Python audit: 11 WAV formats, payload hashes and peaks; 19 fixture-aligned slots decoded, 18 v1 and 15 v2 releases; 84 two-erasure combinations across the three blocks of one clean frame. Independent DFT dominance criterion, direct modular parity solve and stack syntax parser; aligned fixture starts are known, so no independent blind acquisition result. Recounts both sessions' configured-version and preceding-send ACK decisions. Not an independent implementation of the scheduler.
- Three negative controls: mutated WAV, mutated receipt, and mutated WAV plus recomputed receipt hash entry all rejected. Maximum peak 8192/32768; no acoustic exposure claim.
- Original splice and missing suffix rejected by strict v2; recomputed hybrid, matching forged ACK and tag collision accepted. These are negative witnesses of public checksum limits, not cryptographic proof or human findings. Two 10-second schedules both receive three and confirm two; DATA-first zero fresh ACKs, ACK-first one. No universal ranking.

## Qualification gate

No merge or scientific acceptance. Windows native CLI, ordinary browser/gallery interaction and independent PR review outstanding. Full clone blocked by DNS; source retrieval and exact blob verification succeeded. Future batch: 45 scheduled cases and newer authenticated session lifecycle counterexamples; do not silently retarget this frozen scope.
