# OBS-PACKAGE-007 — frozen dependency closure and offline assembler

2026-11-26. Refs #607, #443. Draft/HOLD, AI-assisted consolidation; no scientific acceptance, new license, independent human review or merge. Source snapshot #443 at 5a1e3a857389ce8f6763c66847c9522179dcbf59; main observed 495a98ca12bae467a507031f04931aa4254b1866.

## Build the bounded package

From this directory in a byte-preserving checkout of #608, with Python 3.11+ and Node (22.16.0 tested on fixture jobs):

    python -m unittest -v test_build_observatory
    python build_observatory.py NEW_OUTPUT_DIRECTORY

The output parent must exist and the target must not exist. No network, npm or upstream branch checkout is needed. On Windows use a checkout with Git core.autocrlf=false from the outset or a byte-preserving source archive; the upstream scripts themselves enforce exact Git blob hashes. Open the generated index.html in an ordinary browser. If file navigation is unavailable locally, a normal loopback server can be used: cd into the output directory and run python -m http.server 8000 --bind 127.0.0.1, then visit http://127.0.0.1:8000/; stop the server when done. Playback is opt-in, start at low hardware volume. Digital peak is not SPL or matched loudness.

Seven source files are frozen in affine-snapshot (two already present, five copied by existing Git blob identity in this batch). The new assembler verifies all seven, invokes the original legacy and selective Node filesystem CLIs unchanged, verifies source and artifact hashes, checks WAV mono PCM16 and records peaks, writes an index and package-manifest.json, and publishes the completed directory only after both jobs succeed. The package contains source and generated outputs, not a rewritten research receipt. No network retrieval at runtime. Do not use concurrent builds targeting the same directory.

## Evidence and exclusions

- Native Python 3.13.5 and Node 22.16.0 fixture contract tests: 6/6 PASS, including repeated 14-file tree byte equality (13 listed files plus package manifest), known WAV peak 2048/32768, source tampering, existing output refusal, wrong hash, undeclared artifact, mutation during execution. These are original packaging fixtures, not upstream runtime qualification.
- Fresh Git direct retrieval exit 128: Could not resolve host github.com. Exact source dependency closure established remotely by pinned Git blob identities, without manually retyping the 114045-byte phase HTML or regenerating its evidence. Native transfer of full source into this execution environment remains unavailable.
- Fresh real Chromium/Playwright loopback navigation of a generated fixture package failed net::ERR_BLOCKED_BY_ADMINISTRATOR at http://127.0.0.1:40469/ (exit 1); no ordinary browser navigation PASS. No attempts to circumvent policy.
- Original full legacy/selective CLI execution, actual package generation from upstream source, browser interaction, Windows, physical audition and independent review remain outstanding.
- No joined reconstruction flag: joined-workbench and its dependencies, later Observatory deltas and generated upstream qualification evidence outside the seven frozen files remain upstream; no blanket promotion. The phase HTML includes its original embedded generated evidence, unmodified. Temporary frozen copies must be coordinated with the source lane before choosing one permanent canonical location. No rights granted.
- Prior numerical OBS-SELECTIVE-003 evidence and all earlier pins remain unchanged. Next run: execute original package against exact snapshot in an authorized native checkout; compare manifest and traces with prior independent oracle, verify browser and prepare bounded owner adjudication. No merge authorization inferred.
