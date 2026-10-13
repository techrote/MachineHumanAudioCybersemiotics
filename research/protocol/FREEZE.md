# Protocol v1 freeze record

[Protocol](PROTOCOL-v1.md) · [Protocol index](README.md) · [Issue #2](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/2)

## Freeze

| Item | Value |
|---|---|
| Protocol version | v1 |
| Freeze date | 2026-10-13 (files finalized at 01:40 UTC) |
| Baseline literature cut-off | 2026-10-04 (unchanged from the programme baseline) |
| Repository base at freeze | `main` at `8ad50e8226b7295ec37b9034be6ae0fd2e44d39d` |
| Branch | `mhac-r002/protocol-freeze` |
| Landing commit | Recorded below after merge; the squash-merge commit on `main` is the authoritative freeze commit |
| External registration | **None.** No registry, timestamp service or journal received this protocol. |

## Frozen artifacts

| File | Bytes | SHA-256 |
|---|---:|---|
| [PROTOCOL-v1.md](PROTOCOL-v1.md) | 35,901 | `9ca38fdb1a973d7ab4b07a1d2131354e9d33cfc88cfa27c4714d02b399c96a4f` |
| [ANALYSIS_PLAN-v1.md](ANALYSIS_PLAN-v1.md) | 17,629 | `c4d89a8b56c01698c34c907645c013c507bd91e4b2a5cc9ac6ce5afe0a18db89` |
| [GLOSSARY-v1.md](GLOSSARY-v1.md) | 7,851 | `e330247c66b165a1c06ac6f7764da6f89de99f983a7179fdfab9dfc1ceeb1ee4` |

The same digests are bound in the live registry's `protocol` stage declaration, which the validator rehashes on every run. Any byte change to these files without a new version and a `protocol_change` amendment fails validation.

## Roles and support

| Role | Who | Basis |
|---|---|---|
| Protocol preparation, pilot, novelty audit | Claude (Anthropic), executing agent in a claude.ai cloud session; model `claude-opus-5-5` as reported by the session | Agent work recorded in `AID-R002-*` records |
| Instruction to continue the research plan | Repository owner (GitHub account `techrote`), in chat on 2026-10-13 | Authorization to execute; **the owner did not review or approve the protocol's content** |
| Independent human review | None | — |
| Funding or sponsor | None recorded | — |

No authorship, affiliation, licence or endorsement is asserted by this record.

## What the freeze does and does not mean

It fixes Track E rules and the analysis plan before production searching, selection and effect extraction, and binds them to exact bytes. It does not establish that the rules are optimal, that the searches will be executable (see the database gate), that any source was read beyond the recorded extent, or that anyone other than the executing agent checked the work. Track G concepts continue to evolve through the concept register.

## Post-merge addendum

Appended 2026-10-13. This addendum does not change any frozen artifact.

| Item | Value |
|---|---|
| Pull request | [#24](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/24), head `f106b799a9a343b85d8d76fd2cd13a532f993dd7` |
| PR-head CI | `repository-integrity` success, [run 38333365192](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/38333365192) |
| **Freeze commit (squash merge on `main`)** | [`ba8599d6e07140d04d46e858d80d0f12d4fbe10d`](https://github.com/techrote/MachineHumanAudioCybersemiotics/commit/ba8599d6e07140d04d46e858d80d0f12d4fbe10d) |
| Post-merge CI on that commit | `repository-integrity` success, [run 38333481456](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/38333481456) |
| Post-merge local check | 216 unit tests OK; validator `pass` against base `8ad50e8`; frozen digests unchanged |
