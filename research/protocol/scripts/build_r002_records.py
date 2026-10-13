"""Write the MHAC-R002 live records deterministically.

Run from the repository root:

    python3 research/protocol/scripts/build_r002_records.py

The facts below were recorded by the executing agent during the R002 pilot on
2026-10-13. This script only serializes them; it does not fetch anything and
adds no evidence. Re-running it reproduces identical bytes. Later revisions
must append to the written records rather than editing this script's history.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.record_io import dumps  # noqa: E402

AT = "2026-10-13T01:33:00Z"
ACTOR = {"kind": "agent", "id": "claude-r002-session",
         "tool": "Claude in a claude.ai cloud session (WebSearch, WebFetch, shell)",
         "model": "claude-opus-5-5"}
EXPORT = "research/searches/pilot/exports/PILOT-WEBSEARCH-2026-10-13.json"
LEDGER = "research/searches/pilot/exports/ACCESS-LEDGER-2026-10-13.csv"
METHODS_WINDOW_END = "2026-10-13T01:14:08Z"
NEES_WINDOW_END = "2026-10-13T01:06:04Z"
COMPARATOR_WINDOW_END = "2026-10-13T01:17:51Z"


FREEZE_AT = "2026-10-13T01:40:06Z"
AUDIT_AT = "2026-10-13T01:40:47Z"
AT2 = AUDIT_AT
FROZEN = ["research/protocol/PROTOCOL-v1.md", "research/protocol/ANALYSIS_PLAN-v1.md",
          "research/protocol/GLOSSARY-v1.md"]
SUPPORTING = ["research/protocol/FREEZE.md", "research/protocol/PILOT_REPORT.md",
              "research/protocol/CONCEPT_REGISTER.md", "research/protocol/REPORTING_APPLICABILITY.md",
              "research/protocol/gates/HG-R002-DATABASE-ACCESS.md"]


def record2(rid: str, kind: str, data: dict, *, basis=(), factual) -> dict:
    row = record(rid, kind, data, basis=basis, factual=factual)
    row["revisions"][0]["at"] = AT2
    return row


def missing(state: str, reason: str) -> dict:
    return {"state": state, "reason": reason}


def known(value) -> dict:
    return {"state": "known", "value": value}


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def record(rid: str, kind: str, data: dict, *, basis=(), factual="source_reported") -> dict:
    return {"schema_version": 1, "id": rid, "kind": kind, "synthetic": False, "issue": 2,
            "revisions": [{"rev": 1, "at": AT, "actor": ACTOR, "basis": list(basis),
                           "data": data, "factual_status": factual}]}


def source(*, title, authors, date, identifiers, source_type, language="en",
           edition, metadata_status, metadata_evidence, access_status, access_at,
           access_reason, rights, family_links=()) -> dict:
    return {
        "title": title,
        "authors": [{"name": name, "role": role} for name, role in authors],
        "publication_date": date,
        "identifiers": [{"scheme": s, "value": v, "status": st, "provenance": p}
                        for s, v, st, p in identifiers],
        "source_type": source_type,
        "language": known(language),
        "edition": edition,
        "metadata_status": metadata_status,
        "metadata_evidence": list(metadata_evidence),
        "access_status": access_status,
        "access_at": access_at,
        "access_reason": access_reason,
        "rights": rights,
        "validity": "active",
        "family_links": list(family_links),
        "manifestations": [],
    }


RIGHTS_UNKNOWN = {"status": "unknown", "reason": "No licence or permission was verified; no bytes are retained.",
                  "evidence": missing("unknown", "Licence not checked in R002")}
NO_BYTES = ("No source bytes were retained: the workspace cannot download from this host and "
            "WebFetch returns an intermediary model's paraphrase only.")

METHOD_SOURCES = {
    "SRC-METH-PRISMA2020": source(
        title="The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
        authors=[("Page, M. J.", "author")], date=known("2021-03-29"),
        identifiers=[("doi", "10.1186/s13643-021-01626-4", "candidate",
                      "Recorded by the R002 1B prepass reading-coverage ledger (2026-10-04); not re-resolved in this session")],
        source_type="article", edition=known("Systematic Reviews 10:89 version"),
        metadata_status="candidate",
        metadata_evidence=["Journal, volume, article number, date and DOI recorded by the archived 1B prepass; title and first author transcribed by the executing agent and not re-verified; full author list not transcribed."],
        access_status="full_text_available", access_at=AT,
        access_reason="Publisher HTML was readable in the 1B prepass (selected ranges with page images). Not re-accessed in R002 freeze work. The 1B access date (2026-10-04) has no recorded time, so access_at is this record's creation time rather than an invented clock time.",
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-PRISMAS": source(
        title="PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews",
        authors=[("Rethlefsen, M. L.", "author")], date=known("2021-01-26"),
        identifiers=[("doi", "10.1186/s13643-020-01542-z", "candidate",
                      "Recorded by the archived R002 1B prepass (2026-10-04); not re-resolved in this session")],
        source_type="article", edition=known("Systematic Reviews 10:39 version"),
        metadata_status="candidate",
        metadata_evidence=["Journal, article number, date and DOI recorded by the archived 1B prepass; title and first author transcribed by the executing agent and not re-verified."],
        access_status="full_text_available", access_at=AT,
        access_reason="Publisher HTML was readable in the 1B prepass (all 16 items read). Not re-accessed in R002 freeze work. The 1B access date (2026-10-04) has no recorded time, so access_at is this record's creation time rather than an invented clock time.",
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-CIS2006": source(
        title="Conducting a critical interpretive synthesis of the literature on access to healthcare by vulnerable groups",
        authors=[("Dixon-Woods, M.", "author")], date=known("2006-07-26"),
        identifiers=[("doi", "10.1186/1471-2288-6-35", "candidate",
                      "Recorded by the archived R002 1B prepass (2026-10-04); not re-resolved in this session")],
        source_type="article", edition=known("BMC Medical Research Methodology 6:35 version"),
        metadata_status="candidate",
        metadata_evidence=["Journal, article number, date and DOI recorded by the archived 1B prepass; title and first author transcribed by the executing agent and not re-verified."],
        access_status="full_text_available", access_at=AT,
        access_reason="Publisher HTML was readable in the 1B prepass (methodological sections read). Not re-accessed in R002 freeze work. The 1B access date (2026-10-04) has no recorded time, so access_at is this record's creation time rather than an invented clock time.",
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-PRISMAP2015": source(
        title="Preferred reporting items for systematic review and meta-analysis protocols (PRISMA-P) 2015 statement",
        authors=[("Moher, D.", "author"), ("Shamseer, L.", "author"), ("Clarke, M.", "author"),
                 ("Ghersi, D.", "author"), ("Liberati, A.", "author"), ("Petticrew, M.", "author"),
                 ("Shekelle, P.", "author"), ("Stewart, L. A.", "author"), ("PRISMA-P Group", "corporate_author")],
        date=known("2015-01-01"),
        identifiers=[("doi", "10.1186/2046-4053-4-1", "verified", "Printed on the publisher PDF read via WebFetch on 2026-10-13"),
                     ("url", "https://systematicreviewsjournal.biomedcentral.com/track/pdf/10.1186/2046-4053-4-1", "verified", "Fetched successfully on 2026-10-13 (ledger row 16)")],
        source_type="article", edition=known("Systematic Reviews 4:1"),
        metadata_status="verified",
        metadata_evidence=["Authors, journal, article number, date and DOI reported from the publisher PDF by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=METHODS_WINDOW_END,
        access_reason="Publisher PDF read through WebFetch (tool-mediated) within batch M window. " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-SWIM2020": source(
        title="Synthesis without meta-analysis (SWiM) in systematic reviews: reporting guideline",
        authors=[("Campbell, M.", "author"), ("McKenzie, J. E.", "author"), ("Sowden, A.", "author"),
                 ("Katikireddi, S. V.", "author"), ("Brennan, S. E.", "author"), ("Ellis, S.", "author"),
                 ("Hartmann-Boyce, J.", "author"), ("Ryan, R.", "author"), ("Shepperd, S.", "author"),
                 ("Thomas, J.", "author"), ("Welch, V.", "author"), ("Thomson, H.", "author")],
        date=known("2020"),
        identifiers=[("doi", "10.1136/bmj.l6890", "verified", "Printed on the repository copy read via WebFetch on 2026-10-13"),
                     ("url", "https://discovery-pp.ucl.ac.uk/10092670/1/bmj.l6890.full.pdf", "verified", "Fetched successfully on 2026-10-13 (ledger row 13)")],
        source_type="article", edition=known("BMJ 2020;368:l6890; UCL repository copy"),
        metadata_status="verified",
        metadata_evidence=["Citation reported from the repository copy of the BMJ article by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=METHODS_WINDOW_END,
        access_reason="Repository PDF read through WebFetch (tool-mediated). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-EGM2020": source(
        title="Guidance for producing a Campbell evidence and gap map",
        authors=[("White, H.", "author"), ("Albers, B.", "author"), ("Gaarder, M.", "author")],
        date=known("2020"),
        identifiers=[("doi", "10.1002/cl2.1125", "verified", "Printed in the LSHTM repository copy read via WebFetch on 2026-10-13"),
                     ("url", "https://lshtm-eprints-repo-prod.lshtm-eprints.cdl.cosector.com/4674958/1/White-etal-2020-Guidance-for-producing-a-Campbell-evidence-and-gap-map.pdf", "verified", "Fetched successfully on 2026-10-13 (ledger row 15)")],
        source_type="article", edition=known("Campbell Systematic Reviews 16:e1125; repository copy"),
        metadata_status="verified",
        metadata_evidence=["Citation reported from the repository copy by the fetch tool on 2026-10-13; only the first three authors were transcribed (et al. in source citation)."],
        access_status="full_text_available", access_at=METHODS_WINDOW_END,
        access_reason="Repository PDF read through WebFetch (first 100000 of 115410 characters). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-AI2025": source(
        title="Position statement on artificial intelligence (AI) use in evidence synthesis across Cochrane, the Campbell Collaboration, JBI, and the Collaboration for Environmental Evidence 2025",
        authors=[("Flemyng, E.", "author"), ("Noel-Storr, A.", "author"), ("Macura, B.", "author"),
                 ("Gartlehner, G.", "author"), ("Thomas, J.", "author"), ("Meerpohl, J. J.", "author"),
                 ("Jordan, Z.", "author"), ("Minx, J.", "author"), ("Eisele-Metzger, A.", "author"),
                 ("Hamel, C.", "author"), ("Jemioło, P.", "author"), ("Porritt, K.", "author"),
                 ("Grainger, M.", "author")],
        date=known("2025-11-06"),
        identifiers=[("doi", "10.11124/JBIES-25-00480", "verified", "Shown on the PMC record read via WebFetch on 2026-10-13"),
                     ("url", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12594113", "verified", "Fetched successfully on 2026-10-13 (ledger row 12)")],
        source_type="article", edition=known("JBI Evidence Synthesis 23(11):2162-2166 (PMC12594113); co-published in other journals"),
        metadata_status="verified",
        metadata_evidence=["Title, authors, journal, issue, pages, date, DOI and co-publication note reported from the PMC record by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=METHODS_WINDOW_END,
        access_reason="PMC HTML read through WebFetch (tool-mediated). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-PRESS2015": source(
        title="PRESS - Peer Review of Electronic Search Strategies: 2015 Guideline Explanation and Elaboration (PRESS E&E)",
        authors=[("McGowan, J.", "author"), ("Sampson, M.", "author"), ("Salzwedel, D. M.", "author"),
                 ("Cogo, E.", "author"), ("Foerster, V.", "author"), ("Lefebvre, C.", "author"),
                 ("CADTH", "corporate_author")],
        date=known("2016-01"),
        identifiers=[("url", "https://www.cda-amc.ca/sites/default/files/pdf/CP0015_PRESS_Update_Report_2016.pdf", "verified", "Fetched successfully on 2026-10-13 (ledger row 17)")],
        source_type="report", edition=known("CADTH, Ottawa, January 2016"),
        metadata_status="verified",
        metadata_evidence=["Authors, publisher and date reported from the report's cover and citation note by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=METHODS_WINDOW_END,
        access_reason="Report PDF read through WebFetch (first 100000 of 110113 characters). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-METH-COCHRANE-CH11": source(
        title="Chapter 11: Undertaking network meta-analyses",
        authors=[("Chaimani, A.", "author"), ("Caldwell, D. M.", "author"), ("Li, T.", "author"),
                 ("Higgins, J. P. T.", "author"), ("Salanti, G.", "author")],
        date=known("2019-10"),
        identifiers=[("url", "https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-11", "verified", "Fetched successfully on 2026-10-13 (ledger row 18)")],
        source_type="chapter", edition=known("Cochrane Handbook for Systematic Reviews of Interventions version 6.5 (2024); chapter last updated October 2019"),
        metadata_status="verified",
        metadata_evidence=["Authors, chapter update date and handbook version reported from the chapter's citation section by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=METHODS_WINDOW_END,
        access_reason="Chapter HTML read through WebFetch (first 100000 of 115788 characters). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
}

NEES_VOR = "SRC-NOV-NEES-LIEBMAN-2023"
COMPARATORS = {
    NEES_VOR: source(
        title="Auditory Icons, Earcons, Spearcons, and Speech: A Systematic Review and Meta-Analysis of Brief Audio Alerts in Human-Machine Interfaces",
        authors=[("Nees, M. A.", "author"), ("Liebman, E.", "author")], date=known("2023"),
        identifiers=[("doi", "10.1080/25742442.2023.2219201", "verified", "Lafayette institutional record fetched 2026-10-13 (ledger row 1); also recorded in the archived 1C1 packet"),
                     ("url", "https://ldr.lafayette.edu/concern/publications/gx41mk40g", "verified", "Institutional deposit record fetched 2026-10-13")],
        source_type="review", edition=known("Auditory Perception & Cognition 6(3-4):300-329 (Version of Record)"),
        metadata_status="verified",
        metadata_evidence=["Lafayette institutional record (2026-10-13) gives title, creators, journal, volume, issue, pages, year and DOI.",
                           "Archived R002 1C1 packet verified the same identity from the institutional and author bibliographies on 2026-10-04."],
        access_status="metadata_only", access_at="2026-10-13T01:06:04Z",
        access_reason="Publisher abstract page returned a client error; institutional PDF was refused by robots exclusion (WebFetch) and by the session proxy (shell). See ledger rows 1-5.",
        rights={"status": "quotation_limited", "reason": "Institutional record states In Copyright with Taylor & Francis as rights holder.",
                "evidence": known("Lafayette record rights statement rightsstatements.org InC/1.0, read 2026-10-13")}),
    "SRC-NOV-NEES-LIEBMAN-2023-PREPRINT": source(
        title="Auditory icons, earcons, spearcons, and speech: A systematic review and meta-analysis of brief audio alerts in human-machine interfaces",
        authors=[("Nees, Michael A.", "author"), ("Liebman, Eliana", "author")], date=known("2022"),
        identifiers=[("doi", "10.31234/osf.io/g68f5", "candidate", "Printed in the preprint text as reported by WebFetch; DOI landing page could not be opened (ledger row 8)"),
                     ("url", "https://www.academia.edu/94454696/Auditory_icons_earcons_spearcons_and_speech_A_systematic_review_and_meta_analysis_of_brief_audio_alerts_in_human_machine_interfaces", "verified", "Author-hosted copy fetched 2026-10-13 (ledger row 6)")],
        source_type="preprint", edition=known("PsyArXiv preprint labelled 'Preprint version 9.8.22' (day/month order ambiguous); 47 pages; not peer reviewed"),
        metadata_status="verified",
        metadata_evidence=["Version label, authors, affiliation, page count and preprint DOI reported from the hosted PDF text by the fetch tool on 2026-10-13.",
                           "Year 2022 inferred from the version label 9.8.22; the exact day is ambiguous."],
        access_status="full_text_available", access_at=NEES_WINDOW_END,
        access_reason="Preprint text available through an author-hosted copy; read only through WebFetch paraphrase (first 100000 of 102096 characters). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN,
        family_links=[{"relation": "version_of", "source_ref": {"id": NEES_VOR, "rev": 1},
                       "reason": "Author preprint submitted as the journal article; correspondence with the Version of Record is unverified."}]),
    "SRC-NOV-FRA-IVAA-2022": source(
        title="In-Vehicle Auditory Alerts Literature Review",
        authors=[("Jeon, M.", "author"), ("Lautala, P.", "author"), ("Nadri, C.", "author"), ("Nelson, D. N.", "author"),
                 ("Federal Railroad Administration, U.S. Department of Transportation", "corporate_author")],
        date=known("2022-02-01"),
        identifiers=[("other", "DOT/FRA/ORD-22/05", "verified", "Report number shown on the ROSA P record fetched 2026-10-13"),
                     ("url", "https://rosap.ntl.bts.gov/view/dot/60401", "verified", "ROSA P landing page fetched 2026-10-13 (ledger row 23)")],
        source_type="report", edition=known("Final report, DOT/FRA/ORD-22/05"),
        metadata_status="verified",
        metadata_evidence=["Title, authors, issuing agency, report number and date reported from the ROSA P record by the fetch tool on 2026-10-13."],
        access_status="abstract_only", access_at=COMPARATOR_WINDOW_END,
        access_reason="Landing-page summary read; the linked report PDF was not fetched.",
        rights=RIGHTS_UNKNOWN),
    "SRC-NOV-NAM-2010": source(
        title="A semiotic analysis of sounds in personal computers: Toward a semiotic model of human-computer interaction",
        authors=[("Nam, Yoonjae", "author")], date=known("2010"),
        identifiers=[("url", "https://www.degruyterbrill.com/document/doi/10.1515/semi.2010.060/pdf", "verified", "Publisher page fetched 2026-10-13 (ledger row 21)"),
                     ("doi", "10.1515/semi.2010.060", "candidate", "Inferred from the publisher URL path only; not shown on the page and not resolved")],
        source_type="article", edition=missing("unknown", "Journal name, volume and pages not visible on the fetched page"),
        metadata_status="candidate",
        metadata_evidence=["Author, title and copyright year (2010, Walter de Gruyter) reported by the fetch tool; journal identity unverified."],
        access_status="abstract_only", access_at=COMPARATOR_WINDOW_END,
        access_reason="Only the abstract and an issue listing were visible.",
        rights=RIGHTS_UNKNOWN),
    "SRC-NOV-VRIEND-2025": source(
        title="Two Empirical Studies on Audiovisual Semiotics of Uncertainty",
        authors=[("Vriend, Sita A.", "author"), ("Hägele, David", "author"), ("Weiskopf, Daniel", "author")],
        date=known("2025"),
        identifiers=[("url", "https://arxiv.org/html/2505.14379v1", "verified", "arXiv HTML fetched 2026-10-13 (ledger row 19)"),
                     ("other", "arXiv:2505.14379v1", "candidate", "Taken from the URL; the arXiv identifier was not stated in the text the tool returned")],
        source_type="preprint", edition=known("arXiv v1 HTML carrying an ACM Audio Mostly 2025 (Coimbra) header"),
        metadata_status="verified",
        metadata_evidence=["Authors, affiliations, date header and venue header reported from the arXiv HTML by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=COMPARATOR_WINDOW_END,
        access_reason="arXiv HTML read through WebFetch (first 100000 of 105254 characters). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-NOV-DESOUZA-2005": source(
        title="The Semiotic Engineering of Human-Computer Interaction",
        authors=[("de Souza, Clarisse Sieckenius", "author")], date=known("2005"),
        identifiers=[("isbn", "9780262042208", "candidate", "From the MIT Press URL recorded in docs/SEED_SOURCES.md; not re-checked"),
                     ("isbn", "9780262527095", "candidate", "From retailer pages returned by pilot runs P-R1 and P-R5; edition relation unverified")],
        source_type="book", edition=missing("unknown", "First edition date, binding variants and printings not verified"),
        metadata_status="candidate",
        metadata_evidence=["Title and author appear on several retailer and catalogue results of pilot run P-R1; year from the project seed list."],
        access_status="metadata_only", access_at=COMPARATOR_WINDOW_END,
        access_reason="Only retailer and catalogue listings were seen; no chapter was read.",
        rights=RIGHTS_UNKNOWN),
    "SRC-NOV-VALENTE-2009": source(
        title="Turn off the graphics: designing non-visual interfaces for mobile phone games",
        authors=[("Valente, L.", "author"), ("de Souza, C. S.", "author"), ("Feijó, B.", "author")],
        date=known("2009"),
        identifiers=[("doi", "10.1007/BF03192576", "verified", "Shown on the open-access publisher page fetched 2026-10-13 (ledger row 27)")],
        source_type="article", edition=known("Journal of the Brazilian Computer Society 15:45-58"),
        metadata_status="verified",
        metadata_evidence=["Authors, title, journal, volume, pages, year and DOI reported from the publisher page by the fetch tool on 2026-10-13."],
        access_status="abstract_only", access_at=COMPARATOR_WINDOW_END,
        access_reason="The fetched page returned the abstract and article metadata only.",
        rights={"status": "redistribution_permitted", "reason": "Publisher page states a Creative Commons Attribution 2.0 licence.",
                "evidence": known("Licence statement on the SpringerOpen article page, read through WebFetch on 2026-10-13")}),
    "SRC-NOV-BRIER-2010": source(
        title="Cybersemiotics: An Evolutionary World View Going Beyond Entropy and Information into the Question of Meaning",
        authors=[("Brier, Søren", "author")], date=known("2010-08-09"),
        identifiers=[("doi", "10.3390/e12081902", "verified", "Shown on the MDPI HTML fetched 2026-10-13 (ledger row 28)"),
                     ("url", "https://www.mdpi.com/1099-4300/12/8/1902/htm", "verified", "Fetched successfully on 2026-10-13")],
        source_type="article", edition=known("Entropy 12(8):1902-1920"),
        metadata_status="verified",
        metadata_evidence=["Author, title, journal, volume, issue, pages, dates, DOI and licence reported from the MDPI HTML by the fetch tool on 2026-10-13."],
        access_status="full_text_available", access_at=COMPARATOR_WINDOW_END,
        access_reason="MDPI HTML read through WebFetch (first 100000 of 110193 characters). " + NO_BYTES,
        rights={"status": "redistribution_permitted", "reason": "Article page states a Creative Commons Attribution 3.0 licence.",
                "evidence": known("Licence statement on the MDPI article page, read through WebFetch on 2026-10-13")}),
    "SRC-NOV-BRIER-2015": source(
        title="Cybersemiotics: A Semiotic-systemic Transdisciplinary Approach",
        authors=[("Brier, Søren", "author")], date=known("2015"),
        identifiers=[("url", "https://research-api.cbs.dk/ws/portalfiles/portal/45591012/s_ren_brier_cybersemiotics_a_semiotic_systemic_publishersversion.pdf", "verified", "Fetched successfully on 2026-10-13 (ledger row 22)")],
        source_type="article", edition=known("Studia kulturoznawcze 1(7):247-265; publisher's version deposited at CBS"),
        metadata_status="verified",
        metadata_evidence=["Title, author, journal, volume, issue, pages and version label reported from the deposited PDF by the fetch tool on 2026-10-13; no DOI given."],
        access_status="full_text_available", access_at=COMPARATOR_WINDOW_END,
        access_reason="Deposited publisher PDF read through WebFetch (tool-mediated). " + NO_BYTES,
        rights=RIGHTS_UNKNOWN),
    "SRC-NOV-THOMSEN-BRIER-2014": source(
        title="Total Integrative Evolutionary Communication: Towards a Cybersemiotic Discourse Pragmatics",
        authors=[("Thomsen, Ole Nedergaard", "author"), ("Brier, Søren", "author")], date=known("2014-10-21"),
        identifiers=[("doi", "10.37693/pjos.2014.6.11467", "verified", "Shown on the journal page fetched 2026-10-13 (ledger row 25)"),
                     ("url", "https://journals.lub.lu.se/pjos/article/view/11467", "verified", "Fetched successfully on 2026-10-13")],
        source_type="article", edition=known("Public Journal of Semiotics 6(1):22-57"),
        metadata_status="verified",
        metadata_evidence=["Authors, title, journal, volume, issue, pages, date and DOI reported from the journal page by the fetch tool on 2026-10-13."],
        access_status="abstract_only", access_at=COMPARATOR_WINDOW_END,
        access_reason="Only the abstract and metadata were read.",
        rights=RIGHTS_UNKNOWN),
    "SRC-NOV-COBLEY-2010": source(
        title="Cybersemiotics and Human Modelling",
        authors=[("Cobley, Paul", "author")], date=known("2010-09"),
        identifiers=[("doi", "10.3390/e12092045", "verified", "Shown on the DOAJ record fetched 2026-10-13 (ledger row 24)")],
        source_type="article", edition=known("Entropy 12(9):2045-2066"),
        metadata_status="verified",
        metadata_evidence=["Author, title, journal, volume, issue, pages, year and DOI reported from the DOAJ record by the fetch tool on 2026-10-13."],
        access_status="abstract_only", access_at=COMPARATOR_WINDOW_END,
        access_reason="DOAJ record and abstract only.",
        rights=RIGHTS_UNKNOWN),
}


def search_runs() -> dict[str, dict]:
    export = json.loads((ROOT / EXPORT).read_text(encoding="utf-8"))
    digest = sha256(EXPORT)
    lanes = {"N": "comparator_access", "M": "methods"}
    runs = {}
    for batch in export["batches"]:
        for run in batch["runs"]:
            label = run["label"]
            rid = "SRCH-R002-" + label.replace("-", "")
            mode = run["mode"]
            runs[rid] = {
                "lane": run.get("lane", lanes.get(batch["batch"], "unassigned")),
                "protocol_version": "pilot-pre-v1",
                "mode": "pilot",
                "status": "partial",
                "platform": "General web search engine via the agent's WebSearch tool",
                "interface": f"WebSearch tool, {mode} mode, US-only results",
                "query": run["query"],
                "filters": ["No user-set filters; tool default US-only results"],
                "coverage": {"start": missing("unknown", "The engine does not state its index coverage"),
                             "end": missing("unknown", "The engine does not state its index coverage")},
                "started_at": known(batch["window_start"]),
                "finished_at": known(batch["window_end"]),
                "reported_count": missing("not_reported", "The engine reports no total hit count"),
                "retrieved_count": len(run["results"]),
                "export": known({"path": EXPORT, "sha256": digest}),
                "pagination": {"complete": False,
                               "detail": "One page of top results only; the tool exposes no further pages."},
                "failures": [],
                "boundary": (f"Pilot run {label} in batch {batch['batch']} ({batch['purpose']}). "
                             "Times are batch-window bounds from the shell clock. Discovery only: titles and URLs, "
                             "no abstracts, not a bibliographic database search and not usable to claim coverage."),
            }
    return runs


OPENED = "The agent fetched this URL in R002 and identified the publication from its content (access ledger)."
ID_IN_URL = "The URL carries this publication's persistent identifier; the page itself was not opened."
RESOLUTIONS = {
    ("N1", 3): (NEES_VOR, OPENED), ("N2", 1): (NEES_VOR, OPENED), ("P-A6", 2): (NEES_VOR, OPENED),
    ("P-A7", 5): (NEES_VOR, OPENED), ("N3", 1): (NEES_VOR, ID_IN_URL),
    ("N3", 3): ("SRC-NOV-NEES-LIEBMAN-2023-PREPRINT", OPENED),
    ("M1", 3): ("SRC-METH-PRISMAP2015", OPENED),
    ("M2", 10): ("SRC-METH-SWIM2020", OPENED),
    ("M3", 1): ("SRC-METH-AI2025", "Same PMC identifier (PMC12594113) as the record the agent fetched after redirect."),
    ("M3", 5): ("SRC-METH-AI2025", OPENED),
    ("M4", 3): ("SRC-METH-EGM2020", ID_IN_URL), ("M4", 5): ("SRC-METH-EGM2020", ID_IN_URL),
    ("M4", 6): ("SRC-METH-EGM2020", OPENED),
    ("M5", 1): ("SRC-METH-PRESS2015", OPENED),
    ("M6", 3): ("SRC-METH-COCHRANE-CH11", OPENED),
    ("P-B1", 8): ("SRC-NOV-BRIER-2015", OPENED),
    ("P-B2", 6): ("SRC-NOV-COBLEY-2010", OPENED),
    ("P-B4", 3): ("SRC-NOV-NAM-2010", OPENED), ("P-R2", 5): ("SRC-NOV-NAM-2010", OPENED),
    ("P-A4", 3): ("SRC-NOV-VRIEND-2025", "Same arXiv identifier (2505.14379v1) as the HTML version the agent fetched."),
    ("P-A4", 7): ("SRC-NOV-VRIEND-2025", OPENED),
    ("P-A6", 7): ("SRC-NOV-FRA-IVAA-2022", OPENED),
    ("P-R6", 3): ("SRC-NOV-VALENTE-2009", OPENED), ("P-R6", 4): ("SRC-NOV-VALENTE-2009", ID_IN_URL),
    ("P-B5", 1): ("SRC-NOV-BRIER-2010", "EPUB file of the same Entropy article (entropy-12-01902) the agent fetched as HTML."),
    ("P-B5", 2): ("SRC-NOV-BRIER-2010", OPENED),
    ("P-B5", 3): ("SRC-NOV-BRIER-2010", "Article landing page for the same Entropy article the agent fetched as HTML."),
    ("P-B5", 5): ("SRC-NOV-THOMSEN-BRIER-2014", OPENED),
    **{("P-R1", n): ("SRC-NOV-DESOUZA-2005", "Retailer or bookshop page whose URL carries ISBN 9780262527095, recorded as a candidate identifier of this book; the page was not opened.")
       for n in (1, 3, 4, 5, 7, 9)},
}


def search_hits(runs: dict[str, dict]) -> dict[str, dict]:
    export = json.loads((ROOT / EXPORT).read_text(encoding="utf-8"))
    hits = {}
    used = set()
    for batch in export["batches"]:
        for run in batch["runs"]:
            label = run["label"]
            run_id = "SRCH-R002-" + label.replace("-", "")
            assert run_id in runs
            for result in run["results"]:
                ordinal = result["ordinal"]
                hid = f"HIT-R002-{label.replace('-', '')}-{ordinal:02d}"
                data = {
                    "search_ref": {"id": run_id, "rev": 1},
                    "ordinal": ordinal,
                    "raw_metadata": f"{result['title']} | {result['url']}",
                    "returned_identifiers": [{"scheme": "url", "value": result["url"]}],
                }
                key = (label, ordinal)
                basis = [{"id": run_id, "rev": 1}]
                if key in RESOLUTIONS:
                    source_id, reason = RESOLUTIONS[key]
                    used.add(key)
                    data.update(status="resolved", resolution_reason=reason,
                                source_ref={"id": source_id, "rev": 1})
                    basis.append({"id": source_id, "rev": 1})
                else:
                    data.update(status="unresolved",
                                resolution_reason="Pilot occurrence; publication identity not checked. Title and URL only.")
                hits[hid] = (data, basis)
    assert used == set(RESOLUTIONS), sorted(set(RESOLUTIONS) - used)
    return hits


def human_gate() -> dict:
    return {
        "need": "Executable, exportable bibliographic database searches for Track E (protocol v1 channels C1-C4, C6-C7), starting with OpenAlex and Crossref.",
        "reason": "The agent workspace proxy refuses api.openalex.org, api.crossref.org, export.arxiv.org and api.semanticscholar.org, and the owner's desktop built-in browser blocks api.openalex.org under its site permissions. Without a database channel, MHAC-R005 must use the declared web-search fallback and cannot claim database coverage.",
        "attempted_remedies": [
            "Shell requests to four open bibliographic APIs on 2026-10-13 (proxy CONNECT 403).",
            "Owner's built-in browser preview of an OpenAlex API URL on 2026-10-13 (blocked by site permissions; no workaround attempted).",
            "Pilot through the WebSearch tool, which returned about 7% of a known-item set (pilot report section 4).",
        ],
        "owner_action": "Either allow api.openalex.org and api.crossref.org for the Claude desktop built-in browser (or the session network), or supply database exports for the protocol queries. Steps and links: research/protocol/gates/HG-R002-DATABASE-ACCESS.md.",
        "evidence": missing("unknown", "No owner action has occurred"),
        "completion_signal": "An OpenAlex API URL opens in the browser pane or the workspace, or exported result files appear in a connected folder or the conversation.",
        "stop_condition": "If no action is taken before MHAC-R005 starts, R005 executes the protocol section 5.3 fallback and records the database channels as access gaps. No account creation, purchase or paywall bypass is attempted.",
        "status": "waiting",
        "gate_class": "source_access",
        "authorized_actor": missing("unknown", "No authorization has been given"),
    }


def assistance(task, inputs, outputs, artifacts, steps, limitations, performed_at) -> dict:
    return {"subtype": "assistance", "task": task, "input_refs": inputs, "output_refs": outputs,
            "artifacts": artifacts, "verification_steps": steps, "limitations": limitations,
            "status": "performed", "performed_at": known(performed_at),
            "independence": "Single executing agent. Not a human check and not independent of the work it describes."}


def pins(ids) -> list[dict]:
    return [{"id": rid, "rev": 1} for rid in sorted(ids)]


def main() -> int:
    out = {}
    for rid, data in METHOD_SOURCES.items():
        out[f"research/protocol/records/{rid}.json"] = record(rid, "source", data)
    for rid, data in COMPARATORS.items():
        basis = [link["source_ref"] for link in data["family_links"]]
        out[f"research/novelty/records/{rid}.json"] = record(rid, "source", data, basis=basis)
    runs = search_runs()
    for rid, data in runs.items():
        out[f"research/searches/pilot/records/{rid}.json"] = record(rid, "search_run", data, factual="discovery")
    for hid, (data, basis) in search_hits(runs).items():
        out[f"research/searches/pilot/records/hits/{hid}.json"] = record(
            hid, "search_hit", data, basis=basis, factual="discovery")
    out["research/protocol/records/HG-R002-DATABASE-ACCESS.json"] = record(
        "HG-R002-DATABASE-ACCESS", "human_gate", human_gate(), factual="project_decision")
    pilot_inputs = []
    out["research/protocol/records/AID-R002-PILOT-SEARCH.json"] = record(
        "AID-R002-PILOT-SEARCH", "assistance", assistance(
            "Run and transcribe 31 labelled pilot and discovery web searches; log every access attempt.",
            pilot_inputs, pins(runs), [EXPORT, LEDGER],
            ["Each returned title and URL was transcribed from the tool output in the same session and checked again against it before commit.",
             "Batch windows were taken from shell clock readings and proxy failure records."],
            "Web search returns about ten results without counts or abstracts; transcription was by the same agent that ran the searches.",
            "2026-10-13T01:17:51Z"), factual="discovery")
    comparator_ids = sorted(COMPARATORS)
    out["research/protocol/records/AID-R002-READ-COMPARATORS.json"] = record(
        "AID-R002-READ-COMPARATORS", "assistance", assistance(
            "Tool-mediated reading of the Nees-Liebman preprint and overlap comparators for the novelty audit.",
            pins(comparator_ids), [], ["research/novelty/COMPARATOR_NEES_LIEBMAN_2023.md", "research/novelty/OVERLAP_MATRIX.md", "research/novelty/OVERLAP_MATRIX.csv"],
            ["Seven targeted WebFetch questions covered the preprint's methods, counts, coding, analysis, results, discussion, introduction and included-study list.",
             "Facts that the tool reported as absent are recorded as 'not found in tool-mediated reading', not as absence from the source."],
            "WebFetch returns an unidentified intermediary model's paraphrase with no bytes, page images, figures or appendices; page numbers are approximate; the Version of Record was not read; several comparators were abstract-only.",
            COMPARATOR_WINDOW_END), basis=pins(comparator_ids), factual="researcher_interpretation")
    method_ids = ["SRC-METH-AI2025", "SRC-METH-COCHRANE-CH11", "SRC-METH-EGM2020", "SRC-METH-PRESS2015",
                  "SRC-METH-PRISMAP2015", "SRC-METH-SWIM2020"]
    out["research/protocol/records/AID-R002-READ-METHODS.json"] = record(
        "AID-R002-READ-METHODS", "assistance", assistance(
            "Tool-mediated reading of the methodological guidance deferred by the 1B prepass (PRISMA-P, SWiM, EGM guidance, 2025 AI position statement, PRESS 2015, Cochrane Handbook chapter 11).",
            pins(method_ids), [], ["research/protocol/REPORTING_APPLICABILITY.md", "research/protocol/ANALYSIS_PLAN-v1.md"],
            ["Each item list or requirement was requested with section, table or page locators and mapped to a protocol location."],
            "Paraphrase through the fetch tool; the PRESS checklist form, RAISE documents and later portions of three long documents were not read.",
            METHODS_WINDOW_END), basis=pins(method_ids), factual="researcher_interpretation")
    source_pins = pins(list(METHOD_SOURCES) + list(COMPARATORS))
    evidence = sorted(source_pins + pins(runs), key=lambda ref: ref["id"])
    frozen = [{"path": path, "sha256": sha256(path)} for path in FROZEN]
    draft = assistance(
        "Draft and freeze protocol v1, analysis plan and glossary, with pilot report, concept register, reporting applicability record and database-access gate.",
        source_pins, [], [item["path"] for item in frozen] + SUPPORTING,
        ["Pilot-driven revisions were applied before the digests were taken (pilot report section 8).",
         "Frozen-file digests recomputed after the last edit and bound in FREEZE.md and the protocol stage declaration."],
        "Single-agent drafting; no human review of content; method sources read in prepasses were not re-read.",
        FREEZE_AT)
    review = {
        "subtype": "review", "scope": "internal_audit", "outcome": "pass", "verification": "agent_checked",
        "target_refs": evidence, "input_refs": [{"id": "AID-R002-PROTOCOL-DRAFT", "rev": 1}],
        "artifact": "research/protocol/INTERNAL_AUDIT-R002.md",
        "status": "performed", "performed_at": known(AUDIT_AT),
        "independence": "Self-audit by the same agent that produced the audited work. Not independent, not human and not peer review.",
    }
    out["research/protocol/records/AID-R002-PROTOCOL-DRAFT.json"] = record2(
        "AID-R002-PROTOCOL-DRAFT", "assistance", draft, basis=source_pins, factual="project_decision")
    out["research/protocol/records/AID-R002-INTERNAL-AUDIT.json"] = record2(
        "AID-R002-INTERNAL-AUDIT", "assistance", review,
        basis=sorted(evidence + [{"id": "AID-R002-PROTOCOL-DRAFT", "rev": 1}], key=lambda r: r["id"]),
        factual="researcher_interpretation")
    for path, row in sorted(out.items()):
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dumps(row), encoding="utf-8")
    state_path = ROOT / "research/registry/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["research_state"] = "in_progress"
    state["stage_gates"] = [gate for gate in state["stage_gates"] if gate["stage"] != "protocol"] + [{
        "stage": "protocol",
        "status": "complete",
        "evidence_refs": evidence,
        "review_refs": [{"id": "AID-R002-INTERNAL-AUDIT", "rev": 1}],
        "human_gate_refs": [],
        "artifacts": frozen + [{"path": EXPORT, "sha256": sha256(EXPORT)}, {"path": LEDGER, "sha256": sha256(LEDGER)}],
        "limitations": ("Structural declaration only. Protocol v1 is internal and unregistered; prepared and self-audited by one "
                        "agent with no human review; pilot used web search only; database access is gated "
                        "(HG-R002-DATABASE-ACCESS); comparator readings were tool-mediated and partly abstract-only."),
    }]
    state_path.write_text(dumps(state), encoding="utf-8")
    print(f"wrote {len(out)} records and the protocol stage declaration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
