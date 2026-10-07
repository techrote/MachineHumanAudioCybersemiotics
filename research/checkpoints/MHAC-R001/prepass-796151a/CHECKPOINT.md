# MHAC-R001 prepass checkpoint

Historical checkpoint for the MHAC-R001 research-record architecture prepass.

- Repository: `techrote/MachineHumanAudioCybersemiotics`
- Issue: #1 / MHAC-R001
- Assessed commit: `796151a33ec7a1acc026b239fe5c883312ebf40b`
- Assessed tree: `40afaeebb1801fd8adf1417a8da7523bff014d9f`
- Original verified ZIP: `MHAC-R001-prepass-796151a.zip`
- ZIP size: 195,264 bytes
- ZIP SHA-256: `7b71bd0a202694c8000619c68d66dfc510a413678345ffaf2035ad01560f2fc1`

## Publication status

This branch is an archival checkpoint only. It is intentionally rooted at the commit assessed by the prepass and must not be merged as the MHAC-R001 implementation. After this prepass was produced, #1 was implemented independently and closed on `main` via PR #22; the accepted implementation commit observed during publication reconciliation was `f08330bf05e124694b276313d76ee68ccc946d48`.

## Preserved here

The architecture/data dictionary, worked synthetic example, implementation order, original ZIP SHA-256 sidecar and verification report are preserved with Git blob identities matching the verified prepass packet. These are the highest-value human-readable checkpoint materials.

The complete original ZIP remains identified by the SHA-256 above. The GitHub connector used for this publication does not expose a binary-file upload path from the local artifact, so the archive bytes themselves are not referenced from this commit. No substitute archive was generated and no claim is made that an incomplete reconstruction is equivalent to the verified ZIP.

## Verified prepass results

- 70 local overlay tests passed: 26 retained bootstrap tests plus 44 prepass tests.
- All 33 CLI cases matched expected outcomes: 5 positive and 28 negative.
- Proposed patch apply-check and byte-equality verification passed.
- ZIP CRC check passed; 64 payload records plus the manifest were verified.
- The deliberate structurally consistent but source-wrong 8 ms extraction demonstrates that structural validation is not source-fidelity review.

## Scientific boundary

This checkpoint records preparatory architecture work. Structural validation does not establish source entailment, study/sample identity, appraisal adequacy, independence, scientific validity, external review or human communication performance.
