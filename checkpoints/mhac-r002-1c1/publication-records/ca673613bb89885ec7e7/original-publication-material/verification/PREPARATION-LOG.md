# Local preparation record

Prepared from the actual four mounted inputs, not from prior-chat summaries.

## Performed

- Read the interrupted publication record and retrieved the final 1C1 handoff for orientation.
- Opened the original ZIP, standalone receipt, checkpoint and progress record; checked their byte sizes, SHA-256 and Git blob identities.
- Checked all three nested archive manifests (36 + 32 + 44 records), inventories, CRCs, receipt agreement and five prior-copy identities. Readability/privacy inspection did not run archived scripts.
- Read the exact source commit, complete recursive tree and visible heads through the GitHub connector; main matched the source pin and no checkpoint-prefix branch was returned.
- Direct Git cloning failed with DNS resolution error; archive download did not yield a file. No source-file reconstruction or expanding retrieval campaign followed.
- Recreated only exact Git metadata: original commit raw bytes match `796151a33ec7a1acc026b239fe5c883312ebf40b`, and all eight source tree objects match the live tree. An initial signature-header serialization did not match and was discarded; the final exact object includes the original trailing signature continuation line. No fabricated base was used.
- Constructed 49 exact saved blobs and a single additive commit with 27 unchanged original source path/mode/blob identities.
- Created the standard incremental bundle and checked its prerequisite/ref header, Git bundle verification and isolated unbundle.
- Independently checked all saved bytes after import and ran Git pack integrity checks. The resolved pack contains 71 objects: all 70 new objects plus the prerequisite base tree used to resolve a thin-pack delta. This is an integrity check, not a repository/research test.

## Not performed

No remote mutations in this preparation. No research tests or archived script executions. No full original source checkout or full original-history fsck. No scientific/registry validation, source access retries, CI polling or dispatch. No active-register changes, PRs, merges, comments or issue actions.

The unsigned local commit is `3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252`. Its timestamp is local preparation metadata only. Historical receipts and results remain unchanged. Bundle import was exercised in a disposable local metadata object store; a later publisher must import against the actual complete source base before pushing.
