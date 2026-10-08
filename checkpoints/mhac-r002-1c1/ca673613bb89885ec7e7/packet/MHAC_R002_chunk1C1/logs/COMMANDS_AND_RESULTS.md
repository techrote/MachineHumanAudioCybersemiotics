# Commands, tool reads and actual results

[Checkpoint](../CHECKPOINT.md) · [Access ledger](../provenance/ACCESS_LEDGER.csv) · [Input verification](../provenance/INPUT_HASH_VERIFICATION.json)

## Local execution boundary

All writes were confined to one new task workspace, `/mnt/data/mhac_1c1_20261004_9c40fdua`. Supplied packets were read, never edited. Other agents' workspaces and sibling repositories were not traversed. No GPU, USB, shared native-test environment, package installation or credential access was used.

The first environment timestamp was `2026-10-04T16:22:08Z`. An early checkpoint was written during workspace creation. The source-access decision was saved before the final matrices. Commands had explicit 10- or 15-second tool timeouts; web/connector per-request timeouts are not exposed and no values are invented. Retrieval was finite, not a retry loop or background job.

## Commands and outcomes

| Operation actually performed | Command or equivalent | Timeout | Actual result |
|---|---|---|---|
| Verify supplied files and read PDF tool instructions | `date -u +%FT%TZ; ls -l <1A.zip> <1B.zip>; cat /home/oai/skills/pdfs/SKILL.md` | 10 seconds | Both archives present; sizes 129,557 and 219,338 bytes. No PDF was subsequently acquired. |
| Create isolated workspace, early checkpoint, inspect ZIP inventories and restore safely | Inline standard-library Python: `mkdtemp`, `ZipFile.testzip`, reject absolute/traversal member paths, `extractall` into task-owned `restored/` | 10 seconds | Archives readable; no unsafe member paths; original packets unchanged. |
| Verify every preceding manifest member and inventory | `python packet/scripts/verify_inputs.py <1A.zip> <1B.zip>` | 15 seconds | PASS: 1A 45 members/44 hashes; 1B 33 members/32 hashes. Output saved in INPUT_HASH_VERIFICATION.json. |
| Verify receipt and nesting identities | Inline Python SHA256 and byte comparisons | 15 seconds | 1B equals receipt SHA256; standalone 1A equals nested 1A. Original 1B/receipt copied unchanged into delivery inputs. |
| Read required prior findings | Bounded `cat` and `csv.DictReader`/JSON inspection batches | 10 seconds per batch | Both checkpoints; 1A scope/RQ/record/coverage/snapshot; 1B 28 decisions, adaptation, open questions, coverage and six deferred packages. Truncated display batches were followed by focused reads. |
| Write source-access checkpoint and missing-input note | Inline Python UTF-8 writes | 10 seconds | PARTIAL access boundary saved; primary body fields not populated. |
| Generate original audit notes and matrices | `python packet/scripts/build_audit.py` at execution time | 15 seconds | Reading/identity record, six-RQ matrix, fourteen-field unknown ledger, two conditional candidate questions, next-input note, provenance and manifest written. Construction helper moved to task scratch afterward; not part of deliverable or a research implementation. |
| Preserve only portable prior copies | Inline Python byte-preserving copies and local-note adjustments | 10 seconds | Five exact prior CSV copies; prior Markdown kept in its original archive context. Input identities unchanged. |
| Final packet integrity verification | `PYTHONDONTWRITEBYTECODE=1 python scripts/verify_packet.py <packet-root>` plus ZIP member checks | 15 seconds | Actual final result is recorded in the external archive-verification receipt. These are packet checks, not repository/research tests. |

## Read-only GitHub operations

The connector was discovered through `api_tool.list_resources(paths=["GitHub"], query="fetch")`. Reads: branch collection, all-state issue changes since `2026-10-04T15:53:27Z`, open PRs, and full pinned AGENTS/runbook/seed/search/protocol files. Main pin unchanged; recent issue list and open PR list empty. Exact endpoint/commit/blob references are in REMOTE_REFRESH.json. No CI reads/polling, workflow actions, issue/comment/PR/review writes, branch mutations, settings changes or humagent actions occurred.

The delta query reuses the previously verified #1/#2 state and acceptance limits; it is not represented as a new complete issue/comment or acceptance audit. Observations were collected sequentially, not atomically.

## Source retrieval coverage

ACCESS_LEDGER.csv records the exact sequence: one publisher route and two lawful alternatives, including navigation, a malformed author-link normalization, institutional host normalization, and a final direct-file attempt within the existing preprint route. Two exact-identity web-search batches contained three queries. These were source-location attempts, not pilot database queries or production literature searches. The search engine exposed incidental third-party previews; no third full-text alternative or second comparator was opened.

All primary-text routes failed. Only institutional/author bibliography entries were read. No external full text was downloaded or hashed, no source PDF was inspected, and no snippet/abstract was promoted to methods/results evidence. HTTP 403/502 and tool-inaccessibility messages are route failures, not proof of a global access barrier or article absence.

## Tests not run

Repository tests, registry/schema validation, numerical reference checks, empirical analyses, meta-analysis recomputation, primary-study re-extraction and scientific acceptance checks: **zero**. Prior 1A test results remain historical results in the unchanged input packet, not tests repeated in this chunk. No independent human source verification or review occurred.

## Final packaging command

```sh
PYTHONDONTWRITEBYTECODE=1 python packet/scripts/package_packet.py packet MHAC_R002_chunk1C1_packet_2026-10-04.zip
```

Executed from the isolated task workspace with a 15-second timeout. This command writes SHA256SUMS, invokes the packet verifier, builds the archive, then reads and compares every archived member against the hashed local payload. It also verifies unchanged embedded 1B and nested 1A inputs. The external `MHAC_R002_chunk1C1_archive_verification.json` supplies the final PASS/FAIL result and exact counts/hash. No network calls or repository tests occur in this packaging command.
