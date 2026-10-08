# Preserved prepass checkpoints

[Home](../README.md) · [Programme](PROGRAMME.md) · [RAG](../RAG.md) · [R001 implementation](R001_IMPLEMENTATION.md)

These immutable checkpoints preserve the original preparatory work and its recorded evidence. They keep archive completeness separate from implementation and research acceptance. R001 was accepted through [PR #22](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/22), merged as [`f08330bf05e124694b276313d76ee68ccc946d48`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/f08330bf05e124694b276313d76ee68ccc946d48). [R002 / issue #2](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/2) remains the next dependency-ready task; its research preparation is partial and its protocol is not frozen. Live research remains `not_started`.

## Archive entry points

| Checkpoint | Immutable entry points | Preserved content and limits |
|---|---|---|
| R001 original architecture prepass | [Complete archive][r001-archive] · [preservation note][r001-preservation] · [preservation manifest][r001-manifest] | Exact original ZIP, all original unpacked files, original receipt/sidecar, and the retained earlier partial publication. Historical prototype and synthetic evidence; accepted implementation is recorded separately through #22. |
| R002 1A → 1B → 1C1 | [Canonical saved directory][r002-archive] · [preservation note][r002-preservation] · [saved-payload manifest][r002-saved-manifest] · [outer publication package][r002-package] | All 49 prepared saved-file paths, representing 48 unique blobs, plus separately preserved publication records. The unchanged nested packet chain includes 1A and 1B. Complete preservation does not complete the primary-text novelty audit or R002 acceptance. |
| R002 quantitative-methods prepass | [Handoff and identity][quant-handoff] · [exact original ZIP][quant-zip] · [internal manifest][quant-manifest] | Previously archived complete findings, decisions, extraction contract, prototype, synthetic fixture/results, tests, verification records and inert patch. Proposed methods remain subject to R002 review. |

The 8 October preservation pass verified the reachable refs, commit parents, tree paths/modes and actual remote file bytes for all 70 R001 additions and all 71 R002 files. The original outer ZIP digests matched after read-back. The prior partial branches and all pre-existing parent source blobs remain unchanged. The quantitative ZIP was independently read back at its existing commit and matched its recorded digest. These checks establish preservation integrity; they are separate from historical test reports and current research acceptance.

All original prepasses assessed commit `796151a33ec7a1acc026b239fe5c883312ebf40b` (tree `40afaeebb1801fd8adf1417a8da7523bff014d9f`). That historical source state predates the accepted R001 pipeline. Original issue-open, implementation-pending and publication-pending statements remain unchanged within the dated packets.

## R001 original prepass

The complete archive is pinned at `47a782df91ff4e61b5904a72aade72948c16a7e0`. Its additive parent is the [earlier six-file checkpoint][r001-partial] at `4a0b208e7aa18c9650002e5794eb97e21b981441`. The earlier ref and its files remain preserved.

[ORIGINAL-PACKET.zip][r001-zip] is the exact `MHAC-R001-prepass-796151a.zip`. Its 65 regular-file members map from `MHAC-R001-prepass/<path>` to `unpacked/<path>` without changing bytes or modes. The original `unpacked/SHA256SUMS` covers 64 payload files and excludes itself. The new preservation manifest covers 69 additions and excludes itself: the published addition is 70 files, and the checkpoint directory contains 76 files including the six unchanged earlier files. These are file/integrity counts, not new research results.

The [original handoff][r001-handoff] and retained logs report a final 70-test local overlay, comprising 26 bootstrap tests and 44 prepass tests, plus 33 CLI cases: five positive and 28 negative. An earlier 67-test invocation is retained alongside the final run; the original handoff explains the subsequent three audit-binding tests. Preservation checks reauthenticated the bytes and two retained baseline Git blobs; the historical tests and proposed patch were not rerun or applied for this publication.

The packet preserves the architecture/data dictionary, worked synthetic records, original validator and fixture generator, negative cases, raw logs/results, implementation order and inert proposed patch. Only two repository source files were retained as exact bytes in the original packet; other authority reads have provenance locators and reported identities. This is a complete original prepass packet, not a full historical repository checkout. Its deliberate 8 ms extraction against an 80 ms synthetic source continues to illustrate the boundary between structural checks and source fidelity.

## R002 packet chain and lineage

The complete R002 archive is pinned at `ced4e17873ba436e46e5fdfac21522ea65d8d325`. It is an additive child of the verified assessed commit `796151a33ec7a1acc026b239fe5c883312ebf40b`, on branch `checkpoint/mhac-r002-1c1-ca673613bb89885ec7e7`. The new commit preserves the exact prepared checkpoint subtree `70a7c5af3e7eb5bcd340052be578832e81d0281a`; all 27 assessed source blobs remain unchanged. The complete publication has 71 files: 49 canonical saved files and 22 separately checksummed publication-record files. The [canonical saved directory][r002-archive] is `checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/`. Its [SAVED-PAYLOAD.sha256][r002-saved-manifest], [ORIGINAL-PAYLOAD.sha256][r002-original-manifest] and [RESTORE-MAP.json][r002-restore-map] preserve the prepared content identity and mapping. The 49 saved-file paths and 48 unique blobs describe this canonical payload only; additional publication records are outside that comparison.

The exact outer package and the new preservation note are under `checkpoints/mhac-r002-1c1/publication-records/ca673613bb89885ec7e7/`. The original package includes the prepared Git bundle, whose SHA-256 is `4bf56d8cad4157f902b48484b606dfad635ff304acd1be7eaab8251b678f28f6`, and identifies prepared local commit `3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252`. Those describe the original prepared transport; they are not substituted for the actual published archive commit above. See the preservation note for publication ancestry and verification.

The [earlier 1C1 publication][r002-partial] at `f68325f161de7cc5968bfd32a6e3b6a14b548ab8` preserved eleven principal text files. It remains available as historical publication evidence. The complete archive additionally preserves the original packets, supporting records, CSVs, scripts, manifests and handoff material.

| Bounded chunk | Original recorded progress | Acceptance boundary |
|---|---|---|
| 1A | Scope/authority and existing/missing inventory; six RQ-to-method mappings; fourteen-family assessment; two illustrative mappings; seven reading packages; recorded 4/4 bootstrap smoke batch. | Preparatory repository/method audit; no external primary-source reading in this chunk and no protocol acceptance. |
| 1B | Bounded PRISMA 2020, PRISMA-S and critical interpretive synthesis reading; 28 source-to-decision rows; five illustrative change-impact classes; nine open questions; six deferred guidance packages. | Source-located preparation and proposed two-track adaptations; no implemented amendment, full methodological compliance or independent human review. |
| 1C1 | Comparator identity/access reconciliation, six-RQ conditional overlap matrix, coverage/unknowns ledger and provisional candidate questions. | Primary Nees–Liebman full text was not retrieved/read. The source-grounded novelty/overlap audit remains incomplete; candidate questions are not verified literature gaps. |

## Original packet identities

These digests identify the original bytes. Nested packet counts are separate from the outer publication package, canonical saved-file paths and publication-wrapper files.

| Original artifact | Bytes | SHA-256 | Original inventory |
|---|---:|---|---|
| `MHAC-R001-prepass-796151a.zip` | 195,264 | `7b71bd0a202694c8000619c68d66dfc510a413678345ffaf2035ad01560f2fc1` | 65 members; 64 payload hashes |
| `MHAC_R002_chunk1C1_publication_ready_ca673613bb89885ec7e7.zip` | 1,084,190 | `90244465f1fe18ecc6b5ac27201836a068cf0938e094553817c7ebd51a3d1119` | 65 outer members; 49 prepared saved-file paths |
| `MHAC_R002_chunk1C1_packet_2026-10-04.zip` | 283,668 | `81d87fb306d542aa2013b25c05776088838ee7de5ab14726d9d25e57991439fc` | 37 members; 36 payload hashes |
| `MHAC_R002_chunk1B_packet_2026-10-04.zip` | 219,338 | `d2c89ead12ab89e4bb551d4dbb4ff3cfeacbc1b2f7a3490399e22faf56e5176f` | 33 members; 32 payload hashes; contains unchanged 1A ZIP |
| `MHAC_R002_chunk1A_packet_2026-10-04.zip` | 129,557 | `d515cbebf715bb3f4473663b10217ba61b7770f607f7849ec8f9fe667fac63da` | 45 members; 44 payload hashes |
| `MHAC-R002_quantitative_prepass_2026-10-04.zip` | 106,806 | `29aed9f427e4e3a238c91d14804cfe0619b3aa3cad93c72b700c5d24864948cc` | 28 members; 27 payload hashes |

The quantitative checkpoint remains pinned at `007559214bf3fe2f2a00f9151fa7e3462cec9bf3`, under `checkpoints/prepass/MHAC-R002/d0a736be70ce/`. Its historical records report 17 tests and five reproduced output files. This harmonization links the existing complete archive; it does not duplicate it or accept its proposed estimands, pooling rules or production implementation.

## Reuse and remaining work

Resume R002 by reconciling its live issue, the accepted R001 record system, these complete original packets and their unresolved questions. Reuse the existing 1A/1B preparation and quantitative decisions. The primary comparator reading gap, further methodological decisions, feasible-channel pilots and truthful protocol freeze still require their own work and acceptance. Publication does not establish source-grounded novelty, source fidelity, scientific validity, independent human review or participant results.

Prototypes, fixture records, source exports and proposed patches remain in archival locations. They are not live research records or active protocol authority. The registry, accepted implementation and protocol files are outside this documentation-only harmonization.

[r001-archive]: https://github.com/techrote/MachineHumanAudioCybersemiotics/tree/47a782df91ff4e61b5904a72aade72948c16a7e0/research/checkpoints/MHAC-R001/prepass-796151a
[r001-preservation]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/47a782df91ff4e61b5904a72aade72948c16a7e0/research/checkpoints/MHAC-R001/prepass-796151a/PRESERVATION.md
[r001-manifest]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/47a782df91ff4e61b5904a72aade72948c16a7e0/research/checkpoints/MHAC-R001/prepass-796151a/PRESERVATION-MANIFEST.json
[r001-zip]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/47a782df91ff4e61b5904a72aade72948c16a7e0/research/checkpoints/MHAC-R001/prepass-796151a/ORIGINAL-PACKET.zip
[r001-handoff]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/47a782df91ff4e61b5904a72aade72948c16a7e0/research/checkpoints/MHAC-R001/prepass-796151a/unpacked/HANDOFF.md
[r001-partial]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/4a0b208e7aa18c9650002e5794eb97e21b981441/research/checkpoints/MHAC-R001/prepass-796151a/CHECKPOINT.md
[r002-archive]: https://github.com/techrote/MachineHumanAudioCybersemiotics/tree/ced4e17873ba436e46e5fdfac21522ea65d8d325/checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7
[r002-preservation]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/ced4e17873ba436e46e5fdfac21522ea65d8d325/checkpoints/mhac-r002-1c1/publication-records/ca673613bb89885ec7e7/PRESERVATION.md
[r002-saved-manifest]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/ced4e17873ba436e46e5fdfac21522ea65d8d325/checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/SAVED-PAYLOAD.sha256
[r002-original-manifest]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/ced4e17873ba436e46e5fdfac21522ea65d8d325/checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/ORIGINAL-PAYLOAD.sha256
[r002-restore-map]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/ced4e17873ba436e46e5fdfac21522ea65d8d325/checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/RESTORE-MAP.json
[r002-package]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/ced4e17873ba436e46e5fdfac21522ea65d8d325/checkpoints/mhac-r002-1c1/publication-records/ca673613bb89885ec7e7/MHAC_R002_chunk1C1_publication_ready_ca673613bb89885ec7e7.zip
[r002-partial]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/f68325f161de7cc5968bfd32a6e3b6a14b548ab8/research/checkpoints/MHAC-R002/chunk-1C1/PUBLICATION.md
[quant-handoff]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/007559214bf3fe2f2a00f9151fa7e3462cec9bf3/checkpoints/prepass/MHAC-R002/d0a736be70ce/HANDOFF.md
[quant-zip]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/007559214bf3fe2f2a00f9151fa7e3462cec9bf3/checkpoints/prepass/MHAC-R002/d0a736be70ce/payload/archive/MHAC-R002_quantitative_prepass_2026-10-04.zip
[quant-manifest]: https://github.com/techrote/MachineHumanAudioCybersemiotics/blob/007559214bf3fe2f2a00f9151fa7e3462cec9bf3/checkpoints/prepass/MHAC-R002/d0a736be70ce/payload/unpacked/SHA256SUMS
