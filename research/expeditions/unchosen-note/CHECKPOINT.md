# Execution checkpoint

- Scope: #205, only research/expeditions/unchosen-note/.
- Base: main at 495a98ca12bae467a507031f04931aa4254b1866, verified via branch metadata before branching. Existing issue/PR search identified #183, #197, #199, #201, #203 and their related work. Existing open PR branches were left alone. Read AGENTS, RAG, programme, runbook and protocol freeze.
- Artifacts: README.md, SOURCES.md, AFTERWORD.md, lab.mjs, run.mjs, RESULTS.json, instrument.html, this checkpoint.
- Local-equivalent execution: pure JavaScript function executed in the available JS runtime before serializing the exact function body to lab.mjs and instrument.html. 396 checks passed; 127 families, 109 same-full-union designs, 84 of those with empty intersection. Invalid inputs, duplicate/order invariance, independently quantified union/intersection, and example controls checked. The module wrapper and browser event handlers were not run in that runtime; verify Node CLI and real browser separately.
- Source work: targeted source reads as documented, including Gaver primary rendered pages 2 and 4. No external reviewer, no human data, no source republishing.
- Remaining: exact-final-head repository CI and merge status, Node wrapper verification, browser/audio smoke test if available, post-merge CI and landed files check. If these cannot be confirmed, do not claim completed acceptance. No human gate except any actual required repository approval.
- No shared manifests, tests outside expedition, protocol, evidence registries, or other issue branches changed. Refs #205.
