# Source and bibliography recovery

[Coverage memo](../../../../sources/auditory/README.md) · [Bibliographic export](REFERENCE-LISTS.json) · [Access observations](access.json) · [Navigation](NAVIGATION.json)

The integrator retrieved the Nees–Liebman accepted manuscript, FRA review and McFarlane et al. sleep-inertia review on 3 November 2026. The obsolete process-industry route returned migration HTML; eventual retrieval is in [reviews](../reviews/README.md). Complete source bytes remain outside the public repository.

| Exported section | Source bytes / range | Occurrences |
|---|---|---:|
| Nees–Liebman general bibliography | 52-page accepted manuscript; SHA256 `5585a4d7d64d84edaef80ab322863a273152e85eac572da4bbeec245540e2fbf`; PDF pp. 33–42 | 85 |
| McFarlane et al. 2020 bibliography | 18-page publisher PDF; SHA256 `5cc81d1275bafc8da1e3e3ac7e5b4f08801a19c7759667cd32368615a33e77b4`; PDF pp. 14–18 | 91 |

The 52-page Nees–Liebman file is distinct from the older 47-page preprint. Headers and bibliography ranges were inspected, with rendered reference pages checked. Sleep-review PDF p.18 states CC BY4.0. No empirical methods/results reading or numerical extraction is claimed. FRA reacquisition matches its October PDF hash and does not duplicate its bibliography run.

REFERENCE-LISTS.json preserves ordered citation text and file-page locators, including background sources and original spelling. Entries are not verified canonical identities or included studies. The extractor verifies source hashes and reproduces the exports:

```sh
python3 research/searches/auditory/recovery-2026-11-03/references/build_reference_exports.py /path/to/private-source-directory --check
```

Inputs must contain `nees-liebman-am.pdf` and `sleep-review.pdf`. The private directory is not guaranteed on another machine.

NAVIGATION.json records the repeat known-item search with measured start/end times and all 26 results. The tool returns a combined batch, so results cannot be attributed separately to its two queries. Earlier exploratory titles/URLs in `web-navigation.json` have date-only observations; they are diagnostic route history, not counted again as a production search. Copyrighted snippets and temporary signed download parameters are omitted. Stable requested URLs permit lawful re-retrieval.
