# R005 C9 clinical-alarm correction and targeted backward-citation audit — 10 November 2026

[Issue #5](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/5) · [Protocol §5](../../../protocol/PROTOCOL-v1.md#5-track-e-sources-and-searches) · [Coverage memo](../../../sources/auditory/README.md) · [Observation ledger](OBSERVATIONS.json)

## Scope and selection

This is a **bounded C9 reference follow-up with C8 metadata verification**, focused on clinical machine-state communication, conflicting design evidence and an authoritative publication correction. The parent is Deschamps et al., *Auditory Sequences Presented With Spearcons Support Better Multiple Patient Monitoring Than Single-Patient Alarms: A Preclinical Simulation*, DOI [10.1177/00187208221116949](https://journals.sagepub.com/doi/10.1177/00187208221116949), first online 7 August 2022. It was already present in R005's OpenAlex EQ6 and Nees–Liebman bibliography occurrences. This tranche **does not create a new hit or claim it was previously unknown**.

The SAGE publisher-rendered abstract, relevant Introduction material, Tables 1–2, conclusion, Appendix A and references were consulted. The paper reports a four-patient monitoring simulation with 60 non-clinicians and manipulates **both** sound category and presentation configuration. These are author-reported details from publisher HTML, not independent result verification or MHAC empirical extraction. Original PDF bytes, source manifests, tables as versioned page-images and study data were not obtained.

## High-impact correction: a four-arm design must not be collapsed

The publisher links [an explicit erratum](https://journals.sagepub.com/doi/10.1177/00187208221131795), DOI **10.1177/00187208221131795**, first online **26 October 2022** (later printed in *Human Factors* **67(11), 2025, p. 1230**). Its correction text says the abstract's Methods description had misidentified both multi-patient configurations as *spearcon* sequences. Items (c) and (d) should instead read **multi-patient sequences**. It also notes minor formatting fixes to Tables 1–3.

**Scientific consequence:** the multi-patient presentation advantage cannot be attributed generically to *spearcons* based on that mistaken abstract wording: the configuration effect spans the IEC auditory-icon condition and the event-specific spearcon condition. The sound-category contrast and configuration contrast require separate study extraction; do not claim this corrigendum changed data or changed effect sizes, since it states no such thing. The corrected abstract and Methods/Table 1 descriptions must be preferred in R006/R009. The erratum itself is not a second experiment or sample.

The *online* correction date, not merely the 2025 printed-volume year, should remain attached to parent-publication identity. Both precede the frozen **4 October 2026** cutoff.

## Source-backed four-reference follow-up

| Parent link | Verified route and reading extent | Unresolved relevance / contrary case |
|---|---|---|
| **Srbinovska et al. (2020)**, 10.1037/xap0000330 | [PubMed metadata and abstract](https://pubmed.ncbi.nlm.nih.gov/32915012/) | Comprehension of time-compressed speech for trained/untrained listeners. The parent's patient privacy/anxiety concern is a design rationale; do **not** claim this experiment directly measured patient anxiety or clinical confidentiality. |
| **Roche et al. (2021)**, 10.1016/j.bja.2021.07.015 | [PubMed metadata and abstract](https://pubmed.ncbi.nlm.nih.gov/34454710/) | Clinical comparisons of speech, icons and prior alarm sounds; context and language/participant limits require primary-text extraction. |
| **Davidson et al. (2019)**, 10.1016/j.apergo.2019.102895 | [PubMed](https://pubmed.ncbi.nlm.nih.gov/31422275/) and [institutional abstract](https://experts.arizona.edu/en/publications/the-impact-of-concurrent-linguistic-tasks-on-participants-identif/) | A **contrary condition** to unconditional speech-cue preference: concurrent linguistic work can impair spearcon identification. R006 must check related conference DOI 10.1177/1071181319631319 for identity/sample reuse. |
| **Deschamps & Sanderson (2021)**, 10.1016/j.apergo.2021.103475 | [PubMed metadata and abstract](https://pubmed.ncbi.nlm.nih.gov/34107432/) | Observational nurses' alarm use, including non-actionable alarms used for awareness. Not evidence that reducing alarms is always beneficial or harmful. |

These are existing or potentially overlapping R005/R006 discoveries, **not four new independent studies**. DOI cross-links and selected existing record paths are in the machine-readable ledger. Evidence has mixed experimental, clinical and observational origins; nothing was screened under E1–E6.

## Query/access provenance and reproducibility

**Interface:** public C8 web search followed by SAGE publisher HTML, DOI-linked publisher erratum, PubMed and University of Arizona rendered metadata/abstract pages on **10 November 2026 UTC**. The exact four search queries and the URLs, locators, reading extent, previous-record cross-refs, negative controls and uncertainties are in [OBSERVATIONS.json](OBSERVATIONS.json). The additional publisher correction was found by the paper's **View correction** link; not a database search. The interface supplied **no lossless ordered result export, original HTTP response bytes, per-request UTC timestamps, original PDF hashes, page-level images or stable total-hit counts**. Therefore HTTP status, response SHA256, original source-file SHA256 and completion/count fields are null/not claimed. Re-fetching a page is a new observation.

A **non-production C1 connectivity probe** via the web URL-open tool attempted `https://api.openalex.org/works?search=auditory%20warnings&per-page=1` on **10 November 2026 UTC** and returned **“URL not accessible via this tool”**. That is a *tool-level rejection*, not an observed HTTP status, successful OpenAlex API invocation, quota measurement, or execution of the frozen EQ1 terms; the request and null response/hash fields are preserved in the ledger. **No new C1/EQ1 run** was executed here. The retained immutable OpenAlex checkpoint remains sorted EQ1 **4,200/9,368** in the dated 3 November recovery; other channels are incomplete. The October known-item benchmark **38/10/21**, historical R005 **150 search records / 21,483 discovery occurrences**, and frozen cutoff are not recomputed or changed by these extra routes.

## Verification and transfer

The issue-scoped unit test checks correction-to-parent identity, provenance limits, disallowed science promotions, known duplicate routes and non-confusion of sound category and configuration. To rerun on the repo tree:

```sh
python -m unittest discover -s tests -p 'test_r005_c9_clinical_correction.py' -v
python -m unittest discover -s tests -v
python tools/validate.py
python -m tools.build_record_fixtures --check
```

**R006:** check correction parent link, known occurrences, journal/conference identity and actual title/abstract screening; treat all 60 as *reported participants in this parent*, not as an admitted independent sample. **R009:** if this work is later eligible and selected, verify full article/versioned Tables 1–3 and analyze factorial effects, without attributing configuration benefits to speech alone. **R005:** continue EQ1 legally with a separate hash-bound invocation when available; remaining review/included-report citation chains and C3/C4/C6/C7 access gaps are unfilled.

This is model-assisted source navigation and selected publisher-text/abstract reading, not independent human source review, full-text admission, trial replication, a completed C9 chain or a coverage-complete corpus. No clinical recommendation is established.

**Dated coverage decision:** four targeted existing-source routes and one *newly documented correction relationship* warrant R006 attention. Zero new canonical searches, canonical hits, admitted studies/samples or corpus-state changes. Issue #5 must remain OPEN.
