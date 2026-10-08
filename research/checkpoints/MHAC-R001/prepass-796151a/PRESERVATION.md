# MHAC-R001 original prepass preservation

This is an additive preservation record for the exact completed prepass packet. It records local authentication and staging; remote publication and remote-byte verification are recorded separately by the publication process. Original packet contents, results and dated statements remain unchanged. No archived script, test, fixture generator or proposed patch was executed or applied during this preservation pass.

## Artifact identity and layout

- Original filename: `MHAC-R001-prepass-796151a.zip`
- Preserved exact ZIP: [ORIGINAL-PACKET.zip](ORIGINAL-PACKET.zip)
- Size: **195,264 bytes**
- SHA-256: `7b71bd0a202694c8000619c68d66dfc510a413678345ffaf2035ad01560f2fc1`
- Original ZIP: **65 regular-file members**, no directory members; every file mode is **100644**.
- Original manifest: [unpacked/SHA256SUMS](unpacked/SHA256SUMS), **64 payload entries**, excluding itself.
- Full original packet: [unpacked/README.md](unpacked/README.md), [handoff](unpacked/HANDOFF.md), [architecture and data dictionary](unpacked/proposal/docs/R001_PREPASS.md), [worked example](unpacked/assessment/WORKED_EXAMPLE.md), [implementation order](unpacked/assessment/IMPLEMENTATION_ORDER.md), [historical results](unpacked/results/SUMMARY.json).
- Unchanged external records: [original verification receipt](original-records/MHAC-R001-prepass-verification.json) and [original SHA-256 sidecar](original-records/MHAC-R001-prepass-796151a.zip.sha256).

The complete ZIP-member mapping is `MHAC-R001-prepass/<path>` to `unpacked/<path>`. Only that common outer directory prefix is relocated; bytes, relative logical paths and file modes are preserved. The original SHA256SUMS remains directly relative to `unpacked/` and is unmodified. The archived sidecar retains the original ZIP filename; its digest also authenticates the byte-identical `ORIGINAL-PACKET.zip`. This note and the `original-records/` directory are outside the original manifest's comparison scope.

## Assessment and publication lineage

| Role | Immutable reference |
|---|---|
| Original assessed commit | [`796151a33ec7a1acc026b239fe5c883312ebf40b`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/796151a33ec7a1acc026b239fe5c883312ebf40b) |
| Original assessed tree | `40afaeebb1801fd8adf1417a8da7523bff014d9f` |
| Existing partial archive and selected additive parent | [`4a0b208e7aa18c9650002e5794eb97e21b981441`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/4a0b208e7aa18c9650002e5794eb97e21b981441) |
| Selected parent tree | `6b51f66d8224bfc5487c9874c0121108e6690f5b` |
| Preserved historical partial branch | `checkpoint/mhac-r001-prepass` |
| Selected new publication branch | `checkpoint/mhac-r001-prepass-complete-7b71bd0a2026` |

The earlier six-file checkpoint remains intact. Its report, worked example and implementation order are useful direct views, but its historical CHECKPOINT.md accurately describes the earlier omission of the full ZIP. These new paths complete the original packet without rewriting that historical account. The additive payload has no path collisions with the six existing files or any existing parent-tree blob.

## Integrity checks performed for this preservation

The current preservation pass independently checked the known outer SHA-256 and size, ZIP CRC/readability, safe and unique member paths, exact 65-member inventory, all 64 original payload hashes, original sidecar/receipt agreement, and byte-for-byte identity of every staged file with its ZIP member. All 65 ZIP file modes are retained as 100644. The two retained baseline source files were independently rehashed as Git blobs and matched their original recorded identities.

These are transport, identity and staging checks. The historical unit tests, CLI cases, fixture generation and patch application were **not rerun**. No new scientific validation, full repository checkout validation or remote-publication success is asserted by this local receipt.

## Historical results and present acceptance

The original packet records a final local overlay of **70 passing tests**: 26 retained bootstrap tests plus 44 prepass tests. It also records **33 matching CLI cases**, comprising five positive and 28 negative cases, and successful historical patch applicability/byte-equality checks. `results/execution.json` and `results/unit-tests.txt` retain an earlier 67-test invocation; three exact-audit-binding tests were subsequently added, with the final 70-test log retained separately. The original handoff explains that chronology and states the validator implementation was unchanged between the completed CLI replay and the final test run. Preserve all of these logs as historical observations.

R001 was subsequently implemented and accepted through [PR #22](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/22), merged as [`f08330bf05e124694b276313d76ee68ccc946d48`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/f08330bf05e124694b276313d76ee68ccc946d48), with completion recorded on [issue #1](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/1). This archive does not reopen, replace or amend that implementation. The original packet's issue-open and implementation-pending statements describe its 4 October assessment. The migrated production records are distinct from these original preparatory bytes.

## Source and scientific limits

The prepass retained exact bytes for only two repository source files: `tools/validate.py` and `tests/test_validate.py`, both under `unpacked/baseline/`. Its nine other listed authority-file reads are preserved as provenance locators and reported identities, not as original retained source bytes. This is the complete original prepass packet, **not a complete repository checkout or complete source corpus**.

Synthetic records, fixture sources, prototype scripts and the 40-file proposed patch remain archival and unapplied. The deliberate structurally consistent 8 ms extraction against an 80 ms synthetic source remains part of the source-fidelity counterexample. Structural validity and complete preservation do not establish source entailment, study/sample identity, scientific quality, independent human review, participant results or MHAC-R002 protocol acceptance.
