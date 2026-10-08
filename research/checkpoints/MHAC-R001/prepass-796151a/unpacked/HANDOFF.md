# HANDOFF — MHAC-R001 prepass

**Repository / issue:** techrote/MachineHumanAudioCybersemiotics #1, MHAC-R001.
**Assessed main commit:** `796151a33ec7a1acc026b239fe5c883312ebf40b` (tree `40afaeebb1801fd8adf1417a8da7523bff014d9f`). Issue open; one comment read; no open PR returned. No GitHub mutations, comments or workflow actions were performed.

## Read first

`proposal/docs/R001_PREPASS.md` is the architecture, record graph, complete proposed dictionary, lifecycle decisions and validation-layer boundary. `assessment/WORKED_EXAMPLE.md` maps the actual synthetic snapshots. `assessment/IMPLEMENTATION_ORDER.md` names intended repository files in order and maps them to all six acceptance criteria.

## Actual files and results

`proposal/tools/validate_records_prepass.py` is the executable cross-record prototype; `proposal/tools/build_r001_fixtures.py` deterministically rebuilds the frozen synthetic sources/cases. `proposal/tests/test_records_prepass.py` exercises the example and hard relationships. Intended paths are those beneath `proposal/`, relative to the repository root. `proposed.patch` adds only those files; it does not modify bootstrap authorities, install a live registry or wire a new CI gate.

`baseline/tools/validate.py` and `baseline/tests/test_validate.py` match their assessed Git blob IDs. This packet is not a full repository checkout. A direct clone failed DNS; authority/issue reads used the GitHub read connector. Full-checkout repository validation was not simulated or claimed.

Final local overlay: **70 tests passed** (26 retained bootstrap + 44 prepass); all **33 CLI cases** matched expected outcomes (5 positive, 28 negative). `results/unit-tests-final.txt` is the final 70-test run. `results/execution.json` retains the separate 33-case replay and its earlier 67-test invocation; three exact-audit-binding tests were subsequently added and passed in the final run. The validator implementation was unchanged between the completed CLI replay and the final 70-test run. Remote bootstrap CI success is historical, not CI for this patch.

## Reproduce

From the extracted packet, run `python verify_packet.py`, then `python run_prepass.py --output rerun-results`. Python 3.11+ is intended; actually tested here with Python 3.13.5. No network or secrets are required. In a reconciled checkout, the proposed module also supports `python -m tools.validate_records_prepass INPUT --dataset-kind fixture --previous PRIOR`.

## Next action and questions

Reconcile live main before applying anything. Review this design, then implement #1 in the file order supplied. Required infrastructure still includes full schemas, live loading/history integration, search/screening flow, citation/export/gate checks, sample-overlap/alias handling and CI integration. This prepass does not close #1 or establish R002 acceptance.

Scientific questions remain: protocol-specific sufficient reading coverage; actual report/sample identity and dependence; appropriateness of appraisal and any pooling; source entailment/contrary evidence; genuine independent human review and authorized study evidence. These must remain open until actual evidence and method work answer them. Structural pass is never scientific proof.
