# R005 recovery checkpoint — 3 November 2026

[Coverage and limitations](../../../sources/auditory/README.md) · [Search inventory](../README.md) · [Issue #5](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/5)

## Preserved starting point

The existing `mhac-r005/auditory-search` branch at `d3869293c90f4a1c136041dd5144ae1c057fa4dc` contained 128 search records and 2,244 occurrences and had not merged. Recovery reconciled it with accepted main `17744bafca1297e8b94a0684d9011489506ba319`, preserving R004 and R005 history. `INTEGRATION.json` records registration time separately from actual network times.

## Retained work

| Directory | Evidence and checks |
|---|---|
| [database](database/AUDIT.md) | Frozen-query access probes, three invocations, hash/count verification, seven complete families and explicit EQ1 budget stop |
| [icad](icad/README.md) | Available Georgia Tech series enumeration, 35 issued-year outcomes, failures and lossless raw-response storage |
| [references](references/README.md) | Direct retrieval, manuscript-version reconciliation, two bibliography exports and timed navigation |
| [reviews](reviews/README.md) | Three more bibliographies and separate AI boundary verification |

New records use SRCH-R005R, HIT-R005R, AID-R005R and new source identities. The [offline integrator](../../../sources/auditory/scripts/build_r005_recovery_records.py) checks hashes/counts and preserves historical revisions. Probe/access ledgers are diagnostic evidence; production occurrence totals do not count feasibility probes again.

## Completion boundary and next action

The final OpenAlex response reported zero credits at `2026-11-03T01:06:18Z`. Final sorted EQ1 retained 4,200 of 9,368 reported records; all attempts together retained 4,549 distinct EQ1 IDs. Later continuation needs a separate invocation with the same filter, actual times/counts and overlap reconciliation. No unattended retry is scheduled.

R006 must adjudicate identity, screen reports, record unavailable texts, select theory under its separate criteria and assess study/sample overlap. Further included-report chaining depends on these outputs. EQ8-review chaining and forward citations remain incomplete. An available PDF or bibliography entry does not establish eligibility or complete reading.

This work supports a **partial evidence-preserving PR referencing #5**. Protocol §11 stopping conditions are unmet. Issue #6 depends on #5, while §11 includes #6-owned screening; the coverage memo records the staging reconciliation. Bounded preparatory R006 work can land without declaring either issue or the corpus complete. The existing human access gate is not marked satisfied by an agent.

## Verification boundary

Offline reproduction, history checks, tests and CI establish structural integrity. Source-fidelity checks cover identity and specified reference ranges. They establish neither empirical conclusions nor independent human review nor exhaustive coverage.

## Landed evidence

The recovery landed in [PR #28](https://github.com/techrote/MachineHumanAudioCybersemiotics/pull/28), squash commit `8c4629180d9d81744f3e7c067fff4f35211e2d0d`. The published tree exactly matched validated local tree `2488758eda4f7d8c0ab4add4af54e25b4cf9e7c0`. [Final PR-head CI](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/41561016673) passed on `b1024823d6dbdddb6b0662fd393abe3d86fd822d`, and [push CI](https://github.com/techrote/MachineHumanAudioCybersemiotics/actions/runs/41561149891) passed on the merged main commit. Issue #5 remains open for the acceptance limits above; landing this tranche does not close the research gate.
