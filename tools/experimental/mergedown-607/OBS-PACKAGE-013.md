# OBS-PACKAGE-013 — Windows checkout identity repair

Refs #607 / #608. 2026-11-26. Experimental software qualification only.

## Recovered Windows receipt

[Native job 139769540251](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45778989934/job/139769540251), exact head `e991120ebc69ab3ea4b770a90f958b0c04fa5fc3`: checkout succeeded, Python 3.12.10 / Node 22.23.5; all 11 unit tests passed. The real frozen package build failed at build_observatory.py line 80: `ValueError: Frozen source mismatch: core.js; use byte-preserving checkout`. Exit 1. Artifact and browser steps skipped. [Separate research integrity](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45778989719) passed. No full Windows package qualification claimed.

## Reproduction and minimal fix

The inherited root .gitattributes uses * text=auto; JS/CJS/HTML have no explicit line-ending rule. The pre-checkout global core.autocrlf=false step did not suffice (checkout action uses a temporary HOME/config). Exact checkout bytes on the hosted runner were not captured, so CRLF conversion is a reproduced mechanism consistent with the failure, not a measured hosted file diff.

Locally verified the retained [Linux archive](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/45771992305/artifacts/15094366767): CRC, 26/26 manifest entries, and 7/7 frozen source Git blob hashes. Created a disposable Git repository with the exact root attributes and seven frozen source files. Fresh clone --no-checkout, git config core.autocrlf true, checkout frozen fixture: all seven working-tree blob hashes differed, including core.js. Added only affine-snapshot/.gitattributes with * -text. Repeated fresh checkout under the same setting: all seven hashes matched their upstream pins. git diff --name-only showed only that new attribute file. Executed node legacy-workbench.cjs NEW_DIR and node selective-transfer.cjs NEW_DIR from the repaired checkout (Node 22.16.0, Linux): 10/10 and 8/8 outputs respectively byte-identical to the existing hosted Linux archive. No new audio, no human evidence.

Fix preserves exact snapshot bytes under Git text conversion; never normalizes or relaxes the builder's immutable source check. Scoped to this consolidation snapshot, not repository-wide. Existing single Windows workflow will run against new head. No additional CI matrix or manual reruns. Windows end-to-end and browser gate remain open until receipts exist. Earlier Linux qualification remains valid at its exact ref.

## Reconciliation

Main base 495a98ca12bae467a507031f04931aa4254b1866; all five candidate PRs open, draft and mergeable when inspected. Later refs and successful structural checks are recorded in promotion-ledger.json without changing original frozen pins. Recent spectral-retention, version-bound payload and restart-journal advances remain read-only deferred batches. No change to source lanes, shared protocol, human gates, licensing or owner authorization. No merge. Local Git network retrieval failed exit 128 (Could not resolve host: github.com); connector reads and existing retained archive enabled actual native regression.

## Remaining

Recover exact-head Windows package + Chrome result; compare native output against Linux using explicit artifact versus numerical equivalence, then settle permanent source location without duplicate live implementations. Overall #608 Draft/HOLD; bounded Linux package QUALIFIED FOR OWNER REVIEW only.
