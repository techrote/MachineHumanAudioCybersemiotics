# R005 C9 targeted review-to-reference chaining — 10 November 2026

[Coverage memo](../../../sources/auditory/README.md) · [Frozen protocol](../../../protocol/PROTOCOL-v1.md) · [Issue #5](https://github.com/techrote/MachineHumanAudioCybersemiotics/issues/5)

## Scope and recorded retrieval

A bounded **supplementary C9 backward-chaining** pass was made on Dang, Elelu, Le & Le (2022), *Augmented Hearing of Auditory Safety Cues for Construction Workers: A Systematic Literature Review*, *Sensors* 22(23):9135, DOI [10.3390/s22239135](https://doi.org/10.3390/s22239135), PMCID [PMC9740817](https://pmc.ncbi.nlm.nih.gov/articles/PMC9740817/). The article's rendered HTML §References was inspected along with the relevant §2 and §5 review discussions. Five **selected** references (#33, #38, #39, #101, #102) were followed to publisher, PubMed, institutional or conference metadata/routes. All were published before the frozen **2026-10-04** cutoff.

This is **not** a new completed search run, a complete backward chain for the review, a lossless reference-list export, or a complete article/research corpus screen. In particular, the review discusses environmental acoustic *detection*, whereas MHAC's Track E question concerns the communication of machine state to humans. Noise and hearing protection supply transport context, but detection of natural ambient sounds does not imply a machine-generated auditory message. A non-auditory wearable provides an alternative modality, not a positive auditory result. The selected five items are purposefully chosen candidates/controls, not a representative random sample.

**Actual interface:** public C8 web navigation and rendered PMC/publisher/PubMed/institutional pages on 2026-11-10 UTC. The web interface did not return original HTTP response bytes or a durable lossless export or measured per-request UTC timestamps; therefore no response-byte SHA256 or full-text hash is claimed. Observation date and stable URLs are retained in [OBSERVATIONS.json](OBSERVATIONS.json); re-fetching now would be a new observation, not bitwise replay. No direct OpenAlex EQ1 request succeeded: a separate local DNS probe against `api.openalex.org` failed to resolve, and web navigation to its API was inaccessible; this says nothing about the current service's daily allowance.

## Five navigational leads, *not* five included studies

| Parent ref | Routed work | Verification and pending R006 question |
|---|---|---|
| **#33** | Marks & Teizer 2013, [DOI 10.1080/01446193.2013.783705](https://doi.org/10.1080/01446193.2013.783705) | Publisher abstract identifies RF proximity-alert field experiments. Alert output modality and human-action outcomes not established. |
| **#38** | Brungart et al. 2014, [DOI 10.1121/1.4893932](https://doi.org/10.1121/1.4893932) | PubMed abstract identifies complex-listening/spatial awareness research, not necessarily machine-message communication. |
| **#39** | Vinnik et al. 2011, [DOI 10.1371/journal.pone.0017266](https://doi.org/10.1371/journal.pone.0017266) | PubMed abstract addresses interrupted sound perception; [public PMC text route](https://pmc.ncbi.nlm.nih.gov/articles/PMC3046163/) identified, but not read in full. |
| **#101** | Sakhakarmi et al. 2021, [DOI 10.1016/j.autcon.2021.103613](https://doi.org/10.1016/j.autcon.2021.103613) | [UNLV institutional abstract](https://oasis.library.unlv.edu/fac_articles/840/) documents **tactile** warning feedback, a non-audio comparator. |
| **#102** | Goodman et al. 2020, [DOI 10.1145/3313831.3376406](https://doi.org/10.1145/3313831.3376406) | CHI work with a [university-hosted PDF route](https://courses.cs.washington.edu/courses/cse590w/20sp/GoodmanCHI2020.pdf); presence of sound sensing does not establish auditory output. No PDF byte or page examination claimed. |

## Impact, nonduplication and handoff

The R005 issue's previous 150 search records/21,483 discovery occurrences and the 69-item October known-item benchmark **remain unchanged**: these five source leads are not registered `search_hit` records. R006 must check each DOI against retained C1/C8/C9 and source records, preserve pre-existing occurrence provenance, and conduct eligibility screening under frozen E1–E6 before any admission or study/sample aggregation. No `research/registry/identity` or `research/screening` file was edited here.

Of 2022 review's broader references, only these five were selected; the **remaining reference list is not marked complete or excluded**. The review's cited sources mix sound recognition technologies, perception, alerting, HCI and non-auditory controls. Before scaling C9, prioritize directly relevant reviews from EQ8 and accepted R006 included reports. This supplement is explicitly lower priority than a lawful immutable EQ1 continuation, which still lacks the 9,368-result complete sorted run (last retained 4,200 unique IDs).

## Verification and reproducibility

Run `python -m unittest tests.test_r005_c9_construction_review -v` if `tests` is importable, or `python -m unittest discover -s tests -p 'test_r005_c9_construction_review.py' -v`. Follow with `python -m unittest discover -s tests -v`, `python tools/validate.py` and `python -m tools.build_record_fixtures --check`. These tests verify observation-ledger *integrity and negative admission constraints*, not whether the underlying publisher articles have the recorded content.

**Work still gated:** C1 EQ1 partial; remaining C9 review/included-report chaining; C3/C4/C6/C7 database access gaps; R006 deduplication, screening and corpus. No human source review, peer review, effect estimate, newly admitted study or permission event is asserted.

**Next action:** An integration shepherd should review the five bibliographic routes and accept/reject this bounded C9 supplement as discovery-only. R006 should first resolve duplicate discovery paths and screen the most promising abstracts. When authorized network access and quota work, resume EQ1 in a new immutable invocation without changing its frozen terms or overwriting the previous prefix.
