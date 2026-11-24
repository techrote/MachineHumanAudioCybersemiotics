# MHAC-T001 — warning failure paths (research prepass)

[Issue #30](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/30) · [Taxonomy](TAXONOMY.md) · [Candidate evidence](CANDIDATE-EVIDENCE.csv) · [Protocol sketch](PROTOCOL-SKETCH.md) · [Decision log](DECISION-LOG.md)

**State: proposed research tangent, not accepted Track E evidence or a completed R009/R014 analysis.** Prepared on 2026-11-03 UTC from publisher/PubMed abstracts and publicly accessible publisher HTML results/discussion. No participant testing, preregistration, human independent review, quantitative effect extraction, risk-of-bias appraisal or formal screening.

## Objective and scope

Test whether one generic warning success/failure obscures distinct **observable** endpoints: signal presence, report of detection, source identity, requested-action interpretation, chosen action and deadline-sensitive completion. A missing response is not proof of masking, inattention, failed comprehension or refusal. The proposed classification is a *measurement design*, not a validated cognitive architecture.

This work is disjoint from #5's search inventory, #6's canonical identity/selection ledger, #9's empirical extraction, #12's accepted semantics and #14's eventual experimental protocol. It creates no live evidence records, inclusion decisions, accepted findings or modifications to frozen protocol v1. Historical literature cut-off remains 2026-10-04.

## Artifacts and replication

| Artifact | Function |
|---|---|
| [TAXONOMY.md](TAXONOMY.md) | Observable endpoints, unknown attribution and falsifiable model comparison |
| [CANDIDATE-EVIDENCE.csv](CANDIDATE-EVIDENCE.csv) | Five bibliographic identities, verified public-source locators and evidence limits |
| [PROTOCOL-SKETCH.md](PROTOCOL-SKETCH.md) | Proposed factorial test and instrument/control design; **not run** |
| [DECISION-LOG.md](DECISION-LOG.md) | Explicit competing account, decision rules and gated programme handoffs |
| [SYNTHETIC-ONLY.csv](SYNTHETIC-ONLY.csv) | Twelve explicitly invented alert trials; no people or device observations |
| [analysis.py](analysis.py) and [test_analysis.py](test_analysis.py) | Standard-library-only deterministic calculations and negative/invariant tests |

Commands from repository root, Python 3.11+:

    python research/tangents/warning-failure-paths/analysis.py
    python -m unittest discover -s research/tangents/warning-failure-paths -p 'test_*.py' -v
    python -m unittest discover -s tests -v
    python tools/validate.py
    python -m tools.build_record_fixtures --check

The toy intentionally lacks no-alarm catch trials. Therefore false-alarm rate, sensitivity, specificity, d-prime and criterion are not estimable. Denominators refer to **different assessed subsets**. Cases may not be imported into the live research registry or represented as experiments on people.

## Verification and independence

Single GPT-6 assistant inspected five works' public publisher/PubMed metadata/abstracts on 2026-11-03 UTC and the accessible Results/Discussion HTML of Sanderson et al. 2006; no complete full-text verification or independent human adjudication. The candidate CSV records title, bibliographic identifier, venue, population, public locator, access/reading extent, reported outcomes, confounders and missing evidence per source. No source is yet formally screened or appraised. Potential follow-up publication and sample overlaps remain for #6; different DOIs do not by themselves prove independent samples.

## Interfaces and limits

#5/#6 must verify source identities and eligibility before any empirical inclusion. #9 can consider these **candidate** extraction variables only after actual screening. #12/#13 may test the distinct lifecycle/semantic vocabulary provisionally. #14 may adapt the proposed instrument only through authorized protocol work; human recruitment and evaluation remain gated at #20. #17 should audit any stage-to-cause inferences. Negative or unidentifiable outcomes are legitimate results.

This repository package contains original notes and explicitly fictional data. Linked papers are references, not redistributed third-party publications.
