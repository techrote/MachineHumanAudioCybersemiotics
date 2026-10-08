# MHAC-R002 1C1 — publication-ready checkpoint package

**Local checkpoint complete; not pushed to GitHub. Research remains PARTIAL.**

The main payload file is `MHAC_R002_chunk1C1_publication.bundle`. It holds the complete new archival commit, including the previously orphaned receipt blob, the exact original ZIP/receipts/checkpoint, nested 1A/1B prerequisites, browsable 1C1 files and publication metadata. The `payload/` directory independently provides all 49 saved files.

## Download integrity

Bundle SHA-256:

```text
4bf56d8cad4157f902b48484b606dfad635ff304acd1be7eaab8251b678f28f6
```

The same checksum is in `MHAC_R002_chunk1C1_publication.bundle.sha256`. `SHA256SUMS` covers every other file in this outer package, including the bundle and verification records. The final ZIP checksum is supplied outside the ZIP; putting the ZIP's own final hash inside it would create a self-reference.

## Exact prepared Git state

| Field | Value |
|---|---|
| Repository | `techrote/MachineHumanAudioCybersemiotics` |
| Local checkpoint commit | `3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252` |
| Exactly one parent | `796151a33ec7a1acc026b239fe5c883312ebf40b` |
| Prepared root tree | `e58c33056e95365922f20fab377abe06bbe8fc1a` |
| Intended branch | `checkpoint/mhac-r002-1c1-ca673613bb89885ec7e7` |
| Saved directory | `checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/` |
| Saved files | 49 |
| Changes outside that directory | 0 |

**The bundle is incremental, not a standalone repository clone.** The importing repository must already contain source commit `796151a33ec7a1acc026b239fe5c883312ebf40b` and its unchanged source objects/history. This preserves the full existing tree rather than replacing it with the partial research packet. The package is self-contained for checkpoint data, but not for the pre-existing repository. No unseen source files have been invented.

## Verify locally without network access

Python 3.9 or newer, from this extracted package directory:

```sh
python verify_publication_package.py
```

With Git installed, also exercise isolated bundle import and verify every saved blob:

```sh
python verify_publication_package.py --git
```

The optional Git check uses a disposable local object store, the exact verified source commit/tree metadata, and the bundle. It performs no GitHub requests or writes and executes no archived research script. It does not claim that this metadata-only verifier is a full source checkout or a full source-history fsck.

## Publish in a later checkpoint-only step

See [MINIMAL-RESUME.md](MINIMAL-RESUME.md) and [PUBLICATION-PLAN.json](PUBLICATION-PLAN.json). Reconcile current repository instructions/workflows and the exact destination before any write. The candidate is already a finished single-parent additive commit; it does not need research continuation or regeneration.

An isolated repository with the real base can import this bundle using `git fetch <bundle-path> refs/heads/checkpoint/mhac-r002-1c1-ca673613bb89885ec7e7`. Confirm `FETCH_HEAD` equals `3ae79ab787f9ea0fbd13d41e0fbfc8022e92b252` and verify all saved bytes before pushing. A different existing destination must not be overwritten. Do not use force, create a PR, merge, change live registers/queues, close issues or dispatch workflows.

Only after the remote branch resolves to this intended commit and all saved bytes verify may the publisher report `GIT_CHECKPOINT_VERIFIED`. This package reports `LOCAL_CHECKPOINT_READY`, not repository or research acceptance.

## Original evidence and recorded limits

Start with [SAVE-README.md](payload/checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/SAVE-README.md) and the [unaltered 1C1 checkpoint](payload/checkpoints/mhac-r002-1c1/ca673613bb89885ec7e7/packet/MHAC_R002_chunk1C1/CHECKPOINT.md). The original packet remains SHA-256 `81d87fb306d542aa2013b25c05776088838ee7de5ab14726d9d25e57991439fc`.

Current byte checks passed for all 36 + 32 + 44 historical manifest entries, nested receipts, exact archive inventories, CRCs and five selected prior-file copies. The separate independent Git import checked all 49 saved files and retained all 27 original source path/mode/blob identities. None of those checks is scientific validation.

The original comparator full text remains inaccessible/unread; methods, results, tables and limitations remain unknown. No new source acquisition, research test, registry validation, statistical analysis, protocol freeze or novelty claim was performed.

## What is included and excluded

All three supplied checkpoint artifacts and the previous local stop record are preserved byte-for-byte. No genuine checkpoint file was excluded. Earlier 1B and 1A dependencies are retained inside the original nested ZIPs. Restricted texts, credentials and unrelated private data are not added. The original repository base remains the explicit Git prerequisite; comparator full text is still a separately gated research input.

The existing remote orphan receipt does not need to be present for restoration: its exact bytes, SHA-256 and Git blob identity are included. The local commit now reaches that receipt object; no claim is made that the remote orphan has become reachable yet.
