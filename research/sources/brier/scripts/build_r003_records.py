"""Write the MHAC-R003 Brier-lane live records deterministically.

Run from the repository root:

    python3 research/sources/brier/scripts/build_r003_records.py

Facts were recorded by the executing agent on 2026-10-13 from the pages listed in
research/searches/brier/exports/ACCESS-LEDGER-R003-2026-10-13.csv. Metadata taken only
from a search-result title, a URL or Brier's own reference lists is marked
`candidate`. This script serializes; it fetches nothing. Later changes must append
revisions to the written records.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.record_io import dumps  # noqa: E402

AT = "2026-10-13T01:58:16Z"
ACTOR = {"kind": "agent", "id": "claude-r003-session",
         "tool": "Claude in a claude.ai cloud session (WebSearch, WebFetch, shell)",
         "model": "claude-opus-5-5"}
EXPORT = "research/searches/brier/exports/BRIER-WEBSEARCH-2026-10-13.json"
LEDGER = "research/searches/brier/exports/ACCESS-LEDGER-R003-2026-10-13.csv"
SEEN = "2026-10-13T01:52:59Z"
SEEN2 = "2026-10-13T01:53:19Z"
NO_BYTES = ("No bytes retained: the workspace cannot download from this host and WebFetch "
            "returns an intermediary model's paraphrase only.")
SELF_CITED = ("Listed in Brier's own reference list in the Studia kulturoznawcze 2015 article and/or the "
              "Green Letters 2015 accepted manuscript, read through WebFetch on 2026-10-13 (ledger rows 20, 28); "
              "not checked against the publication itself.")


def missing(state: str, reason: str) -> dict:
    return {"state": state, "reason": reason}


def known(value) -> dict:
    return {"state": "known", "value": value}


RIGHTS_UNKNOWN = {"status": "unknown", "reason": "No licence or permission verified; no bytes retained.",
                  "evidence": missing("unknown", "Licence not checked in R003")}


def rights(status: str, reason: str, evidence: str) -> dict:
    return {"status": status, "reason": reason, "evidence": known(evidence)}


def ref(rid: str) -> dict:
    return {"id": rid, "rev": 1}


def src(*, title, authors, date, identifiers, source_type, edition, metadata_status, evidence,
        access_status, access_at=SEEN, access_reason, rights_=RIGHTS_UNKNOWN, links=(), language="en"):
    return {
        "title": title,
        "authors": [{"name": n, "role": r} for n, r in authors],
        "publication_date": date,
        "identifiers": [{"scheme": s, "value": v, "status": st, "provenance": p} for s, v, st, p in identifiers],
        "source_type": source_type,
        "language": known(language),
        "edition": edition,
        "metadata_status": metadata_status,
        "metadata_evidence": list(evidence),
        "access_status": access_status,
        "access_at": access_at,
        "access_reason": access_reason,
        "rights": rights_,
        "validity": "active",
        "family_links": [{"relation": rel, "source_ref": ref(target), "reason": why} for rel, target, why in links],
        "manifestations": [],
    }


BRIER = ("Brier, Søren", "author")
VOL = "SRC-BRIER-2021-VIDALES-BRIER-EDS"

SOURCES = {
    "SRC-BRIER-1996-JDOC": src(
        title="Cybersemiotics: A New Interdisciplinary Development Applied to the Problems of Knowledge Organisation and Document Retrieval in Information Science",
        authors=[BRIER], date=known("1996"),
        identifiers=[("doi", "10.1108/eb026970", "verified", "DOI landing page fetched 2026-10-13 (R003 ledger row 5)")],
        source_type="article", edition=known("Journal of Documentation 52(3):296-344 (MCB UP)"),
        metadata_status="verified", evidence=["Title, journal, volume, issue, pages, year and DOI reported from the DOI landing page by the fetch tool."],
        access_status="abstract_only", access_reason="Landing page gave the abstract; open availability of the text was not established."),
    "SRC-BRIER-1996-SR": src(
        title="From second-order cybernetics to cybersemiotics: A semiotic re-entry into the second-order cybernetics of Heinz von Foerster",
        authors=[BRIER], date=known("1996-09"),
        identifiers=[("doi", "10.1002/(SICI)1099-1735(199609)13:3<229::AID-SRES96>3.0.CO;2-B", "candidate", "Decoded from the Wiley URL returned by search B-08 and repeated in the academia.edu metadata; the Wiley page returned a client error (ledger row 18)")],
        source_type="article", edition=known("Systems Research 13(3), starting page 229 per the DOI (end page unknown)"),
        metadata_status="candidate", evidence=["Title, author, journal and year from the Wiley search-result title (B-08) and the author manuscript; volume/issue/start page inferred from the DOI string."],
        access_status="unavailable", access_reason="Publisher page could not be fetched (client error). An author manuscript is recorded separately."),
    "SRC-BRIER-1996-SR-MS": src(
        title="From Second-order Cybernetics to Cybersemiotics: A Semiotic Re-entry into the Second-order Cybernetics of Heinz von Foerster",
        authors=[BRIER], date=known("1996-03-21"),
        identifiers=[("url", "https://www.academia.edu/10056952/From_Second_order_Cybernetics_to_Cybersemiotics_A_Semiotic_Re_entry_into_the_Second_order_Cybernetics_of_Heinz_von_Foerster", "verified", "Fetched 2026-10-13 (ledger row 27)")],
        source_type="preprint", edition=known("Author manuscript labelled 'shortend version 21 Marts 1996. 9896 words'; Festschrift contribution for Heinz von Foerster"),
        metadata_status="verified", evidence=["Version note, author affiliation (Royal School of Librarianship, Aalborg Branch) and title reported from the hosted text by the fetch tool."],
        access_status="full_text_available", access_reason="Manuscript text visible on the author's academia.edu profile; read only through WebFetch paraphrase (first 100000 of 107318 characters). " + NO_BYTES,
        links=[("version_of", "SRC-BRIER-1996-SR", "Author manuscript of the Systems Research article; differences from the published version are unknown.")]),
    "SRC-BRIER-2001-SRBS": src(
        title="Cybersemiotics: a reconceptualization of the foundation for information science",
        authors=[BRIER], date=known("2001"),
        identifiers=[("doi", "10.1002/sres.446", "candidate", "From the Wiley URL returned by search B-08; the page returned a client error (ledger row 19)")],
        source_type="article", edition=missing("unknown", "Volume, issue and pages not seen"),
        metadata_status="candidate", evidence=["Title, author, year and journal (Systems Research and Behavioral Science) from the search-result title only."],
        access_status="unavailable", access_reason="Publisher page could not be fetched."),
    "SRC-BRIER-2003-TRIPLEC": src(
        title="The Cybersemiotic Model of Communication: An Evolutionary View on the Threshold between Semiosis and Informational Exchange",
        authors=[BRIER], date=known("2003"),
        identifiers=[("doi", "10.31269/triplec.v1i1.6", "verified", "Shown on the tripleC article page fetched 2026-10-13 (ledger row 3)"),
                     ("url", "https://www.triple-c.at/index.php/tripleC/article/view/6", "verified", "Fetched 2026-10-13")],
        source_type="article", edition=known("tripleC 1(1):71-94"),
        metadata_status="verified", evidence=["Title, author, affiliation, volume, issue, pages, year, DOI and licence reported from the journal page by the fetch tool."],
        access_status="full_text_available", access_reason="Open-access PDF linked from the journal page; not fetched or read.",
        rights_=rights("redistribution_permitted", "Journal page states CC BY-NC-ND 4.0; redistribution of unmodified copies with attribution for non-commercial use.", "Licence statement on the tripleC article page read via WebFetch 2026-10-13")),
    "SRC-BRIER-2006-SEMIOTICA": src(
        title="The cybersemiotic model of communication: An evolutionary model of the threshold between semiosis and informational exchange",
        authors=[BRIER], date=known("2006-02-20"),
        identifiers=[("doi", "10.1515/SEM.2006.008", "verified", "Shown in the download link of the de Gruyter page fetched 2026-10-13 (ledger row 4)")],
        source_type="article", edition=known("Semiotica 2006(158); pages not shown"),
        metadata_status="verified", evidence=["Title, journal, issue, print and online dates and DOI reported from the publisher page by the fetch tool."],
        access_status="abstract_only", access_reason="Only abstract and author note visible; body requires authentication.",
        links=[("version_of", "SRC-BRIER-2003-TRIPLEC", "Candidate relation: near-identical title and abstract to the 2003 tripleC article; full texts not compared.")]),
    "SRC-BRIER-2008-BOOK": src(
        title="Cybersemiotics: why information is not enough!",
        authors=[BRIER], date=known("2008"),
        identifiers=[("isbn", "9780802092205", "verified", "Loughborough University catalogue record fetched 2026-10-13 (ledger row 9)"),
                     ("isbn", "9781442687813", "candidate", "Appears in catalogue and search URLs (oeaw.ac.at, dokumen.pub); the catalogue page was blocked (ledger row 17); format and date unverified")],
        source_type="book", edition=known("University of Toronto Press, Toronto/Buffalo, c2008; xx, 477 pages; Toronto Studies in Semiotics and Communication; bibliography pp. 453-469"),
        metadata_status="verified", evidence=["Catalogue record gives publisher, place, copyright year, ISBN, pagination, series and notes."],
        access_status="metadata_only", access_reason="Catalogue metadata only. No lawful open copy identified; a search result offering the full book on dokumen.pub was not opened because it appears to redistribute the book without permission (ledger row 31)."),
    "SRC-BRIER-2013-BOOK-PB": src(
        title="Cybersemiotics: Why Information Is not Enough",
        authors=[BRIER], date=known("2013-08-13"),
        identifiers=[("isbn", "9781442626362", "verified", "Retailer record fetched 2026-10-13 (ledger row 16)"),
                     ("doi", "10.3138/9781442626362", "candidate", "From the publisher URL recorded in docs/SEED_SOURCES.md; not resolved")],
        source_type="book", edition=known("University of Toronto Press paperback, 2013; 498 pages (retailer count)"),
        metadata_status="verified", evidence=["Publisher, date, binding, ISBN and page count reported from the retailer record by the fetch tool."],
        access_status="metadata_only", access_reason="Retailer metadata only.",
        links=[("version_of", "SRC-BRIER-2008-BOOK", "Candidate relation: later paperback issue of the 2008 book; textual identity with the 2008 printing not verified.")]),
    "SRC-BRIER-2009-CF": src(
        title="Cybersemiotic Pragmaticism and Constructivism", authors=[BRIER], date=known("2009"),
        identifiers=[], source_type="article", edition=known("Constructivist Foundations 5(1):19-38 (as cited by Brier)"),
        metadata_status="candidate", evidence=[SELF_CITED], access_status="not_attempted",
        access_reason="Located only as a citation; no page for the article was opened."),
    "SRC-BRIER-2010-INFOCOMP": src(
        title="Cybersemiotics and the Question of Knowledge", authors=[BRIER], date=known("2010"),
        identifiers=[("isbn", "9789814295475", "verified", "CBS research portal record fetched 2026-10-13 (ledger row 22)")],
        source_type="chapter", edition=known("In Burgin and Dodig-Crnkovic (eds), Information and Computation, World Scientific Series in Information Studies vol. 2, pp. 1-36"),
        metadata_status="conflict", evidence=["CBS record gives 2010 and pages 1-36; the PhilPapers record of the book gives 2011 (ledger rows 22-23). Brier's own reference list gives 2010."],
        access_status="metadata_only", access_reason="CBS record links an external PDF (idt.mdh.se) that was not fetched."),
    "SRC-BRIER-2011-SIGNS": src(
        title="Cybersemiotics: A New Foundation for Transdisciplinary Theory of Information, Cognition, Meaning, Communication and Consciousness",
        authors=[BRIER], date=known("2011-08-17"),
        identifiers=[("url", "https://tidsskrift.dk/signs/article/view/26864", "verified", "Fetched 2026-10-13 (ledger row 24)")],
        source_type="article", edition=known("Signs - International Journal of Semiotics 5:75-111"),
        metadata_status="verified", evidence=["Title, journal, volume, pages and publication date reported from the journal page by the fetch tool."],
        access_status="abstract_only", access_reason="Article page and abstract read; the full text is hosted by the journal but was not fetched."),
    "SRC-BRIER-2011-SEBEOK": src(
        title="Ethology and the Sebeokian way from Zoosemiotics to Cyber(bio)semiotics", authors=[BRIER], date=known("2011"),
        identifiers=[], source_type="chapter", edition=known("In Deely, Kull and Petrilli (eds), Semiotics Continues to Astonish, Mouton de Gruyter, pp. 41-84 (as cited by Brier)"),
        metadata_status="candidate", evidence=[SELF_CITED], access_status="not_attempted", access_reason="Located only as a citation."),
    "SRC-BRIER-2012-TIC": src(
        title="The Transdisciplinary View of Information Theory From a Cybersemiotic Perspective", authors=[BRIER], date=known("2012"),
        identifiers=[], source_type="chapter", edition=known("In Ibekwe-SanJuan and Dousa (eds), Theories of Information, Communication and Knowledge, Springer, pp. 23-49 (as cited by Brier)"),
        metadata_status="candidate", evidence=[SELF_CITED], access_status="not_attempted", access_reason="Located only as a citation."),
    "SRC-BRIER-2012-CHK-SORENSEN": src(
        title="Mind, Matter, and Evolution: An Outline of C.S. Peirce's Evolutionary Cosmogony",
        authors=[("Sørensen, B.", "author"), ("Thellefsen, T.", "author"), BRIER], date=known("2012"),
        identifiers=[], source_type="article", edition=known("Cybernetics and Human Knowing 19(1-2):95-120 (as cited)"),
        metadata_status="candidate", evidence=[SELF_CITED], access_status="not_attempted", access_reason="Located only as a citation."),
    "SRC-BRIER-2013-IR": src(
        title="Cybersemiotics: A New Foundation for Transdisciplinary Theory of Information, Cognition, Meaningful Communication and the Interaction Between Nature and Culture",
        authors=[BRIER], date=known("2013-06"),
        identifiers=[("url", "https://research.cbs.dk/en/publications/cybersemiotics-a-new-foundation-for-transdisciplinary-theory-of-i-2/", "verified", "CBS record fetched 2026-10-13 (ledger row 7)"),
                     ("url", "https://cspeirce.com/menu/library/aboutcsp/brier/brier-cybersemiotics-2013.pdf", "verified", "Published-layout copy fetched 2026-10-13 (ledger row 13)")],
        source_type="article", edition=known("Integral Review 9(2), June 2013 (ARINA)"),
        metadata_status="conflict", evidence=["CBS record and Brier's own reference list give pages 220-263; the published-layout copy's printed pagination begins at 221 (ledger rows 7, 13, 28). Retained unresolved."],
        access_status="full_text_available", access_reason="Published-layout copy hosted on the Arisbe Peirce site; read through WebFetch only to printed p. 247 (truncated). " + NO_BYTES),
    "SRC-BRIER-2013-ORIGINS": src(
        title="Cybersemiotics: A new foundation for transdisciplinary theory of consciousness, cognition, meaning and communication",
        authors=[BRIER], date=known("2013"),
        identifiers=[], source_type="chapter", edition=known("In L. Swan (ed.), Origins of Mind, Springer, pp. 97-126 (as cited by Brier)"),
        metadata_status="candidate", evidence=[SELF_CITED, "The same title appears on Brier's PhilPeople profile description (ledger row 2)."],
        access_status="not_attempted", access_reason="Located only as a citation."),
    "SRC-BRIER-2013-XIAN": src(
        title="How to define an information concept for a universal theory of information", authors=[BRIER], date=known("2013"),
        identifiers=[], source_type="conference_paper", edition=known("Proceedings of the 1st International Conference on Philosophy of Information, Xi'an, 19-21 November 2013, pp. 277-299 (as cited by Brier)"),
        metadata_status="candidate", evidence=[SELF_CITED], access_status="not_attempted", access_reason="Located only as a citation."),
    "SRC-BRIER-2013-JOSLYN": src(
        title="What Does It Take to Produce Interpretation? Informational, Peircean, and Code-Semiotic Views on Biosemiotics",
        authors=[BRIER, ("Joslyn, C. A.", "author")], date=known("2013-04-01"),
        identifiers=[("doi", "10.1007/s12304-012-9153-5", "verified", "PNNL publication record fetched 2026-10-13 (R003 ledger row 30)"),
                     ("other", "PNNL-SA-86502", "verified", "Report number on the PNNL record")],
        source_type="article", edition=known("Biosemiotics 6(1):143-159"),
        metadata_status="verified", evidence=["Authors, title, journal, volume, issue, pages, date and DOI reported from the PNNL record by the fetch tool; consistent with Brier's own reference lists."],
        access_status="abstract_only", access_at=SEEN2, access_reason="Abstract only."),
    "SRC-BRIER-2014-CF-COMMENT": src(
        title="Phenomenological Computation?", authors=[BRIER], date=known("2014-03-15"),
        identifiers=[("url", "http://www.univie.ac.at/constructivism/journal/articles/9/2/234.brier.pdf", "candidate", "URL as printed in Brier's 2015 reference list; not opened")],
        source_type="other", edition=known("Open peer commentary, Constructivist Foundations 9(2) (as cited by Brier)"),
        metadata_status="candidate", evidence=[SELF_CITED, "The title also appears on Brier's PhilPeople profile description (ledger row 2)."],
        access_status="not_attempted", access_reason="Located only as a citation."),
    "SRC-BRIER-2015-GL": src(
        title="Cybersemiotics and the Reasoning Powers of the Universe: Philosophy of Information in a Semiotic-Systemic Transdisciplinary Approach",
        authors=[BRIER], date=known("2015"),
        identifiers=[("doi", "10.1080/14688417.2015.1070684", "verified", "Printed in the accepted manuscript fetched 2026-10-13 (ledger row 20)")],
        source_type="article", edition=known("Green Letters 19(3):280-292 (Version of Record)"),
        metadata_status="verified", evidence=["Journal, volume, issue, pages and DOI as printed in the accepted manuscript's cover note."],
        access_status="metadata_only", access_reason="Version of Record not accessed; accepted manuscript recorded separately."),
    "SRC-BRIER-2015-GL-AM": src(
        title="Cybersemiotics and the Reasoning Powers of the Universe: Philosophy of Information in a Semiotic-Systemic Transdisciplinary Approach",
        authors=[BRIER], date=known("2015-09-16"),
        identifiers=[("url", "https://research-api.cbs.dk/ws/files/44031602/s_ren_brier_cybersemiotics_reasoning_powers_postprint.pdf", "verified", "Fetched 2026-10-13 (ledger row 20)")],
        source_type="preprint", edition=known("Accepted manuscript (post-print) deposited at Copenhagen Business School; 16 pages"),
        metadata_status="verified", evidence=["Version label and availability date reported from the deposited file by the fetch tool."],
        access_status="full_text_available", access_reason="Deposited accepted manuscript read through WebFetch (identity, abstract, technology passages, references). " + NO_BYTES,
        links=[("version_of", "SRC-BRIER-2015-GL", "Accepted manuscript of the Green Letters article.")]),
    "SRC-BRIER-2015-PBMB": src(
        title="Can Biosemiotics be a \"Science\" if its Purpose is to be a Bridge between the Natural, Social and Human Sciences?",
        authors=[BRIER], date=known("2015"),
        identifiers=[("doi", "10.1016/j.pbiomolbio.2015.08.001", "verified", "CBS research portal record fetched 2026-10-13 (ledger row 26)")],
        source_type="article", edition=known("Progress in Biophysics & Molecular Biology 119(3):576-587 (Elsevier)"),
        metadata_status="verified", evidence=["Title, journal, volume, issue, pages, year and DOI reported from the CBS record by the fetch tool."],
        access_status="metadata_only", access_reason="No file attached to the CBS record; publisher page not accessed."),
    "SRC-BRIER-2017-PROC": src(
        title="Can Cybersemiotics solve the problem of informational transdisciplinarity?", authors=[BRIER], date=known("2017-06-26"),
        identifiers=[("url", "https://sciforum.net/paper/download/4105/manuscript", "verified", "Fetched 2026-10-13 (ledger row 25)")],
        source_type="conference_paper", edition=known("Extended abstract, Proceedings (MDPI) 2017 vol. 1; conference not named in the text"),
        metadata_status="verified", evidence=["Title, author, affiliation, venue and date reported from the manuscript file by the fetch tool; no DOI given."],
        access_status="full_text_available", access_reason="Extended abstract read through WebFetch. " + NO_BYTES),
    "SRC-BRIER-2019-TJES": src(
        title="Cybersemiotic Systemic and Semiotical Based Transdisciplinarity", authors=[BRIER], date=known("2019-03-15"),
        identifiers=[("doi", "10.22545/2019/0119", "verified", "Printed in the publisher's version fetched 2026-10-13 (ledger row 21)"),
                     ("url", "https://research-api.cbs.dk/ws/files/60162937/s_ren_brier_cybersemiotic_systemic_and_semiotical_publishersversion.pdf", "verified", "Fetched 2026-10-13")],
        source_type="article", edition=known("Transdisciplinary Journal of Engineering & Science 10:81-92"),
        metadata_status="verified", evidence=["Journal, volume, pages, dates, DOI and licence reported from the publisher's version by the fetch tool."],
        access_status="full_text_available", access_reason="Publisher's version deposited at CBS; only identity and section structure were read. " + NO_BYTES,
        rights_=rights("redistribution_permitted", "Article states a Creative Commons Attribution licence.", "CC BY statement printed in the article, read via WebFetch 2026-10-13")),
    VOL: src(
        title="Introduction to Cybersemiotics: A Transdisciplinary Perspective",
        authors=[("Vidales, Carlos", "editor"), ("Brier, Søren", "editor")], date=known("2021-04-14"),
        identifiers=[("doi", "10.1007/978-3-030-52746-4", "verified", "Springer book page fetched 2026-10-13 (ledger row 8)"),
                     ("isbn", "9783030527457", "verified", "Hardcover ISBN on the Springer page"),
                     ("isbn", "9783030527488", "verified", "Softcover ISBN on the Springer page"),
                     ("isbn", "9783030527464", "verified", "eBook ISBN on the Springer page")],
        source_type="book", edition=known("1st edition; Biosemiotics vol. 21; Springer, Cham; XIX + 555 pages"),
        metadata_status="verified", evidence=["Editors, series, publisher, dates, ISBNs, DOI, page count and full table of contents reported from the Springer page."],
        access_status="metadata_only", access_reason="Table of contents and metadata only; chapters are subscription content."),
    "SRC-BRIER-2021-CH2": src(
        title="Cybersemiotic Systemic and Semiotical Based Transdisciplinarity", authors=[BRIER], date=known("2021"),
        identifiers=[("doi", "10.1007/978-3-030-52746-4_2", "candidate", "Chapter DOI pattern of the volume; chapter 2 page not opened")],
        source_type="chapter", edition=known("Chapter 2, pp. 17-31, in Vidales and Brier (eds) 2021"),
        metadata_status="verified", evidence=["Title, sole author and pages from the Springer table of contents (ledger row 8)."],
        access_status="metadata_only", access_reason="Subscription chapter; not accessed.",
        links=[("version_of", "SRC-BRIER-2019-TJES", "Candidate relation: identical title to the 2019 open-access article; texts not compared."),
               ("companion_of", VOL, "Chapter of the edited volume.")]),
}

RECEPTION = {
    "SRC-BRIER-REC-COBLEY-2010-SIGNS": src(
        title="Second-order thinking, first-class reasoning", authors=[("Cobley, Paul", "author")], date=known("2010"),
        identifiers=[("url", "https://tidsskrift.dk/signs/article/download/26861/23621", "verified", "Fetched 2026-10-13 (ledger row 12)")],
        source_type="review", edition=known("Signs 3:69-107 (ISSN 1902-8822); review article of Brier (2008)"),
        metadata_status="verified", evidence=["Author, title, journal, volume, pages and ISSN reported from the article file by the fetch tool."],
        access_status="full_text_available", access_reason="Review article read through WebFetch paraphrase with page-level outline. " + NO_BYTES),
    "SRC-BRIER-REC-ANKER-2012": src(
        title="Review of Søren Brier's (2008) Cybersemiotics: Why information is not enough",
        authors=[("Anker, Kathrine Elizabeth", "author")], date=known("2012-10-11"),
        identifiers=[("doi", "10.1515/sem-2012-0085", "candidate", "From the de Gruyter URL; not printed on the visible page (ledger row 10)")],
        source_type="review", edition=missing("unknown", "Journal name, volume and pages not shown on the visible page"),
        metadata_status="candidate", evidence=["Reviewer, title and print/online dates reported from the publisher page; journal identity inferred only from the DOI prefix."],
        access_status="metadata_only", access_reason="Review text behind a paywall."),
    "SRC-BRIER-REC-KYBERNETES-2009": src(
        title="Cybersemiotics: Why Information Is Not Enough!", authors=[], date=known("2009"),
        identifiers=[("doi", "10.1108/03684920910962713", "candidate", "From the Emerald URL returned by search B-06; page blocked by verification (ledger row 11)")],
        source_type="review", edition=known("Kybernetes 38(5), page 840 per the Emerald URL path"),
        metadata_status="candidate", evidence=["Title from the search result; journal, volume, issue and page inferred from the URL path; reviewer unknown; year inferred from the DOI string."],
        access_status="unavailable", access_reason="Publisher page returned a traffic-verification challenge; not bypassed."),
    "SRC-BRIER-REC-VIDALES-2022": src(
        title="Cybersemiotics, a transdisciplinary view on communication, information, signification, and cognition",
        authors=[("Vidales, Carlos", "author")], date=known("2022"),
        identifiers=[("doi", "10.2478/lf-2022-0004", "verified", "Journal page fetched 2026-10-13 (ledger row 6)")],
        source_type="article", edition=known("Linguistic Frontiers 5(1):53-56 (commentary); page lists online date 2024-08-01"),
        metadata_status="verified", evidence=["Author, title, journal, volume, issue, pages, DOI and licence reported from the journal page."],
        access_status="abstract_only", access_reason="Abstract read; PDF linked but not fetched.",
        rights_=rights("redistribution_permitted", "Journal page states CC BY-NC-ND 4.0.", "Licence statement on the journal page read via WebFetch 2026-10-13")),
}

CHAPTERS = [
    ("SRC-BRIER-REC-VIDALES-2021-CH3", "From Cybernetics to Semiotics to Cybersemiotics: The Question of Communication and Meaning Processes in Living Systems", "Vidales, Carlos", "3", "33-74"),
    ("SRC-BRIER-REC-NOTH-2021-CH4", "System, Sign, Information, and Communication in Cybersemiotics, Systems Theory, and Peirce", "Nöth, Winfried", "4", "75-95"),
    ("SRC-BRIER-REC-COBLEY-2021-CH6", "Practice as Research: A Cybersemiotic Overview of Knowing", "Cobley, Paul", "6", "105-125"),
    ("SRC-BRIER-REC-JACQUES-2021-CH10", "Human-Computer Interaction Design and the Cybersemiotic Experience", "Jacques, Claudia", "10", "241-281"),
    ("SRC-BRIER-REC-ZHOU-2021-CH11", "The Communication of Form. Why Cybersemiotic Star Is Necessary for Information Studies?", "Zhou, Liqian", "11", "283-300"),
    ("SRC-BRIER-REC-HORTA-2021-CH14", "Cybersemiotics and Epistemology: A Critical Review of the Conditions of \"Observation\" from Transcendental Semiotics", "Horta, Julio", "14", "399-420"),
    ("SRC-BRIER-REC-ROMEU-2021-CH16", "Communication and Evolution", "Romeu, Vivian", "16", "445-477"),
    ("SRC-BRIER-REC-THOMSEN-2021-CH17", "Prolegomena to Cybersemiotic Discourse Pragmatics. Total Human Evolutionary Cognition and Communication", "Thomsen, Ole Nedergaard", "17", "479-539"),
]
for rid, title, author, number, pages in CHAPTERS:
    jacques = number == "10"
    RECEPTION[rid] = src(
        title=title, authors=[(author, "author")], date=known("2021"),
        identifiers=([("doi", "10.1007/978-3-030-52746-4_10", "verified", "Springer chapter page fetched 2026-10-13 (ledger row 29)")] if jacques else []),
        source_type="chapter", edition=known(f"Chapter {number}, pp. {pages}, in Vidales and Brier (eds) 2021"),
        metadata_status="verified",
        evidence=["Title, author and pages from the Springer table of contents (ledger row 8)."] + (
            ["Abstract, keywords, affiliation and first-online date (2021-04-15) from the chapter page (ledger row 29)."] if jacques else []),
        access_status="abstract_only" if jacques else "metadata_only",
        access_at=SEEN2 if jacques else SEEN,
        access_reason=("Chapter preview only (abstract, keywords, notes, references); body is subscription content." if jacques
                       else "Table-of-contents entry only; subscription chapter."),
        links=[("companion_of", VOL, "Chapter of the edited volume.")])

ALL = {**SOURCES, **RECEPTION}

OPENED = "The agent fetched this URL in R003 and identified the publication from its content (R003 access ledger)."
ID_IN_URL = "The URL carries this publication's persistent identifier or ISBN; the page itself was not opened."
SAME_FILE = "Same journal article identifier as a URL the agent fetched (different galley or path)."
RES = {
    ("B-01", 4): ("SRC-BRIER-2006-SEMIOTICA", OPENED), ("B-01", 8): (VOL, ID_IN_URL),
    ("B-02", 1): ("SRC-BRIER-REC-COBLEY-2010-SIGNS", SAME_FILE), ("B-02", 4): ("SRC-BRIER-REC-VIDALES-2022", OPENED),
    ("B-02", 8): ("SRC-BRIER-2006-SEMIOTICA", OPENED),
    ("B-03", 1): ("SRC-BRIER-2003-TRIPLEC", OPENED), ("B-03", 2): ("SRC-BRIER-2003-TRIPLEC", SAME_FILE),
    ("B-03", 3): ("SRC-BRIER-2006-SEMIOTICA", OPENED),
    ("B-04", 1): ("SRC-BRIER-2013-IR", OPENED), ("B-04", 2): ("SRC-BRIER-2013-IR", OPENED),
    ("B-04", 6): ("SRC-BRIER-2011-SIGNS", OPENED),
    ("B-05", 1): ("SRC-BRIER-1996-JDOC", OPENED),
    ("B-06", 2): ("SRC-BRIER-REC-COBLEY-2010-SIGNS", OPENED), ("B-06", 3): ("SRC-BRIER-REC-KYBERNETES-2009", ID_IN_URL),
    ("B-06", 4): ("SRC-BRIER-REC-KYBERNETES-2009", "Emerald article path for the same review (volume 38, issue 5, page 840)."),
    ("B-06", 5): ("SRC-BRIER-REC-ANKER-2012", OPENED),
    ("B-07", 2): ("SRC-BRIER-REC-COBLEY-2010-SIGNS", SAME_FILE), ("B-07", 6): ("SRC-BRIER-2006-SEMIOTICA", OPENED),
    ("B-08", 1): ("SRC-BRIER-1996-SR", ID_IN_URL), ("B-08", 3): ("SRC-BRIER-2001-SRBS", ID_IN_URL),
    ("B-08", 4): ("SRC-BRIER-1996-SR-MS", OPENED),
    ("B-09", 1): ("SRC-BRIER-2017-PROC", OPENED), ("B-09", 2): ("SRC-BRIER-2011-SIGNS", OPENED),
    ("B-09", 3): ("SRC-NOV-BRIER-2015", OPENED),
    ("B-10", 1): ("SRC-NOV-BRIER-2015", OPENED), ("B-10", 2): ("SRC-BRIER-2017-PROC", OPENED),
    ("B-10", 3): (VOL, ID_IN_URL), ("B-10", 4): ("SRC-BRIER-2011-SIGNS", OPENED), ("B-10", 5): (VOL, OPENED),
    ("B-10", 7): ("SRC-BRIER-2015-GL-AM", OPENED), ("B-10", 8): ("SRC-BRIER-2003-TRIPLEC", SAME_FILE),
    ("B-11", 1): ("SRC-BRIER-2015-PBMB", OPENED), ("B-11", 3): ("SRC-BRIER-2015-GL-AM", OPENED),
    ("B-11", 7): ("SRC-BRIER-2013-BOOK-PB", ID_IN_URL), ("B-11", 8): ("SRC-BRIER-2013-BOOK-PB", OPENED),
    ("B-11", 9): ("SRC-BRIER-2013-IR", OPENED),
    ("B-12", 2): ("SRC-BRIER-2010-INFOCOMP", OPENED), ("B-12", 4): ("SRC-BRIER-2019-TJES", OPENED),
    ("B-12", 6): ("SRC-NOV-BRIER-2015", OPENED), ("B-12", 7): ("SRC-BRIER-2013-BOOK-PB", ID_IN_URL),
    ("B-12", 8): ("SRC-BRIER-REC-COBLEY-2010-SIGNS", SAME_FILE),
    ("B-14", 1): ("SRC-BRIER-REC-JACQUES-2021-CH10", OPENED),
    ("B-14", 7): ("SRC-NOV-DESOUZA-2005", ID_IN_URL), ("B-14", 8): ("SRC-NOV-DESOUZA-2005", ID_IN_URL),
    ("B-15", 6): ("SRC-BRIER-2017-PROC", OPENED), ("B-15", 8): ("SRC-BRIER-REC-VIDALES-2022", OPENED),
    ("B-15", 9): ("SRC-BRIER-2015-GL-AM", OPENED),
    ("B-16", 1): ("SRC-BRIER-REC-COBLEY-2010-SIGNS", SAME_FILE), ("B-16", 2): (VOL, ID_IN_URL),
    ("B-16", 3): (VOL, OPENED), ("B-16", 4): ("SRC-BRIER-2017-PROC", OPENED),
    ("B-16", 6): (VOL, ID_IN_URL), ("B-16", 7): (VOL, ID_IN_URL),
    ("B-17", 1): ("SRC-BRIER-2013-JOSLYN", OPENED),
}
EXTERNAL = {"SRC-NOV-BRIER-2015", "SRC-NOV-DESOUZA-2005"}


def record(rid, kind, data, basis=(), factual="source_reported", at=AT):
    return {"schema_version": 1, "id": rid, "kind": kind, "synthetic": False, "issue": 3,
            "revisions": [{"rev": 1, "at": at, "actor": ACTOR, "basis": list(basis), "data": data,
                           "factual_status": factual}]}


def main() -> int:
    out = {}
    for rid, data in ALL.items():
        basis = sorted({json.dumps(link["source_ref"], sort_keys=True) for link in data["family_links"]})
        out[f"research/sources/brier/records/{rid}.json"] = record(rid, "source", data, [json.loads(b) for b in basis])
    export = json.loads((ROOT / EXPORT).read_text(encoding="utf-8"))
    digest = hashlib.sha256((ROOT / EXPORT).read_bytes()).hexdigest()
    used, run_ids = set(), []
    for batch in export["batches"]:
        for run in batch["runs"]:
            label = run["label"]
            run_id = "SRCH-R003-" + label.replace("-", "")
            run_ids.append(run_id)
            out[f"research/searches/brier/records/{run_id}.json"] = record(run_id, "search_run", {
                "lane": "brier", "protocol_version": "v1", "mode": "production", "status": "partial",
                "platform": "General web search engine via the agent's WebSearch tool (protocol channel C8)",
                "interface": f"WebSearch tool, {run['mode']} mode, US-only results",
                "query": run["query"], "filters": ["No user-set filters; tool default US-only results"],
                "coverage": {"start": missing("unknown", "The engine does not state its index coverage"),
                             "end": missing("unknown", "The engine does not state its index coverage")},
                "started_at": known(batch["window_start"]), "finished_at": known(batch["window_end"]),
                "reported_count": missing("not_reported", "The engine reports no total hit count"),
                "retrieved_count": len(run["results"]),
                "export": known({"path": EXPORT, "sha256": digest}),
                "pagination": {"complete": False, "detail": "One page of top results only; the tool exposes no further pages."},
                "failures": [],
                "boundary": (f"Brier-lane run {label} ({batch['purpose']}). Channel C8 discovery under protocol v1: titles and URLs only, "
                             "not a bibliographic database search; times are batch-window bounds."),
            }, factual="discovery")
            for result in run["results"]:
                n = result["ordinal"]
                hid = f"HIT-R003-{label.replace('-', '')}-{n:02d}"
                data = {"search_ref": ref(run_id), "ordinal": n,
                        "raw_metadata": f"{result['title']} | {result['url']}",
                        "returned_identifiers": [{"scheme": "url", "value": result["url"]}]}
                basis = [ref(run_id)]
                if (label, n) in RES:
                    target, why = RES[(label, n)]
                    assert target in ALL or target in EXTERNAL, target
                    used.add((label, n))
                    data.update(status="resolved", resolution_reason=why, source_ref=ref(target))
                    basis.append(ref(target))
                else:
                    data.update(status="unresolved", resolution_reason="Publication identity not checked for this occurrence.")
                out[f"research/searches/brier/records/hits/{hid}.json"] = record(hid, "search_hit", data, basis, "discovery")
    assert used == set(RES), sorted(set(RES) - used)
    source_ids = sorted(ALL)
    out["research/sources/brier/records/AID-R003-BRIER-INVENTORY.json"] = record(
        "AID-R003-BRIER-INVENTORY", "assistance", {
            "subtype": "assistance",
            "task": "Execute Brier-lane discovery under protocol v1 (C8 web search, backward tracing from Brier's own reference lists), verify bibliographic identity where pages were reachable, and record access, rights and version relations.",
            "input_refs": [ref(i) for i in ["SRC-NOV-BRIER-2010", "SRC-NOV-BRIER-2015", "SRC-NOV-COBLEY-2010", "SRC-NOV-THOMSEN-BRIER-2014"]],
            "output_refs": [ref(i) for i in source_ids] + [ref(i) for i in run_ids],
            "artifacts": [EXPORT, LEDGER, "research/sources/brier/README.md"],
            "verification_steps": ["Each record's metadata status reflects what a fetched page showed; facts from search titles, URLs or Brier's own reference lists are marked candidate.",
                                   "Conflicting metadata (Integral Review pages; Information and Computation year) retained as conflict.",
                                   "Search transcriptions re-compared with tool output for B-03, B-11 and B-16."],
            "limitations": "Single agent; web search only (no bibliographic database, no forward citation index); tool-mediated paraphrase; no source bytes retained; reading limited to identity, abstracts and outlines.",
            "status": "performed", "performed_at": known(SEEN2),
            "independence": "Single executing agent. Not a human check and not independent of the work it describes.",
        }, [ref(i) for i in ["SRC-NOV-BRIER-2010", "SRC-NOV-BRIER-2015", "SRC-NOV-COBLEY-2010", "SRC-NOV-THOMSEN-BRIER-2014"]],
        "researcher_interpretation")
    out["research/sources/brier/records/HG-R003-BRIER-FULLTEXT.json"] = record(
        "HG-R003-BRIER-FULLTEXT", "human_gate", {
            "need": "Lawfully obtained files of Brier's core texts so that #7 can hash them and read with page locators.",
            "reason": "The workspace cannot download from publishers or repositories and WebFetch returns paraphrase only, so no Brier text can be read with verifiable locators; the 2008 monograph has no lawful open copy.",
            "attempted_remedies": [
                "Located open copies for nine items (journal sites, CBS repository, Arisbe) on 2026-10-13.",
                "Shell download blocked by the session proxy; owner's built-in browser blocks the tested hosts.",
                "Declined an apparently unauthorized full-book copy (ledger row 31).",
            ],
            "owner_action": "Part A: save nine open-access PDFs from direct links into one folder outside the repository and connect it to the chat. Part B (optional): add paywalled core items only if lawfully available. Steps: research/sources/brier/gates/HG-R003-BRIER-FULLTEXT.md.",
            "evidence": missing("unknown", "No files have been supplied"),
            "completion_signal": "A connected folder containing the Part A files (and any Part B files).",
            "stop_condition": "Without files, #7 makes only bounded tool-mediated statements and no whole-book claims; nothing is purchased, no account is created and no one is contacted.",
            "status": "waiting", "gate_class": "source_access",
            "authorized_actor": missing("unknown", "No authorization has been given"),
        }, factual="project_decision")
    for path, row in sorted(out.items()):
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dumps(row), encoding="utf-8")
    print(f"wrote {len(out)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
