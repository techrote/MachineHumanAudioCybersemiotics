# MHAC-R002 1C1 — archive authentication and staging record

This note records local preservation checks performed on 2026-10-08T22:34:39.934149+00:00. It is outside the original 49-file checkpoint and does not modify its historical reports, manifests or prepared Git identities. It is not a remote-publication receipt or research acceptance.

## Original identities

- Exact outer archive: `MHAC_R002_chunk1C1_publication_ready_ca673613bb89885ec7e7.zip`, 1,084,190 bytes, SHA-256 `90244465f1fe18ecc6b5ac27201836a068cf0938e094553817c7ebd51a3d1119`.
- Exact prepared bundle: `MHAC_R002_chunk1C1_publication.bundle`, 452,161 bytes, SHA-256 `4bf56d8cad4157f902b48484b606dfad635ff304acd1be7eaab8251b678f28f6`.
- Original prepared commit: `3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252`; original prepared root tree: `e58c33056e95365922f20fab377abe06bbe8fc1a`.
- Assessed source commit: `796151a33ec7a1acc026b239fe5c883312ebf40b`; actual assessed root tree supplied by the repository audit: `40afaeebb1801fd8adf1417a8da7523bff014d9f`.
- Original checkpoint path: `checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/`; all 49 saved paths, bytes, Git blob IDs and modes match the prepared bundle. All are mode `100644`.
- Checkpoint subtree Git identity: `70a7c5af3e7eb5bcd340052be578832e81d0281a`. Original payload identity: `ca673613bb89885ec7e754fb2677714f77331bb62b478099470946d3e1ee5864`.

## What was verified and retained

The outer archive has 65 regular-file members and 64 manifest records. All CRCs, inventories and hashes pass. Its 49 canonical saved files remain at their exact intended repository paths; the other 16 original members are retained, without content or relative-path changes, under `original-publication-material/`. These include the bundle, original publication instructions/verifier source, original verification files and transport/provenance metadata. No original outer member was omitted.

The exact outer ZIP and its original external verification JSON are also retained here. `OUTER-RESTORE-MAP.json` maps every original outer member to its current repository location. In particular, the unchanged original outer `SHA256SUMS` addresses both its own wrapper files and `payload/` files; verify it against the original ZIP layout or that explicit map rather than silently rewriting it for this new wrapper location.

The 1C1 archive is 283,668 bytes / 37 members / 36 historical manifest entries, SHA-256 `81d87fb306d542aa2013b25c05776088838ee7de5ab14726d9d25e57991439fc`. Its nested 1B archive is 219,338 bytes / 33 members / 32 entries, SHA-256 `d2c89ead12ab89e4bb551d4dbb4ff3cfeacbc1b2f7a3490399e22faf56e5176f`. Nested 1A is 129,557 bytes / 45 members / 44 entries, SHA-256 `d515cbebf715bb3f4473663b10217ba61b7770f607f7849ec8f9fe667fac63da`. All 112 historical manifest hashes pass; all 37 unpacked 1C1 members and five selected prior CSV copies match their exact original nested bytes.

The original 41-entry restore map and historical payload manifest, and the 48-entry saved manifest plus its own file, also verify. The standalone historical checkpoint and formerly orphaned receipt bytes retain their original identities. Detailed per-file hashes and mode comparisons are in `AUTHENTICATION.json`.

## Git and publication boundary

The original bundle is incremental and requires the real assessed source base. Initial pack-only inspection reported one unresolved delta, as expected for this thin bundle. Supplying only the eight authenticated base-tree metadata objects and exact base commit resolved it; the original bundle remains unchanged. The local check authenticated the prepared commit and 49-file subtree in that isolated object store. Retained metadata reproduces all eight base-tree IDs and proves that the prepared root retains all 27 original source path/mode/blob identities outside the new archive. No absent source body or source history was reconstructed, and no full source checkout or source-history fsck is claimed.

A later publisher may create a new additive commit while retaining this exact subtree. The new parent/head, final remote reachability, original-base reconciliation and unchanged-source proof must be recorded by that publisher. A preserved old receipt saying publication was pending remains a historical statement; this staging note does not claim that a new remote checkpoint already exists.

## Research and execution limits

Research remains **PARTIAL**. The full primary Nees–Liebman text was unread; complete source-grounded novelty, protocol acceptance and independent human review are not established. No archived research/publication scripts were executed, no patch was applied, no source retrieval or research test was performed, and this staging step made no remote mutation. Original scripts are retained as inert evidence.

A bounded UTF-8 member inventory/common-credential-marker screen found no unexpected markers. This is not an exhaustive privacy or security audit. No unexpected path, content or mode differences were found.
