# Metadata-pressure audit hardening — 28 November 2026

Refs #607 and #817. Draft/HOLD. Supplemental fixed-fixture acceptance check, not a replacement for the original Node receiver execution or its historical Python audit. No receiver implementation, pinned upstream file, previous audit, generated evidence, workflow, canonical manifest or human gate changed.

Exact parent c63cb1073fbd9c03006eb90ce3eb5372a13bd93d. Six archived source blobs independently retrieved from both this parent and upstream 3637529f313949d31e55d66d04bb119547c1e29a: byte-identical 6/6. Reconstructed all six plus checker and original auditor locally, confirmed all eight Git object hashes before native execution. Direct Git DNS failed (exit 128), so this was exact connector-source reconstruction, not a full clone.

Run in this directory (fresh output names, no optimized Python):
```sh
node check_metadata_pressure.cjs replay1
python audit_metadata_pressure.py replay1
python audit_metadata_pressure_strict.py replay1
python test_metadata_pressure_audit.py replay1
node check_metadata_pressure.cjs replay2
python audit_metadata_pressure_strict.py replay2
diff -qr replay1 replay2
```

Native Linux Node 22.16.0 and Python 3.13.5: both generations identical across 11 files, exact historical receipt SHA256 01a7643a8313a9d93d4475cd70bc4d86f5c1bc817dfa386eed69d401522dfaf2. Reproduced 30 rows, 34 causal prefix executions, 96 refused candidate events with exact observed metadata. New Python reconstruction separately derives the GF(17) frame, finite tag, phase/oscillator samples and overlapping decoy layout; all 1,500,000 PCM samples match byte for byte, plus matrix coverage, expected outcome sequence, event boundaries, counters and witness totals.

Independent audit gap: the earlier Python checker alone accepted six deliberately altered copies with internally consistent hashes and/or counters: all-silent stimuli with erased outcomes, erased outcomes on genuine stimuli, omitted summary, unexpected mode, event past the end of capture, and altered decoy PCM with recalculated hashes. The new strict audit refuses all six and accepts both genuine executions. Tests mutate only temporary copies; original outputs remain intact. Disabled assertions also refused.

New exact tested Git blobs: audit eea724ac8cb73508b6376565d37c33b2ee74c727; regression bdf34903a2f431f357e4c1b147d512950d74f66b. This is fixed-fixture auditing, not cryptographic authentication of event traces or independent decoding, general receiver superiority, physical/human evidence, Windows/browser qualification, CPU parity, or replication of the separate Python Run062. Retain the original negative controls and all independent-review gates. No merge.
