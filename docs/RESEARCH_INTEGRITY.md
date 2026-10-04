# Research integrity and claim discipline

[RAG](../RAG.md) · [Data model](DATA_MODEL.md) · [Human gates](HUMAN_GATES.md)

## What the programme may claim

The goal is doctoral-level rigor in questions, scholarship, argument, critique and reproducibility. That is an ambition, not a credential, an assurance of novelty or a claim that external experts have approved the result. A substantial negative or qualified conclusion can be valuable. Word count, technical vocabulary, model confidence and green CI are not evidence of rigor.

The original project preference is intelligible, deliberately non-human audio that communicates state without dependence on simulated worry, apology or excitement. Treat it as a design constraint. Do not attribute it to Brier, establish it by citing the repo itself, or screen out contrary evidence. Linguistic prosody and intelligibility must not be conflated with emotional impersonation. Avoiding attributed machine emotion does not imply avoiding all affect in a listener.

## Claim classes

| Class | Minimum basis | Permitted interpretation |
|---|---|---|
| Project constraint | Explicit project instruction or recorded design decision | What this project chooses, not what experiments prove. |
| Source claim | Identified source and exact locator | What the author argues or reports; not automatically true. |
| Empirical finding | Traceable study/outcome data and appraisal | What evidence supports within its uncertainty and boundaries. |
| Theoretical interpretation | Source premises plus explicit inferential argument | A reasoned reading, potentially contested. |
| Synthesis proposition | Traceable integration and counterarguments | Candidate contribution with limits and possible falsification. |
| Design hypothesis | Mechanism, sources/claims, operational variables and test | An unvalidated prediction unless later evidence supports it. |
| Unvalidated convention | Declared arbitrary/provisional choice and reason | A practical placeholder, not a research finding. |

Keep class separate from lifecycle (`proposed`, `source_checked`, `internally_audited`, `externally_reviewed`, `superseded`, `withdrawn`) and confidence. An internally audited hypothesis is still a hypothesis. A source checked by an agent is not human-verified. Do not promote a source's assertion to empirical evidence by copying its abstract.

## Source truthfulness

Record metadata verification, access extent, reading extent, version and verification actor independently. A landing page confirms only what is visible there. Reading a selected section does not mean the entire book was read. Quotes and quantitative values require exact page/section/table/paragraph or equivalent locators; distinguish printed page numbers from PDF page indices. For crucial claims retrieve the whole relevant passage and inspect diagrams/tables where needed. Record uncertainty, translation and interpretation rather than guessing missing text.

No invented DOI, author, year, study participant, statistic, quote, source hash or credential. Verify metadata conflicts rather than silently picking a plausible version. Preserve source corrections/retractions and their downstream effects. Reviews and their component studies must not be counted as independent primary observations of the same data.

## AI-assisted work and reviewers

Log tool/model identity where known, date, task, input/source IDs, output artifacts, verification steps and limitations. Do not invent a model version when unavailable. Save reproducible task instructions or concise decision rationales, not private hidden reasoning. AI screening/extraction may be useful but is disclosed as such; repeated tools or agents are not independent human reviewers. Record who actually read or checked a passage and what checks were performed.

Human external feedback has its own gate and provenance. A self-review, GitHub approval, source-locator test or successful statistical script does not establish peer review, theoretical correctness, ethics approval or effective human communication.

## Rights, privacy and public-repository boundary

The repository is public. Commit original notes, bibliographic metadata, permitted extracts and lawful derived data with provenance. Do not commit restricted books/full articles, credentials, signed consent, personally identifiable participant information, sensitive hearing/health data or private correspondence. Keep restricted raw material outside the repository with a rights/access record; `.gitignore` is not a privacy audit.

Do not choose a software/data/paper license or grant redistribution rights on the user's behalf without authorization. Record third-party rights and proposed licensing choices for the human gate. Likewise, do not invent authorship, affiliations, contributor consent, a registration identifier or publication status. No purchase, outreach, recruitment or external submission is implied by a request to implement repo issues.

## Bias and critical practice

Search contradictory results and alternatives. Preserve incompatible meanings of key terms instead of harmonizing them by fiat. Report access, language, indexing, publication, verification and task-transfer limitations. No significance vote counting or selective extraction of favorable outcomes. Appraise theory and experiments using different appropriate criteria. Distinguish no evidence, imprecise evidence, evidence of absence and an untested preference.

Every major final claim needs a chain from source/extraction through interpretation and evidence appraisal to implication and validation status. Keep a counterargument field and a revision criterion. When evidence changes, amend downstream claims, designs and manuscript together. Final conclusions must visibly reflect material limitations, not bury them in a disclaimer.
