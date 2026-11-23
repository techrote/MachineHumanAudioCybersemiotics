# Execution checkpoint

- Scope: #205, only research/expeditions/unchosen-note/.
- Base: main at 495a98ca12bae467a507031f04931aa4254b1866, verified via branch metadata before branching. Existing issue/PR search identified #183, #197, #199, #201, #203 and their related work. Existing open PR branches were left alone. Read AGENTS, RAG, programme, runbook and protocol freeze.
- Artifacts: README.md, SOURCES.md, AFTERWORD.md, lab.mjs, run.mjs, RESULTS.json, instrument.html, this checkpoint.
- Local-equivalent execution: pure JavaScript function executed in the available JS runtime before serializing the exact function body to lab.mjs and instrument.html. 396 checks passed; 127 families, 109 same-full-union designs, 84 of those with empty intersection. Invalid inputs, duplicate/order invariance, independently quantified union/intersection, and example controls checked. The module wrapper and browser handlers were not run in that initial runtime. Subsequent exact-blob qualification below passed.
- Source work: targeted source reads as documented, including Gaver primary rendered pages 2 and 4. No external reviewer, no human data, no source republishing.
- Remaining: exact-final-head repository CI and merge status, post-merge CI and landed files check. If these cannot be confirmed, do not claim completed acceptance. No human gate except any actual required repository approval.
- No shared manifests, tests outside expedition, protocol, evidence registries, or other issue branches changed. Refs #205.

## Exact-blob qualification

2026-11-23: Direct raw GitHub access from the local runtime failed DNS resolution. Reconstructed source files from connector readback at head b9871f1b55e79d28eb1b23cfd778742800dd54dc and verified their Git blob hashes before use. Node v22.16.0, command node run.mjs > RESULTS.json, exited 0. Output hash exactly matched stored report.

| File | Verified Git blob SHA |
|---|---|
| lab.mjs | 18e2a422924f451e8694bc32c05a3d1d4605ad79 |
| run.mjs | 8258ee09fc644134bc4af6a50a78005696c9c723 |
| RESULTS.json | c29f77d5403f699be949dcf97ff3df5c2ea1d12f |
| instrument.html | d119330f29f196ea9fbdca3b611536c84648ffd7 |

Headless Chromium 144.0.7559.96 via Playwright: file:// navigation was blocked by environment policy, so loaded the exact verified local HTML text using page.set_content. Confirmed initial disabled continuation buttons, all three open options, AB completion and disable-on-complete, singleton refusal with menu hidden and trace unchanged, toggle disclosure, deterministic cycling to C, overlapping and anchored menu states, AC and AD completion, running AudioContext and no page errors. Audio was not listened to by a human; no waveform capture or offline file-navigation assertion. Scope is functional DOM/audio-context smoke, not usability or human reception. No source file changed after these tests except the documentation. Dense integer-mask arrays are the model domain; arbitrary JS sparse array validation is not claimed.
