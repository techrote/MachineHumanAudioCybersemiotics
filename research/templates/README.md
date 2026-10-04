# Record-writing templates

[Data contract](../../docs/DATA_MODEL.md) · [Integrity](../../docs/RESEARCH_INTEGRITY.md)

These are field prompts, not schema-validated real records. MHAC-R001 implements the machine-readable contract and fixtures. Do not copy blank templates into live registers and mark them complete.

## Source note

```text
Source ID and publication identity:
Exact author/editor, title, date and edition/version:
Verified identifier and provenance URL:
Access status and lawful local holding/hash, if any:
Rights/redistribution basis:
What was actually read, when and by whom/what:
Exact printed/file page, section, table or paragraph locators:
Source claim or observation:
Our interpretation (separate):
Relevant RQ and boundaries:
Contrary reading / missing evidence:
Verification performed and independence limits:
```

## Empirical extraction

```text
Source / study / experiment / sample / condition / outcome IDs:
Task, stimuli, population, training and exposure:
Design, counterbalancing and comparison:
Reported estimate, units, uncertainty/dispersion and n:
Source locator for every value:
Missingness, overlap and repeated-measures dependence:
Derived value, inputs, transformation and assumptions (if any):
Risk-of-bias / construct / transfer appraisal:
Verification actor and scope:
```

## Claim and design implication

```text
Claim ID, class and exact statement:
Sources/extractions or explicit project-constraint basis:
Premises and inferential chain:
Expected mechanism and applicability:
Strongest counterargument / alternative explanation:
Uncertainty and limitations:
Proposed requirement or hypothesis ID:
Discriminating test and rejection/revision criterion:
Lifecycle and actual verification level:
Affected manuscript/design locations:
```

## Amendment / audit finding

```text
ID, date, actor and issue:
Prior version/rule and new proposal:
Reason and prior exposure to evidence:
Affected sources, decisions, analyses, claims and outputs:
Required rework and tests:
Finding severity, resolution or remaining limitation:
Actual acceptance evidence:
```

## Assistance disclosure

```text
Date, task, actual tool/model or unknown:
Source/input IDs and output artifacts:
Public task instruction or concise decision rationale:
Verification steps actually performed:
Known limitations and human-review status:
```

Never substitute hidden model reasoning for an auditable source/decision record. Synthetic examples belong in fixture/simulation paths with an explicit synthetic flag and must never feed live study counts.
