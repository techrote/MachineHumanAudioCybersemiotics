# OBS-PACKAGE-009 — hosted native qualification and owner delivery

Refs #607, #443; continuation of OBS-PACKAGE-008. AI-assisted software qualification, not scientific acceptance.

## Executed evidence (26 November 2026)

Frozen consolidation head `37c60b93762bf273059b762d518c35a34897cffe` checked out by [hosted run 45752199179](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45752199179/job/139682384228). The decoded job log records Python 3.12.3, Node v22.23.5, 11/11 fixture tests, two original native builds and verifier PASS. The [research-integrity run](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45752199082) also passed. The extracted complete verifier result is [OBS-PACKAGE-009-hosted-receipt.json](OBS-PACKAGE-009-hosted-receipt.json).

Both packages contain 27 files including the manifest (assembler reports 26 excluding manifest). All files match by SHA-256; all seven source blobs, 2,304 conditions, 24,467 cells, 16 independent rational-oracle fingerprints, 96 certainty comparisons and five WAV hashes passed. Manifest SHA256: `ffcd6fea32658a5f0a5e7c26007bb367b376637441cc47afdc4cb999a02f09c7`. Nine WAV specimens have maximum digital peak 2993/32768. This is not physical listening or calibrated SPL.

The original run did not upload its output (artifact list empty). This follow-on changes only the temporary qualification workflow and consolidation documentation/ledger, not the frozen originals or verifier. The same one Ubuntu job now retains the first verified package and final JSON receipt for 14 days using the pinned official upload-artifact action. No matrix, manual dispatch, paid runner or source-branch changes. New-head upload is pending until checked.

## Owner instructions

From a successful new run, download the MHAC-Observatory-607 artifact while signed into GitHub, extract it, then open `observatory-one/index.html` in an ordinary browser (if the archive root differs, locate the directory containing package-manifest.json). Keep the original JSON qualification receipt alongside the package. Playback opt-in; start with low hardware volume. Original specimens are not level-matched across conditions. No human study is authorized.

To regenerate locally from the exact candidate in a byte-preserving checkout (Python 3.11+, Node 22):

```sh
cd tools/experimental/mergedown-607
python -m unittest -v test_build_observatory verify_native_package
python build_observatory.py output-one
python build_observatory.py output-two
python verify_native_package.py output-one output-two
```

## Promotion decision

HOLD overall. Native bounded legacy/selective execution gap closed at the recorded head; ordinary file/browser interactions, Windows execution, physical audition, independent external review and owner approval remain open. Exclude joined reconstruction, later Measurement/Grammar deltas and temporary CI workflow from general promotion until explicitly reviewed. Avoid permanent duplicate implementation; coordinate canonical placement with Measurement. No licensing change, canonical records, human gates or merge. New Grammar migration collisions reported in #607 comment 7183015554 remain separate unresolved evidence; do not promote the newer code as a migration-safe format.
