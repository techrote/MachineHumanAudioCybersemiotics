# OBS-PACKAGE-008 — exact native package qualification bridge

2026-11-26. Refs #607/#443. Draft/HOLD; AI-assisted software consolidation, not scientific acceptance. Base main 495a98ca12bae467a507031f04931aa4254b1866. Parent candidate 658d6c0ea02c9f4996f0446878121fe12a99794f. Frozen upstream source and prior evidence unchanged.

Fresh local git ls-remote exited 128: Could not resolve host github.com. Native local Python 3.13.5 / Node 22.16.0 available; full upstream source not materialized. New verifier contract tests 5/5 PASS on synthetic fixtures only (native Python), tested blob dab65214ccd19088d98de59e8f09109cee78d7ea. No native original CLI pass asserted locally.

The verifier compares two actual package directories byte-for-byte by SHA-256, rechecks whole-package manifest and seven source Git blob identities, checks cell accounting, compares sixteen grouped fingerprints of the actual selective receipt against the independent rational oracle (2,304 rows, 24,467 cells expected), compares 96 certainty summary values and verifies five original WAV hashes against oracle predictions. This does not independently verify every prediction, every cutoff or the entire legacy detector.

One temporary issue-scoped workflow, .github/workflows/mergedown-607-observatory.yml, is restricted to same-repository PR #608 / exact branch, no matrix, Ubuntu, read-only credentials, exact head checkout. Uses the existing research workflow's pinned checkout action. No manual dispatch/fan-out or new paid services; separate from unchanged research integrity workflow. Coordination checkpoint #607 comment 7182168870. Exclude temporary workflow from general promotion unless explicitly authorized. Hosted result pending at authoring; read actual exact-head job logs before claiming PASS. No upload or browser/audition claim. No human gate or canonical record changed.

From this directory in a byte-preserving checkout:

    python -m unittest -v test_build_observatory verify_native_package
    python build_observatory.py output-one
    python build_observatory.py output-two
    python verify_native_package.py output-one output-two

Windows, ordinary browser interaction, independent human review and owner approval remain outstanding. No merge.
