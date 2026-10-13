"""Write the MHAC-R004 related-theory records deterministically.

Run from the repository root after the lookups and exports exist:

    python3 research/sources/related/scripts/build_r004_records.py

Every fact below comes from a retained lookup response, a fetched page or file listed in
research/searches/related/exports/ACCESS-LEDGER-R004-2026-10-13.csv, or Brier's own reference
lists (BRIER-REFLISTS-R004.json). The script fetches nothing. It writes source, search_run,
search_hit and assistance records and the derived source map CSV.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.record_io import dumps  # noqa: E402
from candidates_r004 import CANDIDATES, ROUND2  # noqa: E402

AT = "2026-10-13T07:20:54Z"
ACTOR = {"kind": "agent", "id": "claude-r004-session",
         "tool": "Claude in a claude.ai cloud session (WebSearch, shell with network access, Python)",
         "model": "claude-opus-5-5"}
WEB = "research/searches/related/exports/RELATED-WEBSEARCH-2026-10-13.json"
LOOKUPS = "research/searches/related/exports/lookups/MANIFEST.json"
BRL = "research/searches/related/exports/BRIER-REFLISTS-R004.json"
LEDGER = "research/searches/related/exports/ACCESS-LEDGER-R004-2026-10-13.csv"
SOURCE_MAP = "research/sources/related/SOURCE-MAP-R004.csv"
AUTHORS = "research/sources/related/BRIER-CITED-AUTHORS-R004.csv"
CONCEPT_MAP = "research/sources/related/CONCEPT-MAP-R004.csv"
MEMO = "research/sources/related/README.md"
SRC_DIR = "research/sources/related/records"
SRCH_DIR = "research/searches/related/records"
LOOKED = "2026-10-13T06:41:33Z"
FETCHED = "2026-10-13T06:46:27Z"


def missing(state, reason):
    return {"state": state, "reason": reason}


def known(value):
    return {"state": "known", "value": value}


def ref(rid):
    return {"id": rid, "rev": 1}


RIGHTS_UNKNOWN = {"status": "unknown", "reason": "No licence verified in R004; no bytes retained.",
                  "evidence": missing("unknown", "Licence not checked")}


def cc_by(evidence):
    return {"status": "redistribution_permitted", "reason": "Creative Commons Attribution licence; reuse with attribution.",
            "evidence": known(evidence)}


def lk(key, route="crossref", item=0):
    return f"Lookup {key} ({route}) result {item + 1}, research/searches/related/exports/lookups/"


# ---------------------------------------------------------------------------------------------
# Source records. Each entry: id suffix -> dict(fields) plus R004 map fields (tier, cluster, role,
# reading). Titles, authors, venues and identifiers are copied from the cited lookup or page.
# ---------------------------------------------------------------------------------------------
S = {}


def add(key, *, title, authors, date, ids=(), stype, edition, status, evidence, access, access_reason,
        tier, cluster, role, reading, rights=RIGHTS_UNKNOWN, language="en", translation="Original English text",
        links=(), manifestations=(), access_at=LOOKED):
    S[key] = dict(
        record={
            "title": title,
            "authors": [{"name": n, "role": r} for n, r in authors],
            "publication_date": date,
            "identifiers": [{"scheme": s, "value": v, "status": st, "provenance": p} for s, v, st, p in ids],
            "source_type": stype, "language": known(language), "edition": edition,
            "metadata_status": status, "metadata_evidence": list(evidence),
            "access_status": access, "access_at": access_at, "access_reason": access_reason,
            "rights": rights, "validity": "active",
            "family_links": [{"relation": rel, "source_ref": ref(t), "reason": why} for rel, t, why in links],
            "manifestations": list(manifestations),
        },
        tier=tier, cluster=cluster, role=role, reading=reading, translation=translation)


A = "author"
CITED_BY_BRIER = "Cited in Brier's own reference lists parsed from hashed files (BRIER-REFLISTS-R004.json)"

# --- T2: Brier's dependencies ------------------------------------------------------------------
add("PEIRCE-CP", title="Collected Papers of Charles Sanders Peirce", authors=[("Peirce, Charles Sanders", A),
    ("Hartshorne, Charles", "editor"), ("Weiss, Paul", "editor"), ("Burks, Arthur W.", "editor")], date=known("1931"),
    ids=[("other", "Open Library work OL1834319W", "verified", lk("PEIRCE-CP", "openlibrary"))],
    stype="book", edition=known("8 vols., Harvard University Press, 1931-1958; Brier cites the 1994 Intelex CD-ROM reproduction (BRL entries)"),
    status="verified", evidence=["Open Library work record (first published 1931, 12 editions)", CITED_BY_BRIER + ": IR 2013, SK 2015, GL 2015 AM"],
    access="metadata_only", access_reason="Catalogue metadata only; no edition consulted.",
    tier="T2", cluster="peirce", role="Primary source for sign, object, interpretant and the categories; the edition Brier cites (Intelex CD-ROM reproduction).",
    reading="Not read", translation="Original English text (editors' compilation of manuscripts)")
add("PEIRCE-EP2", title="The Essential Peirce: Selected Philosophical Writings, Volume 2 (1893-1913)",
    authors=[("Peirce, Charles Sanders", A), ("Peirce Edition Project", "editor")], date=known("1998"),
    ids=[("other", "Open Library work OL1834312W (both volumes)", "verified", lk("PEIRCE-EP2", "openlibrary"))],
    stype="book", edition=known("Indiana University Press, 1998 (volume 2; volume 1, 1992, is the same Open Library work)"),
    status="verified", evidence=["Open Library work 'The Essential Peirce' (5 editions)", CITED_BY_BRIER + ": SK 2015, GL 2015 AM (1998, Vol. 2)"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="peirce", role="Late sign theory, including the emotional/energetic/logical interpretants (EP2:409 as quoted in ATKIN-SEP section 4.3).",
    reading="Not read; locator known only through ATKIN-SEP")
add("PEIRCE-W", title="Writings of Charles S. Peirce: A Chronological Edition", authors=[("Peirce, Charles Sanders", A), ("Peirce Edition Project", "editor")],
    date=known("1982"), ids=[("other", "Open Library work OL1834316W", "verified", lk("PEIRCE-W", "openlibrary"))],
    stype="book", edition=known("Indiana University Press, 1982-; Brier cites vols. 1-6 and 8 (1982-2014)"),
    status="verified", evidence=["Open Library work record (7 editions)", CITED_BY_BRIER + ": SK 2015, GL 2015 AM"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="peirce", role="Critical edition for early sign theory (e.g. the 1867 New List).", reading="Not read")
add("SHORT-2007", title="Peirce's Theory of Signs", authors=[("Short, T. L.", A)], date=known("2007"),
    ids=[("other", "Open Library work OL8332157W", "verified", lk("SHORT-2007", "openlibrary-ta"))],
    stype="book", edition=known("Cambridge University Press, 2007"),
    status="verified", evidence=["Open Library work record (7 editions)", "Crossref holds a 2018 review in Anuario Filosofico naming the book as CUP 2007, 374 pp. (lookup SHORT-2007 result 2)", CITED_BY_BRIER + ": IR 2013, SK 2015, GL 2015 AM"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="peirce", role="Secondary reconstruction of Peirce's semeiotic, cited in all three Brier lists; reading aid for #7.",
    reading="Not read")
add("ATKIN-SEP", title="Peirce's Theory of Signs", authors=[("Atkin, Albert", A)], date=known("2006-10-13"),
    ids=[("url", "https://plato.stanford.edu/entries/peirce-semiotics/", "verified", "Fetched 2026-10-13 (R004 ledger row 11)")],
    stype="web", edition=known("Stanford Encyclopedia of Philosophy entry; first published 13 Oct 2006, substantive revision 4 Aug 2022"),
    status="verified", evidence=["Page metadata and header read from the fetched page"],
    access="full_text_available", access_at=FETCHED,
    access_reason="Entry fetched and hashed; sections 1.3, 4.2 and 4.3 read. Bytes not committed.",
    manifestations=[{"id": "SEP-2026-10-13", "sha256": "5719f471e32f77b07781786663c506b2a22c762b69544cfe716ea5251fce08b8",
                     "extent": 73, "coordinate": "html_paragraph_1based", "location": "https://plato.stanford.edu/entries/peirce-semiotics/"}],
    tier="T2", cluster="peirce", role="Open reference account of interpretant divisions used to check how 'interpretant' is used by Brier and the project.",
    reading="Sections 1.3, 4.2 and 4.3 (paragraphs 9-11 and 43-67 of 73, with the block quotations inside them)")
add("LUHMANN-1995", title="Social Systems", authors=[("Luhmann, Niklas", A)], date=known("1995"),
    ids=[("other", "Open Library work OL1652158W", "verified", lk("LUHMANN-1995", "openlibrary-ta"))],
    stype="book", edition=known("Stanford University Press, 1995 (as cited by Brier)"),
    status="verified", evidence=["Open Library work record (1995, 2 editions)", CITED_BY_BRIER + ": IR 2013, SK 2015, GL 2015 AM"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="autopoiesis", role="Communication as an autopoietic social system; the layer Brier combines with Peirce.",
    reading="Not read", translation="English edition; a German original is likely but was not verified in R004 (translator not recorded in the lookup)")
add("MATURANA-VARELA-1980", title="Autopoiesis and Cognition: The Realization of the Living", authors=[("Maturana, Humberto R.", A), ("Varela, Francisco J.", A)],
    date=known("1980"), ids=[("isbn", "9789027710161", "verified", lk("MATURANA-VARELA-1980")),
                             ("doi", "10.1007/978-94-009-8947-4", "candidate", "Book-level prefix of chapter DOIs ..._12 and ..._13 in the Crossref lookup")],
    stype="book", edition=known("D. Reidel, 1980, Boston Studies in the Philosophy of Science (series named in the Crossref chapter records)"),
    status="candidate", evidence=["Crossref chapter records 'Diversity of Autopoiesis' (pp. 96-111) and 'Presence of Autopoiesis' by Maturana and Varela, 1980, in Boston Studies", "Book title as cited by Brier (BRL entries)"],
    access="metadata_only", access_reason="Chapter metadata only.",
    tier="T2", cluster="autopoiesis", role="Autopoiesis and the observer; cited in all three Brier lists, so a likely source of the closure concepts #7 must trace.",
    reading="Not read", translation="English; earlier Spanish texts may underlie parts, not verified")
add("MATURANA-1988B", title="Reality: The Search for Objectivity or the Quest for a Compelling Argument", authors=[("Maturana, Humberto R.", A)],
    date=known("1988"), ids=[("doi", "10.1080/03033910.1988.10557705", "verified", lk("MATURANA-1988", "crossref", 1))],
    stype="article", edition=known("The Irish Journal of Psychology 9(1):25-82"),
    status="verified", evidence=["Crossref record: title, author, journal, volume, issue, pages"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T2", cluster="autopoiesis", role="Maturana's observer-dependent account of reality cited by Brier (1988b).", reading="Not read")
add("MATURANA-1988A", title="Ontology of Observing: The Biological Foundations of Self-Consciousness and the Physical Domain of Existence",
    authors=[("Maturana, Humberto R.", A)], date=known("1988"), stype="other",
    edition=known("Cited by Brier as The Irish Journal of Psychology 9(1):25-82, the same pages as 1988b"),
    status="conflict", evidence=["Brier's lists give identical volume, issue and pages for 1988a and 1988b (BRL-IR2013, BRL-SK2015, BRL-GL2015AM)",
                                 "Crossref shows only 'Reality: ...' at those pages and found no record with this title (lookup MATURANA-1988)"],
    access="not_attempted", access_reason="Publication venue unresolved.",
    tier="T2", cluster="autopoiesis", role="Brier-cited Maturana text; its bibliographic identity must be resolved before #7 relies on it.", reading="Not read")
add("BATESON-1972", title="Steps to an Ecology of Mind", authors=[("Bateson, Gregory", A)], date=known("1972"),
    ids=[("other", "Open Library work OL486424W", "verified", lk("BATESON-1972", "openlibrary"))],
    stype="book", edition=known("Brier cites the Paladin edition (St Albans), 1972 in IR 2013 and 1973 in GL 2015 AM"),
    status="conflict", evidence=["Open Library work record (1972, 14 editions)", "Brier's two lists give different years for the same edition (BRL-IR2013, BRL-GL2015AM)"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="cybernetics", role="'Difference that makes a difference' account of information; cited in two Brier lists.", reading="Not read")
add("FOERSTER-1984", title="Observing Systems", authors=[("von Foerster, Heinz", A)], date=known("1981"),
    ids=[("other", "Open Library work OL2098990W", "verified", lk("FOERSTER-1984", "openlibrary-ta"))],
    stype="book", edition=known("Intersystems Publications; Open Library gives first publication 1981; Brier cites 1984 (SK 2015)"),
    status="conflict", evidence=["Open Library work record (first published 1981, 2 editions)", "Brier cites a 1984 date (BRL-SK2015); the edition he used is not identified"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="cybernetics", role="Second-order cybernetics: cybernetics of observing systems.", reading="Not read")
add("FOERSTER-2003", title="Understanding Understanding: Essays on Cybernetics and Cognition", authors=[("von Foerster, Heinz", A)], date=known("2003"),
    ids=[("isbn", "9780387953922", "verified", lk("FOERSTER-2003")), ("isbn", "9780387217222", "verified", lk("FOERSTER-2003"))],
    stype="book", edition=known("Springer, New York, 2003 (collected essays, e.g. 'Cybernetics of Cybernetics' pp. 283-286)"),
    status="verified", evidence=["Crossref chapter records give container title, publisher, year and ISBNs"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T2", cluster="cybernetics", role="Accessible collection of von Foerster's essays; checks Brier's citation family.", reading="Not read")
add("WIENER-1948", title="Cybernetics: Or Control and Communication in the Animal and the Machine", authors=[("Wiener, Norbert", A)], date=known("1948"),
    ids=[("other", "Open Library work OL4307531W", "verified", lk("WIENER-1961", "openlibrary"))],
    stype="book", edition=known("Brier cites the MIT Press 1963 printing (second edition first appeared 1961, not verified here)"),
    status="verified", evidence=["Open Library work record (first published 1948, 40 editions)", CITED_BY_BRIER + ": SK 2015, GL 2015 AM"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="cybernetics", role="First-order cybernetics: control and communication.", reading="Not read")
add("SPENCER-BROWN-1969", title="Laws of Form", authors=[("Spencer-Brown, George", A)], date=known("1969"),
    ids=[("other", "Open Library work OL139565W", "verified", lk("SPENCER-BROWN-1969", "openlibrary-ta"))],
    stype="book", edition=known("Brier cites the Dutton printing, New York, 1979"),
    status="verified", evidence=["Open Library work record (1969, 6 editions; a 1979 record also exists)", CITED_BY_BRIER + ": IR 2013, SK 2015"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="cybernetics", role="Calculus of distinction and re-entry used by Luhmann and Brier.", reading="Not read")
add("SHANNON-1948", title="A Mathematical Theory of Communication", authors=[("Shannon, C. E.", A)], date=known("1948-07"),
    ids=[("doi", "10.1002/j.1538-7305.1948.tb01338.x", "verified", lk("SHANNON-1948"))],
    stype="article", edition=known("Bell System Technical Journal 27(3):379-423 (part 1; part 2 is a separate record, DOI ...tb00917.x)"),
    status="verified", evidence=["Crossref record: title, author, journal, volume, issue, pages"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T2", cluster="information", role="Syntactic information on its own terms: the engineering problem that excludes meaning.", reading="Not read")
add("SHANNON-WEAVER-1949", title="The Mathematical Theory of Communication", authors=[("Shannon, Claude E.", A), ("Weaver, Warren", A)], date=known("1949"),
    ids=[("other", "Open Library work OL2296213W", "verified", lk("SHANNON-WEAVER-1949", "openlibrary-ta"))],
    stype="book", edition=known("University of Illinois Press, Urbana, 1949 (as cited by Brier, with Weaver's 'Recent contributions' essay)"),
    status="verified", evidence=["Open Library work record (1949, 4 editions)", CITED_BY_BRIER + ": SK 2015, GL 2015 AM"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="information", role="Book version Brier cites, with Weaver's essay (its levels of communication problems are commonly summarised as technical, semantic and effectiveness; not read here).", reading="Not read",
    links=[("companion_of", "SRC-REL-SHANNON-1948", "Book reprints Shannon's 1948 paper with Weaver's essay.")])
add("HOFFMEYER-1996", title="Signs of Meaning in the Universe", authors=[("Hoffmeyer, Jesper", A)], date=known("1996"),
    ids=[("other", "Open Library work OL3261764W", "verified", lk("HOFFMEYER-1996", "openlibrary"))],
    stype="book", edition=known("Indiana University Press, Bloomington, 1996 (as cited by Brier)"),
    status="verified", evidence=["Open Library work record (1996, 3 editions)", CITED_BY_BRIER + ": IR 2013, SK 2015"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T2", cluster="biosemiotics", role="Peircean biosemiotics; cited in two Brier lists.", reading="Not read",
    translation="English edition; a Danish original is likely but was not verified in R004")
add("KULL-2009", title="Theses on Biosemiotics: Prolegomena to a Theoretical Biology",
    authors=[("Kull, Kalevi", A), ("Deacon, Terrence", A), ("Emmeche, Claus", A), ("Hoffmeyer, Jesper", A), ("Stjernfelt, Frederik", A)],
    date=known("2009-06"), ids=[("doi", "10.1162/biot.2009.4.2.167", "verified", lk("KULL-2009", "crossref", 1))],
    stype="article", edition=known("Biological Theory 4(2):167-173"),
    status="conflict", evidence=["Crossref record: 2009, volume 4, issue 2, pp. 167-173", "Brier's IR 2013 list dates it 2010 while giving '4(2) 2009'; a 2011 book-chapter reprint also exists (lookup result 1)"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T2", cluster="biosemiotics", role="Programmatic statement of biosemiotics cited by Brier.", reading="Not read")

# --- T4: rivals and criticism of T2 -------------------------------------------------------------
add("BARBIERI-2008", title="Biosemiotics: a new understanding of life", authors=[("Barbieri, Marcello", A)], date=known("2008"),
    ids=[("doi", "10.1007/s00114-008-0368-x", "verified", lk("BARBIERI-2008"))],
    stype="article", edition=known("Naturwissenschaften 95(7):577-599"),
    status="verified", evidence=["Crossref record", CITED_BY_BRIER + ": IR 2013"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T4", cluster="biosemiotics", role="Rival code-biology account of biological meaning; cited in Brier's IR 2013 list (Brier's own stance to be read in #7).", reading="Not read")
add("MINGERS-2002", title="Can Social Systems Be Autopoietic? Assessing Luhmann's Social Theory", authors=[("Mingers, John", A)], date=known("2002-05"),
    ids=[("doi", "10.1111/1467-954x.00367", "verified", lk("MINGERS-2002"))],
    stype="article", edition=known("The Sociological Review 50(2):278-299"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record; the Kent repository holds no full text (ledger row 24).",
    tier="T4", cluster="autopoiesis", role="Critique of extending autopoiesis from living to social systems; relevant because Brier draws on Luhmann's social-systems theory.",
    reading="Abstract")
add("SCOTT-2004", title="Second-order cybernetics: an historical introduction", authors=[("Scott, Bernard", A)], date=known("2004-10"),
    ids=[("doi", "10.1108/03684920410556007", "verified", lk("SCOTT-2004"))],
    stype="article", edition=known("Kybernetes 33(9/10):1365-1378"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    tier="T4", cluster="cybernetics", role="Historical framing of the first/second-order distinction; context for judging Brier's use of it.",
    reading="Abstract")
add("TADDEO-FLORIDI-2005", title="Solving the symbol grounding problem: a critical review of fifteen years of research",
    authors=[("Taddeo, Mariarosaria", A), ("Floridi, Luciano", A)], date=known("2005-12"),
    ids=[("doi", "10.1080/09528130500284053", "verified", lk("TADDEO-FLORIDI-2005", "crossref", 1))],
    stype="article", edition=known("Journal of Experimental & Theoretical Artificial Intelligence 17(4):419-445; a 2021 SSRN posting also exists"),
    status="verified", evidence=["Crossref record"],
    access="metadata_only", access_reason="Metadata only; the PhilSci-Archive record page returned no readable content (ledger row 23).",
    tier="T4", cluster="grounding", role="Critical review of proposed solutions to symbol grounding.", reading="Not read")
add("KUHNE-2020", title="The Human Takes It All: Humanlike Synthesized Voices Are Perceived as Less Eerie and More Likable. Evidence From a Subjective Ratings Study",
    authors=[("Kühne, Katharina", A), ("Fischer, Martin H.", A), ("Zhou, Yuefang", A)], date=known("2020-12-16"),
    ids=[("doi", "10.3389/fnbot.2020.593732", "verified", lk("KUHNE-2020"))],
    stype="article", edition=known("Frontiers in Neurorobotics 14, article 593732"),
    status="verified", evidence=["Crossref record", "Header of the publisher PDF (ledger row 22)"],
    access="full_text_available", access_at=FETCHED, access_reason="Publisher PDF fetched and hashed; abstract and results summary read. Bytes not committed.",
    rights=cc_by("Licence statement in the publisher PDF: CC BY"),
    manifestations=[{"id": "FRONTIERS-PDF", "sha256": "4ab306db1904f12eadba34f697d0edc4965e587fa32f415bc898936ef28cebee", "extent": 15,
                     "coordinate": "file_page_1based", "location": "https://www.frontiersin.org/articles/10.3389/fnbot.2020.593732/pdf"}],
    tier="T4", cluster="anthropomorphism", role="Contrary evidence: listeners rated humanlike voices less eerie and more likable (negative case for the project's preference).",
    reading="Abstract and results summary, PDF p. 1")
add("AYLETT-2019", title="The right kind of unnatural: designing a robot voice", authors=[("Aylett, Matthew P.", A), ("Sutton, Selina Jeanne", A), ("Vazquez-Alvarez, Yolanda", A)],
    date=known("2019"), ids=[("doi", "10.1145/3342775.3342806", "verified", lk("MOORE-2017", "crossref") + " (round 2)")],
    stype="conference_paper", edition=known("Proceedings of the 1st International Conference on Conversational User Interfaces (CUI 2019)"),
    status="verified", evidence=["Crossref record (round-2 lookup and work record)"],
    access="metadata_only", access_reason="Metadata only; no abstract deposited.",
    tier="T4", cluster="anthropomorphism", role="Design position for deliberately non-human robot voices; ally of the project preference to test against KUHNE-2020.",
    reading="Not read")
add("MOORE-2019", title="A 'Canny' Approach to Spoken Language Interfaces", authors=[("Moore, Roger K.", A)], date=known("2019-08-21"),
    ids=[("url", "https://arxiv.org/abs/1908.08131", "verified", "arXiv record fetched (ledger row 17)")],
    stype="preprint", edition=known("arXiv:1908.08131, position paper"),
    status="verified", evidence=["arXiv record metadata"],
    access="abstract_only", access_at=FETCHED, access_reason="Abstract read on the arXiv record page.",
    tier="T4", cluster="anthropomorphism", role="Argues for aligning a device's visual, vocal, behavioural and cognitive affordances (the 'habitability gap'), not for maximal human likeness.",
    reading="Abstract")

# --- T3: comparator accounts ---------------------------------------------------------------------
add("DESOUZA-1993", title="The semiotic engineering of user interface languages", authors=[("de Souza, Clarisse Sieckenius", A)], date=known("1993-11"),
    ids=[("doi", "10.1006/imms.1993.1082", "verified", lk("DESOUZA-1993"))],
    stype="article", edition=known("International Journal of Man-Machine Studies 39(5):753-773"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only; no abstract deposited.",
    tier="T3", cluster="semiotic-engineering", role="Founding statement of semiotic engineering (interface as designer-to-user message).", reading="Not read")
add("PRATES-2000", title="Methods and tools: a method for evaluating the communicability of user interfaces",
    authors=[("Prates, Raquel O.", A), ("de Souza, Clarisse S.", A), ("Barbosa, Simone D. J.", A)], date=known("2000-01"),
    ids=[("doi", "10.1145/328595.328608", "verified", lk("PRATES-2000"))],
    stype="article", edition=known("Interactions 7(1):31-38"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only; the ACM interactions archive page refused the request (ledger row 26).",
    tier="T3", cluster="semiotic-engineering", role="Communicability evaluation method; nearest existing evaluation contract for RQ6.", reading="Not read")
add("DESOUZA-LEITAO-2009", title="Semiotic Engineering Methods for Scientific Research in HCI", authors=[("de Souza, Clarisse Sieckenius", A), ("Leitão, Carla Faria", A)],
    date=known("2009"), ids=[("isbn", "9783031010576", "verified", lk("DESOUZA-LEITAO-2009")), ("isbn", "9783031021855", "verified", lk("DESOUZA-LEITAO-2009")),
                             ("doi", "10.1007/978-3-031-02185-5", "candidate", "Book-level prefix of the chapter DOIs in the lookup")],
    stype="book", edition=known("Synthesis Lectures on Human-Centered Informatics (Morgan & Claypool 2009; now Springer)"),
    status="verified", evidence=["Crossref chapter records 'Semiotic Engineering Methods' (pp. 23-48) and 'Lessons Learned with Semiotic Engineering Methods'"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="semiotic-engineering", role="Methods (SIM, CEM) for semiotic-engineering research; checks overlap N09.", reading="Not read")
add("CLARK-BRENNAN-1991", title="Grounding in communication", authors=[("Clark, Herbert H.", A), ("Brennan, Susan E.", A)], date=known("1991"),
    ids=[("doi", "10.1037/10096-006", "verified", lk("CLARK-BRENNAN-1991")), ("isbn", "1557981213", "verified", lk("CLARK-BRENNAN-1991"))],
    stype="chapter", edition=known("In Resnick, Levine and Teasley (eds), Perspectives on Socially Shared Cognition, APA, pp. 127-149"),
    status="verified", evidence=["Crossref record", "Chapter header of the author-hosted scan"],
    access="full_text_available", access_at=FETCHED, access_reason="Author-hosted scan of the published chapter fetched and hashed (ledger row 20); bytes not committed.",
    manifestations=[{"id": "STANFORD-AUTHOR-COPY", "sha256": "24f58bb93eb8008b88a0ce1314d5db9fddfe3715157d4a3dc2b2f0d7fd4f33da", "extent": 12,
                     "coordinate": "file_page_1based", "location": "https://web.stanford.edu/~clark/1990s/"}],
    tier="T3", cluster="grounding", role="Grounding criterion, least collaborative effort and medium constraints (incl. audibility, reviewability) as the comparator for 'feedback' and 'persistence'.",
    reading="PDF pp. 1-2, 5, 8-9 and the closing paragraph on PDF p. 12 (two printed pages per PDF page; constraints list on printed p. 141)")
add("CLARK-SCHAEFER-1989", title="Contributing to Discourse", authors=[("Clark, Herbert H.", A), ("Schaefer, Edward F.", A)], date=known("1989-04"),
    ids=[("doi", "10.1207/s15516709cog1302_7", "verified", lk("CLARK-SCHAEFER-1989"))],
    stype="article", edition=known("Cognitive Science 13(2):259-294"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    tier="T3", cluster="grounding", role="Contribution model: presentation and acceptance phases ending in mutual belief of understanding.", reading="Abstract")
add("CLARK-1996", title="Using Language", authors=[("Clark, Herbert H.", A)], date=known("1996"),
    ids=[("other", "Open Library work OL2959069W", "verified", lk("CLARK-1996", "openlibrary-ta"))],
    stype="book", edition=known("Cambridge University Press, 1996"),
    status="verified", evidence=["Open Library work record", "Crossref holds 1998-1999 reviews naming the book as CUP 1996 (lookup CLARK-1996)"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T3", cluster="grounding", role="Language use as joint action; extended account of common ground.", reading="Not read")
add("SCHEGLOFF-1977", title="The Preference for Self-Correction in the Organization of Repair in Conversation",
    authors=[("Schegloff, Emanuel A.", A), ("Jefferson, Gail", A), ("Sacks, Harvey", A)], date=known("1977-06"),
    ids=[("doi", "10.2307/413107", "verified", lk("SCHEGLOFF-1977"))],
    stype="article", edition=known("Language 53(2):361-382"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    tier="T3", cluster="grounding", role="Repair organisation; comparator for how a machine message could be corrected or acknowledged.", reading="Abstract")
add("BRENNAN-HULTEEN-1995", title="Interaction and feedback in a spoken language system: a theoretical framework",
    authors=[("Brennan, Susan E.", A), ("Hulteen, Eric A.", A)], date=known("1995-04"),
    ids=[("doi", "10.1016/0950-7051(95)98376-h", "verified", lk("BRENNAN-HULTEEN-1995"))],
    stype="article", edition=known("Knowledge-Based Systems 8(2-3):143-151"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only; no abstract deposited and no open copy located.",
    tier="T3", cluster="grounding", role="Grounding applied to spoken system feedback; closest theory-to-design bridge for machine speech.", reading="Not read")
add("HARNAD-1990", title="The symbol grounding problem", authors=[("Harnad, Stevan", A)], date=known("1990-06"),
    ids=[("doi", "10.1016/0167-2789(90)90087-6", "verified", lk("HARNAD-1990")), ("url", "https://arxiv.org/abs/cs/9906002", "verified", "arXiv record fetched (ledger row 18)")],
    stype="article", edition=known("Physica D 42(1-3):335-346; author preprint posted to arXiv 1999"),
    status="verified", evidence=["Crossref record", "arXiv record metadata including the DOI and abstract"],
    access="abstract_only", access_at=FETCHED, access_reason="Abstract read on the arXiv record; the arXiv PDF returned HTTP 404.",
    tier="T3", cluster="grounding", role="Intrinsic meaning for a symbol system versus meaning 'parasitic on the meanings in our heads'; contrasts with interactional grounding.",
    reading="Abstract")
add("FLORIDI-2005", title="Is Semantic Information Meaningful Data?", authors=[("Floridi, Luciano", A)], date=known("2005-03"),
    ids=[("doi", "10.1111/j.1933-1592.2005.tb00531.x", "verified", lk("FLORIDI-2005", "crossref", 1))],
    stype="article", edition=known("Philosophy and Phenomenological Research 70(2):351-370"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="information", role="Philosophy-of-information account of semantic information (comparator to Brier's semiotic account of information).",
    reading="Not read")
add("KOLCHINSKY-WOLPERT-2018", title="Semantic information, autonomous agency and non-equilibrium statistical physics",
    authors=[("Kolchinsky, Artemy", A), ("Wolpert, David H.", A)], date=known("2018-10-19"),
    ids=[("doi", "10.1098/rsfs.2018.0041", "verified", lk("KOLCHINSKY-WOLPERT-2018"))],
    stype="article", edition=known("Interface Focus 8(6):20180041"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Version of record not fetched; preprint recorded separately.",
    tier="T3", cluster="information", role="Formal semantic information defined by causal necessity for a system's self-maintenance.", reading="See the preprint record")
add("KOLCHINSKY-WOLPERT-2018-ARXIV", title="Semantic information, autonomous agency, and nonequilibrium statistical physics",
    authors=[("Kolchinsky, Artemy", A), ("Wolpert, David H.", A)], date=known("2018-11-07"),
    ids=[("url", "https://arxiv.org/abs/1806.08053v3", "verified", "arXiv PDF fetched (ledger row 19)")],
    stype="preprint", edition=known("arXiv:1806.08053v3 [cond-mat.stat-mech], 19 pages"),
    status="verified", evidence=["Version label and date printed in the fetched file"],
    access="full_text_available", access_at=FETCHED, access_reason="Preprint fetched and hashed; abstract and introduction read. Bytes not committed.",
    manifestations=[{"id": "ARXIV-V3", "sha256": "8d590babb3feead54ca778a7bb4bee986afcea44f29f140135235e93336bb2ff", "extent": 19,
                     "coordinate": "file_page_1based", "location": "https://arxiv.org/pdf/1806.08053"}],
    links=[("version_of", "SRC-REL-KOLCHINSKY-WOLPERT-2018", "arXiv v3 of the Interface Focus article; differences from the version of record not checked.")],
    tier="T3", cluster="information", role="Readable version used for the definition of semantic information.", reading="Abstract and introduction, PDF p. 1")
add("EDWORTHY-1991", title="Improving Auditory Warning Design: Relationship between Warning Sound Parameters and Perceived Urgency",
    authors=[("Edworthy, Judy", A), ("Loxley, Sarah", A), ("Dennis, Ian", A)], date=known("1991-04"),
    ids=[("doi", "10.1177/001872089103300206", "verified", lk("EDWORTHY-1991"))],
    stype="article", edition=known("Human Factors 33(2):205-231"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    tier="T3", cluster="human-factors", role="Urgency as a designable function of acoustic parameters (urgency mapping, overlap N04).", reading="Abstract")
add("HELLIER-1993", title="Improving Auditory Warning Design: Quantifying and Predicting the Effects of Different Warning Parameters on Perceived Urgency",
    authors=[("Hellier, Elizabeth J.", A), ("Edworthy, Judy", A), ("Dennis, Ian", A)], date=known("1993-12"),
    ids=[("doi", "10.1177/001872089303500408", "verified", lk("HELLIER-1993"))],
    stype="article", edition=known("Human Factors 35(4):693-706"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    tier="T3", cluster="human-factors", role="Psychophysical scaling of urgency per parameter (overlap N04).", reading="Abstract")
add("EDWORTHY-HELLIER-2006", title="Alarms and human behaviour: implications for medical alarms", authors=[("Edworthy, J.", A), ("Hellier, E.", A)],
    date=known("2006-07"), ids=[("doi", "10.1093/bja/ael114", "verified", lk("EDWORTHY-HELLIER-2006"))],
    stype="article", edition=known("British Journal of Anaesthesia 97(1):12-17"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="human-factors", role="Human-factors account of alarm problems in medicine; candidate review for N04.", reading="Not read")
add("VICENTE-RASMUSSEN-1992", title="Ecological interface design: theoretical foundations", authors=[("Vicente, K. J.", A), ("Rasmussen, J.", A)],
    date=known("1992"), ids=[("doi", "10.1109/21.156574", "verified", lk("VICENTE-RASMUSSEN-1992"))],
    stype="article", edition=known("IEEE Transactions on Systems, Man, and Cybernetics 22(4):589-606"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="human-factors", role="Ecological alternative: interfaces that make work-domain constraints perceivable.", reading="Not read")
add("WICKENS-2002", title="Multiple resources and performance prediction", authors=[("Wickens, Christopher D.", A)], date=known("2002-01"),
    ids=[("doi", "10.1080/14639220210123806", "verified", lk("WICKENS-2002"))],
    stype="article", edition=known("Theoretical Issues in Ergonomics Science 3(2):159-177"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="human-factors", role="Cognitive-resource account predicting auditory versus visual time-sharing costs.", reading="Not read")
add("GAVER-1986", title="Auditory Icons: Using Sound in Computer Interfaces", authors=[("Gaver, William W.", A)], date=known("1986-06-01"),
    ids=[("doi", "10.1207/s15327051hci0202_3", "verified", lk("GAVER-1986"))],
    stype="article", edition=known("Human-Computer Interaction 2(2):167-177"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="human-factors", role="Auditory icons: mapping by everyday-sound resemblance (ecological account).", reading="Not read")
add("GAVER-1993", title="What in the World Do We Hear? An Ecological Approach to Auditory Event Perception", authors=[("Gaver, William W.", A)], date=known("1993-03"),
    ids=[("doi", "10.1207/s15326969eco0501_1", "verified", lk("GAVER-1993"))],
    stype="article", edition=known("Ecological Psychology 5(1):1-29"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="human-factors", role="Everyday versus musical listening; perceptual basis for source attribution.", reading="Not read")
add("BLATTNER-1989", title="Earcons and Icons: Their Structure and Common Design Principles", authors=[("Blattner, Meera M.", A), ("Sumikawa, Denise A.", A), ("Greenberg, Robert M.", A)],
    date=known("1989-03-01"), ids=[("doi", "10.1207/s15327051hci0401_1", "verified", lk("BLATTNER-1989"))],
    stype="article", edition=known("Human-Computer Interaction 4(1):11-44"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="human-factors", role="Earcons: abstract, learned, structured sound messages.", reading="Not read")
add("SANZSEGURA-2022", title="Design Framework for Audible Alarms: A Multidisciplinary and Integrated Approach",
    authors=[("Sanz-Segura, Rosana", A), ("Manchado-Pérez, Eduardo", A), ("Özcan, Elif", A)], date=known("2022"),
    ids=[("doi", "10.57698/v16i2.02", "verified", "Printed in the article's citation line (ledger row 13)"),
         ("url", "https://ijdesign.org/index.php/IJDesign/article/view/3911", "verified", "Fetched (ledger row 12)")],
    stype="article", edition=known("International Journal of Design 16(2):15-32"),
    status="verified", evidence=["Title, authors, affiliations, volume, issue, pages and DOI printed in the article (byline and citation line, PDF p. 1)",
                                 "The running head on PDF p. 13 lists Özcan before Manchado-Pérez; the byline order is recorded",
                                 "Crossref free-text lookup did not find it (lookup IJDESIGN-ALARM-FRAMEWORK)"],
    access="full_text_available", access_at=FETCHED, access_reason="Article PDF fetched and hashed; abstract and framework passages read; whole text searched for terms. Bytes not committed.",
    rights=cc_by("CC BY 4.0 licence link on the journal landing page (ledger row 12)"),
    manifestations=[{"id": "IJDESIGN-PDF", "sha256": "d8c9c957bd4adfe3e19e34471e696638aa5e6cf99af98f81c36f14d313429146", "extent": 18,
                     "coordinate": "file_page_1based", "location": "https://ijdesign.org/index.php/IJDesign/article/download/3911/983"}],
    tier="T3", cluster="human-factors", role="Integrated alarm design framework (event-alarm-action, criticality, priority-to-urgency); comparator for overlap N06.",
    reading="Abstract (PDF p. 1), interview quotations on silencing (PDF p. 11) and framework passages (PDF pp. 13-14); term search over all pages")
add("NASS-1994", title="Computers are social actors", authors=[("Nass, Clifford", A), ("Steuer, Jonathan", A), ("Tauber, Ellen R.", A)], date=known("1994-04-24"),
    ids=[("doi", "10.1145/191666.191703", "verified", lk("NASS-1994", "crossref", 1))],
    stype="conference_paper", edition=known("Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '94), pp. 72-78; a conference-companion item with the same title also exists (DOI 10.1145/259963.260288)"),
    status="verified", evidence=["Crossref records for both items"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="anthropomorphism", role="Social responses to computers regardless of believed nature.", reading="Not read")
add("NASS-BRAVE-2005", title="Wired for Speech: How Voice Activates and Advances the Human-Computer Relationship", authors=[("Nass, Clifford", A), ("Brave, Scott", A)],
    date=known("2005"), ids=[("other", "Open Library work OL5738442W", "verified", lk("NASS-BRAVE-2005", "openlibrary-ta"))],
    stype="book", edition=known("MIT Press, 2005"),
    status="verified", evidence=["Open Library work record (2005)", "Crossref holds 2006 reviews naming the book (lookup NASS-BRAVE-2005)"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T3", cluster="anthropomorphism", role="Voice interfaces evoke social responses (gender, personality, emotion); principal pro-social-voice comparator.", reading="Not read")
add("EPLEY-2007", title="On seeing human: A three-factor theory of anthropomorphism", authors=[("Epley, Nicholas", A), ("Waytz, Adam", A), ("Cacioppo, John T.", A)],
    date=known("2007"), ids=[("doi", "10.1037/0033-295x.114.4.864", "verified", lk("EPLEY-2007"))],
    stype="article", edition=known("Psychological Review 114(4):864-886"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="anthropomorphism", role="When people anthropomorphise; separates listener tendency from machine features.", reading="Not read")
add("MORI-2012", title="The Uncanny Valley", authors=[("Mori, Masahiro", A), ("MacDorman, Karl F.", "translator"), ("Kageki, Norri", "translator")],
    date=known("2012-06"), ids=[("doi", "10.1109/mra.2012.2192811", "verified", lk("MORI-2012"))],
    stype="article", edition=known("IEEE Robotics & Automation Magazine 19(2):98-100 ('From the Field')"),
    status="candidate", evidence=["Crossref record lists Mori, MacDorman and Kageki", "Translator roles and the original Japanese publication are not stated in the lookup and were not verified"],
    access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="anthropomorphism", role="Human likeness and affinity are non-monotonic; tested in voices by KUHNE-2020.", reading="Not read",
    translation="English translation of an earlier Japanese essay (per common citation; not verified in R004)")
add("SEABORN-2021", title="Voice in Human-Agent Interaction: A Survey", authors=[("Seaborn, Katie", A), ("Miyake, Norihisa P.", A), ("Pennefather, Peter", A), ("Otake-Matsuura, Mihoko", A)],
    date=known("2021-05-03"), ids=[("doi", "10.1145/3386867", "verified", lk("SEABORN-2021"))],
    stype="review", edition=known("ACM Computing Surveys 54(4):1-43"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record; the institutional repository file returned HTTP 500 (ledger row 21).",
    tier="T3", cluster="anthropomorphism", role="Survey of agent voice research; principal overlap check for N07.", reading="Abstract")
add("CLARK-FISCHER-2022", title="Social robots as depictions of social agents", authors=[("Clark, Herbert H.", A), ("Fischer, Kerstin", A)], date=known("2022-03-28"),
    ids=[("doi", "10.1017/s0140525x22000668", "verified", lk("CLARK-FISCHER-2023"))],
    stype="article", edition=known("Behavioral and Brain Sciences 46 (target article; first online 2022)"),
    status="verified", evidence=["Crossref record and deposited abstract"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    tier="T3", cluster="anthropomorphism", role="Depiction account: people treat social robots as depictions of agents (base scene, depiction proper, scene depicted).",
    reading="Abstract")
add("VARELA-1991", title="The Embodied Mind: Cognitive Science and Human Experience", authors=[("Varela, Francisco J.", A), ("Thompson, Evan", A), ("Rosch, Eleanor", A)],
    date=known("1991"), ids=[("other", "Open Library work OL15207300W", "candidate", lk("VARELA-1991", "openlibrary-ta"))],
    stype="book", edition=known("MIT Press (year as commonly cited; Open Library records give 1992 and 2016 for English works and list a French translation)"),
    status="conflict", evidence=["Open Library: English work records dated 1992 and 2016 and a French work 'L'inscription corporelle de l'esprit' (lookups VARELA-1991)"],
    access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T3", cluster="embodiment", role="Enactive account developed from autopoietic theory, which Brier also cites (Maturana and Varela 1980 in all three lists).", reading="Not read",
    translation="Original English; a French translation exists as a separate Open Library work")
add("PICARD-1997", title="Affective Computing", authors=[("Picard, Rosalind W.", A)], date=known("1997"),
    ids=[("other", "Open Library work OL2710137W", "verified", lk("PICARD-1997", "openlibrary-ta"))],
    stype="book", edition=known("MIT Press, 1997"),
    status="verified", evidence=["Open Library work record (1997, 3 editions)"], access="metadata_only", access_reason="Catalogue metadata only.",
    tier="T3", cluster="embodiment", role="Programme for machines that recognise and express emotion; opposing design stance to the project preference.", reading="Not read")

# --- T5: semiotics of auditory display -----------------------------------------------------------
add("OSWALD-2012", title="Non-Speech Audio-Semiotics: A Review and Revision of Auditory Icon and Earcon Theory", authors=[("Oswald, David", A)], date=known("2012"),
    ids=[("url", "https://www.htw-berlin.de/forschung/online-forschungskatalog/publikationen/publikation?eid=4775", "verified", "Catalogue page fetched (ledger row 14)")],
    stype="conference_paper", edition=known("Proceedings of the 18th International Conference on Auditory Display (ICAD 2012), as listed in the HTW Berlin catalogue"),
    status="candidate", evidence=["HTW Berlin research catalogue record and a repository search title (R005 run A-W1-FR)", "Not in Crossref (lookup NSAS-ICAD)"],
    access="unavailable", access_at=FETCHED, access_reason="The author's PDF link no longer resolves and the ICAD 2012 proceedings page returned HTTP 500 (ledger rows 28-29).",
    tier="T5", cluster="auditory-semiotics", role="Prior semiotic review of auditory icons and earcons; overlap check N08.", reading="Not read")
add("AUDITORY-SIGNS-REVIEW", title="A review-based conceptual analysis of auditory signs and their design", authors=[], date=missing("unknown", "Not shown in the search result"),
    ids=[("url", "https://repository.gatech.edu/entities/publication/4d76fff4-8093-4fe0-b0f9-d489503049bf", "candidate", "Search-result URL (run G-26); page not readable without JavaScript")],
    stype="conference_paper", edition=missing("unknown", "Venue presumed ICAD from the repository; not verified"),
    status="candidate", evidence=[], access="not_attempted", access_reason="Title known only from a search result.",
    tier="T5", cluster="auditory-semiotics", role="Second semiotic review of auditory signs; overlap check N08.", reading="Not read")
add("JEKOSCH-2005", title="Assigning Meaning to Sounds — Semiotics in the Context of Product-Sound Design", authors=[("Jekosch, Ute", A)], date=known("2005"),
    ids=[("doi", "10.1007/3-540-27437-5_8", "verified", lk("JEKOSCH-2005")), ("isbn", "354022162X", "verified", lk("JEKOSCH-2005"))],
    stype="chapter", edition=known("In Communication Acoustics (Springer), pp. 193-221; year from the ISBN-era series, not printed in the lookup"),
    status="candidate", evidence=["Crossref chapter record (no issued date)"], access="metadata_only", access_reason="Metadata only; a related proceedings paper URL returned HTTP 404 (ledger row 25).",
    tier="T5", cluster="auditory-semiotics", role="Semiotic account of meaning in product sound.", reading="Not read")
add("TUURI-EEROLA-2012", title="Formulating a Revised Taxonomy for Modes of Listening", authors=[("Tuuri, Kai", A), ("Eerola, Tuomas", A)], date=known("2012-06"),
    ids=[("doi", "10.1080/09298215.2011.614951", "verified", lk("TUURI-EEROLA-2012"))],
    stype="article", edition=known("Journal of New Music Research 41(2):137-152"),
    status="verified", evidence=["Crossref record"], access="metadata_only", access_reason="Metadata only.",
    tier="T5", cluster="auditory-semiotics", role="Modes of listening (causal, semantic, reduced and revisions) for situated interpretation of sound.", reading="Not read")
add("HERMANN-2008", title="Taxonomy and Definitions for Sonification and Auditory Display", authors=[("Hermann, Thomas", A)], date=known("2008-06"),
    ids=[("url", "https://www.icad.org/Proceedings/2008/Hermann2008.pdf", "verified", "Fetched (ledger row 16)")],
    stype="conference_paper", edition=known("Proceedings of the 14th International Conference on Auditory Display, Paris, 24-27 June 2008"),
    status="verified", evidence=["Title, author, affiliation and venue printed in the file"],
    access="full_text_available", access_at=FETCHED, access_reason="ICAD PDF fetched and hashed; abstract, introduction and definition read. Bytes not committed.",
    manifestations=[{"id": "ICAD-PDF", "sha256": "7a07958fe2d4e1cc12e2fca76d45df3602def7d06536054fdd31fe41e358365a", "extent": 8,
                     "coordinate": "file_page_1based", "location": "https://www.icad.org/Proceedings/2008/Hermann2008.pdf"}],
    tier="T5", cluster="auditory-semiotics", role="Boundary definition of sonification versus other auditory display (system-boundary concept).", reading="Abstract, introduction and the definition with conditions C1-C3, PDF pp. 1-2")
add("OZCAN-2012", title="Basic Semantics of Product Sounds", authors=[("Özcan, Elif", A), ("van Egmond, René", A)], date=known("2012"),
    ids=[("url", "https://ijdesign.org/index.php/IJDesign/article/view/957", "verified", "Fetched (ledger row 15)")],
    stype="article", edition=known("International Journal of Design 6(2)"),
    status="verified", evidence=["Title, authors, volume and issue on the journal page"], access="full_text_available", access_at=FETCHED,
    access_reason="Open-access article on the journal site; not fetched or read.",
    rights=cc_by("CC BY 4.0 licence link on the journal landing page (ledger row 15)"),
    tier="T5", cluster="auditory-semiotics", role="Semantic categories listeners assign to product sounds.", reading="Not read")

# --- Added from the round-3/round-4 identity checks of negative-case and access finds ----------
TRAUM_SHA = "7e8fb773e84c0c738f4195f3f442c4f47d779a9f941810c131faf8b3fb9626c1"
LOOKED3 = "2026-10-13T07:06:38Z"
LOOKED4 = "2026-10-13T07:10:21Z"


def lk3(key, item=0, rnd=3):
    return f"Round-{rnd} lookup {key} result {item + 1}, research/searches/related/exports/lookups/"


add("BECKER-2025", title="Influence of Robots’ Voice Naturalness on Trust and Compliance",
    authors=[(n, A) for n in ("Becker, Dennis", "Braach, Lukas", "Clasmeier, Lennart", "Kaufmann, Teresa", "Ong, Oskar", "Ahrens, Kyra",
                              "Gäde, Connor", "Strahl, Erik", "Fu, Di", "Wermter, Stefan")], date=known("2025-01-28"),
    ids=[("doi", "10.1145/3706066", "verified", lk3("VOICE-NATURALNESS-TRUST"))],
    stype="article", edition=known("ACM Transactions on Human-Robot Interaction 14(2):1-25"),
    status="verified", evidence=["Crossref record (round-3 lookup) and single-DOI work record"],
    access="abstract_only", access_at="2026-10-13T07:07:38Z",
    access_reason="Abstract read from the Crossref work record; the publisher PDF request was refused with HTTP 403 (ledger row 36).",
    rights=cc_by("Crossref work record licence field: CC BY 4.0"),
    tier="T4", cluster="anthropomorphism",
    role="Contrary evidence: a natural robot voice was perceived as safer and increased reliance on repeated incorrect advice, with no direct trust effect (abstract). Empirical study: candidate for Track E screening in #6.",
    reading="Abstract")
add("ROMEO-2025", title="The Effect of Voice and Repair Strategy on Trust Formation and Repair in Human-Robot Interaction",
    authors=[(n, A) for n in ("Romeo, Marta", "Torre, Ilaria", "Le Maguer, Sébastien", "Sleat, Alexander", "Cangelosi, Angelo", "Leite, Iolanda")],
    date=known("2025-02-19"), ids=[("doi", "10.1145/3711938", "verified", lk3("VOICE-REPAIR-TRUST"))],
    stype="article", edition=known("ACM Transactions on Human-Robot Interaction 14(2):1-22"),
    status="verified", evidence=["Crossref record (round-3 lookup) and single-DOI work record"],
    access="abstract_only", access_at="2026-10-13T07:07:38Z",
    access_reason="Abstract read from the Crossref work record; the publisher PDF request was refused with HTTP 403 (ledger row 36).",
    rights={"status": "redistribution_permitted", "reason": "CC BY-NC-SA 4.0 per the Crossref licence field: reuse with attribution, non-commercial, share-alike.",
            "evidence": known("Crossref work record licence field: CC BY-NC-SA 4.0")},
    tier="T4", cluster="anthropomorphism",
    role="Contrary and mixed evidence: in-game behaviour showed more trust in a state-of-the-art synthetic voice than in the default robot voice while questionnaires indicated the opposite; human repair strategies also worked (abstract). Track E candidate for #6.",
    reading="Abstract")
add("ROMEO-2023", title="Putting Robots in Context: Challenging the Influence of Voice and Empathic Behaviour on Trust",
    authors=[(n, A) for n in ("Romeo, Marta", "Torre, Ilaria", "Le Maguer, Sébastien", "Cangelosi, Angelo", "Leite, Iolanda")],
    date=known("2023-08-28"), ids=[("doi", "10.1109/ro-man57019.2023.10309631", "verified", lk3("VOICE-NATURALNESS-TRUST", 1))],
    stype="conference_paper", edition=known("2023 32nd IEEE International Conference on Robot and Human Interactive Communication (RO-MAN), pp. 2045-2050"),
    status="verified", evidence=["Crossref record (round-3 lookup); Crossref gives the third author's name as 'Maguer, Sébastien Le'"],
    access="metadata_only", access_reason="Metadata only; no abstract deposited.",
    tier="T4", cluster="anthropomorphism", role="Further voice-and-trust study by the same group; title signals a challenge to voice effects on trust. Track E candidate for #6.",
    reading="Not read")
add("MULLER-2014", title="Which symbol grounding problem should we try to solve?", authors=[("Müller, Vincent C.", A)], date=known("2014-09-02"),
    ids=[("doi", "10.1080/0952813x.2014.940143", "verified", lk3("WHICH-SGP"))],
    stype="article", edition=known("Journal of Experimental & Theoretical Artificial Intelligence 27(1):73-78 (Crossref issued date is the online date)"),
    status="verified", evidence=["Crossref record (round-3 lookup)"], access="metadata_only", access_reason="Metadata only; no abstract deposited.",
    tier="T4", cluster="grounding", role="Objection to the framing of symbol grounding; tests whether Harnad's problem is the right one for machine communication.",
    reading="Not read")
add("ZHOU-2025", title="Biosemiotics, code biology, and operational interpretation", authors=[("Zhou, Liqian", A)], date=known("2025-02-01"),
    ids=[("doi", "10.1515/css-2025-2003", "verified", lk3("CODE-BIOLOGY-OPERATIONAL"))],
    stype="article", edition=known("Chinese Semiotic Studies 21(1):39-60"),
    status="verified", evidence=["Crossref record (round-3 lookup) and single-DOI work record"],
    access="abstract_only", access_reason="Abstract read from the Crossref work record.",
    rights=cc_by("Crossref work record licence field: CC BY 4.0"),
    tier="T4", cluster="biosemiotics",
    role="Takes the code-biology critiques of biosemiotics as reasonable and proposes 'operational interpretation' to reconcile them (abstract); tests Brier's claims about interpretation below the human level.",
    reading="Abstract")
add("TRAUM-CONTRIB", title="On Clark and Schaefer’s Contribution Model and its applicability to Human-Computer Collaboration",
    authors=[("Traum, David R.", A)], date=missing("unknown", "No date or venue printed in the file; the file name on the author's site contains '98'"),
    ids=[("url", "https://people.ict.usc.edu/~traum/Papers/traum98clark.pdf", "verified", "Fetched 2026-10-13 (ledger row 37)")],
    stype="other", edition=missing("unknown", "Short paper; venue not printed in the file"),
    status="candidate", evidence=["Title, author and affiliation (UMIACS, University of Maryland) printed on PDF p. 1"],
    access="full_text_available", access_at="2026-10-13T07:07:45Z",
    access_reason="Author-hosted PDF fetched and hashed; all argument sections read. Bytes not committed.",
    manifestations=[{"id": "AUTHOR-PDF", "sha256": TRAUM_SHA, "extent": 6, "coordinate": "file_page_1based",
                     "location": "https://people.ict.usc.edu/~traum/Papers/traum98clark.pdf"}],
    tier="T4", cluster="grounding",
    role="Criticism of the contribution model as a design model: not an on-line model, no way to tell a contribution's current state, graded evidence poorly ordered (PDF pp. 2-4).",
    reading="PDF pp. 1-4 (abstract, sections 1-4); references not read")
add("PARMENTIER-2009", title="Troubles with trichotomies: Reflections on the utility of Peirce's sign trichotomies for social analysis",
    authors=[("Parmentier, Richard J.", A)], date=known("2009-01"),
    ids=[("doi", "10.1515/semi.2009.070", "verified", lk3("SEMIOTICA-2009-070", 0, 4))],
    stype="article", edition=known("Semiotica (Crossref volume 2009, issue 177)"),
    status="verified", evidence=["Crossref record (round-4 DOI filter lookup)"], access="metadata_only", access_reason="Metadata only.",
    tier="T4", cluster="peirce", role="Reflections on how useful Peirce's sign trichotomies are for social analysis (title); tests fixed sign-class assignments (concept K07).",
    reading="Not read")
add("DEJESUS-2015", title="Autopoietic enactivism, phenomenology and the deep continuity between life and mind", authors=[("De Jesus, Paulo", A)],
    date=known("2015-02-01"), ids=[("doi", "10.1007/s11097-015-9414-2", "verified", lk3("AUTOPOIETIC-ENACTIVISM", 0, 4))],
    stype="article", edition=known("Phenomenology and the Cognitive Sciences 15(2):265-289 (Crossref issued date is the online date)"),
    status="verified", evidence=["Crossref record (round-4 lookup)"], access="metadata_only", access_reason="Metadata only.",
    tier="T4", cluster="embodiment", role="Examines the life-mind continuity thesis of autopoietic enactivism; relevant to Brier's use of autopoiesis, to be read in #7.",
    reading="Not read")
add("BRANDT-1994", title="Meaning and the machine: Toward a semiotics of interaction", authors=[("Brandt, Per Aage", A)], date=known("1994-03-25"),
    ids=[("doi", "10.1017/cbo9780511720369.008", "verified", lk3("MEANING-AND-MACHINE", 0, 4)), ("isbn", "9780521419956", "verified", lk3("MEANING-AND-MACHINE", 0, 4))],
    stype="chapter", edition=known("In The Computer as Medium, Cambridge University Press, pp. 128-140 (editors not in the lookup)"),
    status="verified", evidence=["Crossref chapter record (round-4 lookup)"], access="metadata_only", access_reason="Metadata only.",
    tier="T3", cluster="semiotic-engineering", role="Early semiotics of human-computer interaction outside de Souza's school; comparator for interface meaning.",
    reading="Not read")
add("BANSAL-2024", title="Challenges in Human-Agent Communication",
    authors=[(n, A) for n in ("Bansal, Gagan", "Vaughan, Jennifer Wortman", "Amershi, Saleema", "Horvitz, Eric", "Fourney, Adam", "Mozannar, Hussein", "Dibia, Victor", "Weld, Daniel S.")],
    date=known("2024-11-28"), ids=[("url", "https://arxiv.org/abs/2412.10380v1", "verified", lk3("HAC-CHALLENGES") + " (arXiv API)")],
    stype="preprint", edition=known("arXiv:2412.10380v1 [cs.HC]"),
    status="verified", evidence=["arXiv API record (round-3 lookup)"], access="abstract_only", access_at=LOOKED3,
    access_reason="Abstract read from the arXiv API record.",
    tier="T3", cluster="grounding", role="Applies a communication-grounding perspective to generative AI agents and lists twelve communication challenges in both directions (abstract).",
    reading="Abstract")
add("MILDNER-2024", title="Listening to the Voices: Describing Ethical Caveats of Conversational User Interfaces According to Experts and Frequent Users",
    authors=[(n, A) for n in ("Mildner, Thomas", "Cooney, Orla", "Meck, Anna-Maria", "Bartl, Marion", "Savino, Gian-Luca", "Doyle, Philip R.", "Garaialde, Diego",
                              "Clark, Leigh", "Sloan, John", "Wenig, Nina", "Malaka, Rainer", "Niess, Jasmin")],
    date=known("2024-01-26"), ids=[("url", "https://arxiv.org/abs/2401.14746v1", "verified", lk3("CUI-ETHICAL-CAVEATS") + " (arXiv API)"),
                                   ("doi", "10.1145/3613904.3642542", "candidate", "Version-of-record DOI stated in the arXiv author comment (CHI '24); not resolved")],
    stype="preprint", edition=known("arXiv:2401.14746v1, author's version of a CHI '24 paper"),
    status="verified", evidence=["arXiv API record including the author comment"], access="abstract_only", access_at=LOOKED3,
    access_reason="Abstract read from the arXiv API record.",
    tier="T4", cluster="anthropomorphism", role="Interview study of ethical caveats in conversational user interfaces (risks that exploit trust); ethics comparator for human-like machine speech.",
    reading="Abstract")
add("FERRARIO-2026", title="A Scoping Review of the Ethical Perspectives on Anthropomorphising Large Language Model-Based Conversational Agents",
    authors=[(n, A) for n in ("Ferrario, Andrea", "Vinay, Rasita", "Casserini, Matteo", "Facchini, Alessandro")],
    date=known("2026-01-14"), ids=[("url", "https://arxiv.org/abs/2601.09869v2", "verified", lk3("ANTHRO-LLM-ETHICS") + " (arXiv API)")],
    stype="preprint", edition=known("arXiv:2601.09869v2 (updated 2026-06-02); author comment names FAccT '26"),
    status="verified", evidence=["arXiv API record"], access="abstract_only", access_at=LOOKED3, access_reason="Abstract read from the arXiv API record.",
    tier="T4", cluster="anthropomorphism",
    role="Scoping review: ethical concerns (deception, overreliance) and claimed benefits of anthropomorphic agents; reports divergent operationalisations (abstract).",
    reading="Abstract")
add("MURPHY-2006", title="A Semiotic Approach to the Design of Non-speech Sounds",
    authors=[(n, A) for n in ("Murphy, Emma", "Pirhonen, Antti", "McAllister, Graham", "Yu, Wai")], date=known("2006"),
    ids=[("doi", "10.1007/11821731_12", "verified", lk3("NSS-USE-SCENARIO", 2)), ("isbn", "9783540375951", "verified", lk3("NSS-USE-SCENARIO", 2))],
    stype="chapter", edition=known("In Haptic and Audio Interaction Design (HAID 2006), Lecture Notes in Computer Science, Springer, pp. 121-132"),
    status="verified", evidence=["Crossref chapter record returned by the round-3 query for a different title"], access="metadata_only",
    access_reason="Metadata only; the Sussex repository entry in the search results says the files are not publicly available.",
    tier="T5", cluster="auditory-semiotics", role="Semiotic design approach for non-speech interface sounds; overlap check N08.", reading="Not read")
add("SANZSEGURA-2024", title="Guiding design students to sound-driven design from the base camp of semiotics",
    authors=[("Sanz-Segura, Rosana", A), ("Manchado-Pérez, Eduardo", A)], date=known("2024-06-23"),
    ids=[("doi", "10.21606/drs.2024.855", "verified", lk3("SOUND-DRIVEN-DESIGN"))],
    stype="conference_paper", edition=known("Proceedings of DRS2024: Boston (Design Research Society)"),
    status="verified", evidence=["Crossref record (round-3 lookup)"], access="metadata_only", access_reason="Metadata only.",
    tier="T5", cluster="auditory-semiotics", role="Semiotics as a basis for teaching sound-driven design, by two authors of SANZSEGURA-2022; overlap check N06/N08.",
    reading="Not read")
add("NSS-USE-SCENARIO", title="Non-speech sounds as elements of a use scenario: A semiotic perspective", authors=[], date=missing("unknown", "Not shown in the search results"),
    ids=[("url", "https://repository.gatech.edu/entities/publication/e508ee28-0a98-42d9-9dc0-30ec85f1dd5d", "candidate", "Search-result URL (runs G-22, G-25); repository API returned HTTP 500 (ledger row 33)")],
    stype="conference_paper", edition=missing("unknown", "Venue presumed ICAD from the repository collection; not verified"),
    status="candidate", evidence=[], access="not_attempted", access_reason="Title known only from search results; Crossref did not find it (round-3 lookup NSS-USE-SCENARIO).",
    tier="T5", cluster="auditory-semiotics", role="Third semiotic treatment of interface sounds found in the ICAD collection; overlap check N08.", reading="Not read")

EXISTING = {
    "SRC-NOV-DESOUZA-2005": ("T3", "semiotic-engineering", "Core semiotic engineering monograph (R002 record; metadata only)."),
    "SRC-NOV-VALENTE-2009": ("T3", "semiotic-engineering", "Semiotic engineering applied to non-visual (aural/tactile) mobile interfaces (R002 record; abstract only)."),
    "SRC-NOV-NAM-2010": ("T5", "auditory-semiotics", "Peircean classification of interface sounds (R002 record; abstract only)."),
    "SRC-NOV-VRIEND-2025": ("T5", "auditory-semiotics", "Audiovisual semiotics of uncertainty (R002 record; tool-mediated full text)."),
}

# Lookup key -> (route section, result index, source key) for resolving lookup occurrences.
LOOKUP_MATCH = {
    "PEIRCE-CP": 0, "PEIRCE-EP2": 0, "PEIRCE-W": 0, "MATURANA-VARELA-1980": None, "MATURANA-1988": 1, "BATESON-1972": 0,
    "FOERSTER-2003": None, "WIENER-1961": 0, "SHANNON-1948": 0, "HOFFMEYER-1996": 0, "KULL-2009": 1, "BARBIERI-2008": 0,
    "DESOUZA-1993": 0, "PRATES-2000": 0, "DESOUZA-LEITAO-2009": None, "CLARK-BRENNAN-1991": 0, "CLARK-SCHAEFER-1989": 0,
    "SCHEGLOFF-1977": 0, "BRENNAN-HULTEEN-1995": 0, "HARNAD-1990": 0, "TADDEO-FLORIDI-2005": 1, "FLORIDI-2005": 1,
    "KOLCHINSKY-WOLPERT-2018": 0, "EDWORTHY-1991": 0, "HELLIER-1993": 0, "EDWORTHY-HELLIER-2006": 0, "VICENTE-RASMUSSEN-1992": 0,
    "WICKENS-2002": 0, "GAVER-1986": 0, "GAVER-1993": 0, "BLATTNER-1989": 0, "NASS-1994": 1, "EPLEY-2007": 0, "MORI-2012": 0,
    "SEABORN-2021": 0, "CLARK-FISCHER-2023": 0, "KUHNE-2020": 0, "MINGERS-2002": 0, "SCOTT-2004": 0, "JEKOSCH-2005": 0,
    "TUURI-EEROLA-2012": 0,
}
ROUND2_MATCH = {"LUHMANN-1995": 0, "FOERSTER-1984": 0, "PICARD-1997": 0, "SPENCER-BROWN-1969": 0, "SHANNON-WEAVER-1949": 0,
                "NASS-BRAVE-2005": 0, "CLARK-1996": 0, "SHORT-2007": 0, "MOORE-2017": 0, "VARELA-1991": 0}
LOOKUP_TO_SOURCE = {"MATURANA-1988": "MATURANA-1988B", "WIENER-1961": "WIENER-1948", "CLARK-FISCHER-2023": "CLARK-FISCHER-2022",
                    "MOORE-2017": "AYLETT-2019"}

# Brier reference entries that name an R004 source record (regex on the entry start).
BRL_MATCH = [
    (r"^Peirce, C\.\s?S\.? (\[?1931|\(1931|\[1994|\[ 1931)", "PEIRCE-CP"), (r"^Peirce, C\.\s?S\.? \[?\(?1994", "PEIRCE-CP"),
    (r"^Peirce, C\.\s?S\.? \(1998\)", "PEIRCE-EP2"), (r"^Peirce, C\.\s?S\.? \(1982", "PEIRCE-W"),
    (r"^Short, T\.\s?L\. \(2007\)", "SHORT-2007"), (r"^Luhmann, N\. \(1995\)", "LUHMANN-1995"),
    (r"^Maturana, H\.?\s?(&|,) ?Varela, F\. \(1980\)", "MATURANA-VARELA-1980"),
    (r"^Maturana, H\.?R?\.? \(1988a\)", "MATURANA-1988A"), (r"^Maturana, H\.?R?\.? \(1988b\)", "MATURANA-1988B"),
    (r"^Bateson, G\. \(197[23]\)", "BATESON-1972"), (r"^Foerster, H\. von \(1984\)", "FOERSTER-1984"),
    (r"^Wiener, N\. \(1963\)", "WIENER-1948"), (r"^Spencer-Brown, G\. \(1979\)", "SPENCER-BROWN-1969"),
    (r"^Shannon, C\. \(1949\)", "SHANNON-WEAVER-1949"), (r"^Weaver, W\. \(1949\)", "SHANNON-WEAVER-1949"),
    (r"^Hoffmeyer, J\. \(1996\)", "HOFFMEYER-1996"), (r"^Kull, K\.", "KULL-2009"), (r"^Barbieri, M\. \(2008\)", "BARBIERI-2008"),
]


ROUND3_MATCH = {"VOICE-NATURALNESS-TRUST": {0: "BECKER-2025", 1: "ROMEO-2023"}, "VOICE-REPAIR-TRUST": {0: "ROMEO-2025"},
                "WHICH-SGP": {0: "MULLER-2014"}, "CODE-BIOLOGY-OPERATIONAL": {0: "ZHOU-2025", 1: "SRC-BRIER-2013-JOSLYN"},
                "NSS-USE-SCENARIO": {2: "MURPHY-2006"}, "SOUND-DRIVEN-DESIGN": {0: "SANZSEGURA-2024"}, "HAC-CHALLENGES": {0: "BANSAL-2024"},
                "CUI-ETHICAL-CAVEATS": {0: "MILDNER-2024"}, "ANTHRO-LLM-ETHICS": {0: "FERRARIO-2026"}}
ROUND4_MATCH = {"SEMIOTICA-2009-070": {0: "PARMENTIER-2009"}, "MEANING-AND-MACHINE": {0: "BRANDT-1994"}, "AUTOPOIETIC-ENACTIVISM": {0: "DEJESUS-2015"}}
# Lookup key -> source key when the lookup was named differently from the adjudicated source.
LOOKUP_CANDIDATE = {"MATURANA-1988": ["MATURANA-1988A", "MATURANA-1988B"], "WIENER-1961": ["WIENER-1948"], "CLARK-FISCHER-2023": ["CLARK-FISCHER-2022"],
                    "MOORE-2017": ["AYLETT-2019"], "IJDESIGN-ALARM-FRAMEWORK": ["SANZSEGURA-2022"], "NSAS-ICAD": ["OSWALD-2012"],
                    "REVIEW-AUDITORY-SIGNS-ICAD": ["AUDITORY-SIGNS-REVIEW"], "OZCAN-2008": ["OZCAN-2012"],
                    "KOLCHINSKY-WOLPERT-2018": ["KOLCHINSKY-WOLPERT-2018", "KOLCHINSKY-WOLPERT-2018-ARXIV"],
                    "VOICE-NATURALNESS-TRUST": ["BECKER-2025", "ROMEO-2023"], "VOICE-REPAIR-TRUST": ["ROMEO-2025"], "WHICH-SGP": ["MULLER-2014"],
                    "CODE-BIOLOGY-OPERATIONAL": ["ZHOU-2025"], "NSS-USE-SCENARIO": ["NSS-USE-SCENARIO", "MURPHY-2006"],
                    "SOUND-DRIVEN-DESIGN": ["SANZSEGURA-2024"], "HAC-CHALLENGES": ["BANSAL-2024"], "CUI-ETHICAL-CAVEATS": ["MILDNER-2024"],
                    "ANTHRO-LLM-ETHICS": ["FERRARIO-2026"], "SEMIOTICA-2009-070": ["PARMENTIER-2009"], "MEANING-AND-MACHINE": ["BRANDT-1994"],
                    "AUTOPOIETIC-ENACTIVISM": ["DEJESUS-2015"]}

# Sources reached as known items rather than through a logged search.
KNOWN_ITEM = {"ATKIN-SEP": "known-item fetch of the standard open reference entry (ACCESS-LEDGER-R004 row 11; candidates_r004.py route 'web')"}

# Web-search occurrences adjudicated to a source: (run label, ordinal, source key or existing record ID, text the title or URL must contain).
WEB_MATCH = [
    ("G-01", 4, "DESOUZA-LEITAO-2009", "978-3-031-02185-5"), ("G-01", 5, "DESOUZA-LEITAO-2009", "Semiotic engineering methods for scientific research"),
    ("G-01", 10, "SRC-NOV-DESOUZA-2005", "The Semiotic Engineering of Human-Computer Interaction"),
    ("G-02", 1, "MINGERS-2002", "kar.kent.ac.uk/3907"),
    ("G-03", 2, "TADDEO-FLORIDI-2005", "solving the symbol grounding problem a critical review"),
    ("G-03", 3, "TADDEO-FLORIDI-2005", "Solving the symbol grounding problem: a critical review"),
    ("G-03", 4, "TADDEO-FLORIDI-2005", "Solving the symbol grounding problem: a critical review"),
    ("G-03", 6, "MULLER-2014", "Which symbol grounding problem should we try to solve?"),
    ("G-03", 10, "MULLER-2014", "Which symbol grounding problem should we try to solve?"),
    ("G-06", 3, "BECKER-2025", "Voice Naturalness on Trust and Compliance"), ("G-06", 4, "BECKER-2025", "10.1145%2F3706066"),
    ("G-06", 7, "ROMEO-2025", "the effect of voice and repair strategy on trust formation"),
    ("G-07", 2, "ZHOU-2025", "css-2025-2003"), ("G-07", 4, "SRC-BRIER-2015-PBMB", "Can Biosemiotics be a"),
    ("G-07", 6, "SRC-BRIER-2015-PBMB", "can biosemiotics be a science"),
    ("G-08", 1, "KOLCHINSKY-WOLPERT-2018-ARXIV", "arxiv.org/pdf/1806.08053"), ("G-08", 8, "KOLCHINSKY-WOLPERT-2018-ARXIV", "1806.08053"),
    ("G-09", 9, "SEABORN-2021", "Voice in Human-Agent Interaction: A Survey"), ("G-09", 10, "SEABORN-2021", "Voice in Human-Agent Interaction: A Survey"),
    ("G-10", 2, "MOORE-2019", "1908.08131"), ("G-10", 5, "AYLETT-2019", "3342775.3342806"), ("G-10", 7, "AYLETT-2019", "3342775.3342806"),
    ("G-10", 9, "AYLETT-2019", "The right kind of unnatural"),
    ("G-11", 2, "OZCAN-2012", "IJDesign/article/download/957"), ("G-11", 3, "OZCAN-2012", "Basic Semantics of Product Sounds"),
    ("G-11", 6, "OZCAN-2012", "Basic Semantics of Product Sounds"),
    ("G-12", 1, "OSWALD-2012", "Non-Speech Audio-Semiotics"), ("G-12", 3, "OSWALD-2012", "publikationen/publikation?eid"),
    ("G-12", 4, "AUDITORY-SIGNS-REVIEW", "A review-based conceptual analysis of auditory signs"),
    ("G-14", 6, "SHANNON-WEAVER-1949", "Shannon Weaver 1949"),
    ("G-15", 1, "BANSAL-2024", "Challenges in Human-Agent Communication"), ("G-15", 4, "TRAUM-CONTRIB", "traum98clark.pdf"),
    ("G-16", 1, "MILDNER-2024", "Listening to the Voices"), ("G-16", 5, "FERRARIO-2026", "2601.09869"), ("G-16", 6, "FERRARIO-2026", "2601.09869"),
    ("G-19", 4, "SEABORN-2021", "Voice in Human-Agent Interaction: A Survey"), ("G-19", 8, "SEABORN-2021", "Voice in Human-Agent Interaction: A Survey"),
    ("G-20", 3, "CLARK-BRENNAN-1991", "web.stanford.edu/%7Eclark/1990s/Clark"),
    ("G-21", 1, "BRENNAN-HULTEEN-1995", "Interaction and feedback in a spoken language system: a theoretical framework"),
    ("G-21", 2, "BRENNAN-HULTEEN-1995", "Interaction and feedback in a spoken language system: a theoretical framework"),
    ("G-21", 4, "BRENNAN-HULTEEN-1995", "interaction and feedback in a spoken language system a theoretica"),
    ("G-22", 1, "OSWALD-2012", "publikationen/publikation?eid"), ("G-22", 3, "OSWALD-2012", "Non-Speech Audio-Semiotics"),
    ("G-22", 4, "MURPHY-2006", "A_Semiotic_Approach_to_the_Design_of_Non"), ("G-22", 7, "NSS-USE-SCENARIO", "Non-speech sounds as elements of a use scenario"),
    ("G-22", 10, "MURPHY-2006", "11821731"),
    ("G-23", 1, "SANZSEGURA-2022", "IJDesign/article/view/3911"), ("G-23", 2, "SANZSEGURA-2022", "design framework for audible alarms"),
    ("G-23", 3, "SANZSEGURA-2022", "IJDesign/article/download/3911"), ("G-23", 4, "SANZSEGURA-2022", "Design Framework for Audible Alarms"),
    ("G-23", 7, "SANZSEGURA-2024", "Guiding design students to sound-driven design"), ("G-23", 8, "SANZSEGURA-2024", "Guiding design students to sound-driven design"),
    ("G-23", 9, "SANZSEGURA-2024", "Guiding design students to sound-driven design"),
    ("G-24", 1, "PRATES-2000", "methods and tools a method for evaluating the communicability"),
    ("G-25", 1, "OSWALD-2012", "Non-Speech Audio-Semiotics"), ("G-25", 3, "OSWALD-2012", "publikationen/publikation?eid"),
    ("G-25", 7, "NSS-USE-SCENARIO", "Non-speech sounds as elements of a use scenario"), ("G-25", 9, "MURPHY-2006", "A_Semiotic_Approach_to_the_Design_of_Non"),
    ("G-26", 1, "AUDITORY-SIGNS-REVIEW", "A review-based conceptual analysis of auditory signs"), ("G-26", 2, "OSWALD-2012", "Non-Speech Audio-Semiotics"),
    ("G-27", 4, "BRANDT-1994", "meaning-and-the-machine-toward-a-semiotics-of-interaction"),
    ("G-28", 6, "DEJESUS-2015", "Autopoietic enactivism, phenomenology and the deep continuity"),
    ("G-31", 1, "OSWALD-2012", "Non-Speech Audio-Semiotics"), ("G-31", 6, "PARMENTIER-2009", "semi.2009.070"),
    ("G-31", 8, "SRC-NOV-NAM-2010", "semi.2010.060"),
]
# Web occurrences that look like empirical Track E studies; flagged for #6 screening, not resolved here.
TRACK_E_HANDOFF = ([("G-05", n) for n in (1, 2, 3, 4, 5, 7, 8, 9, 10)] + [("G-29", n) for n in (2, 4, 6, 7, 9)]
                   + [("G-30", n) for n in (2, 3, 4, 6, 9)])


def record(rid, kind, data, basis=(), factual="discovery"):
    return {"schema_version": 1, "id": rid, "kind": kind, "synthetic": False, "issue": 4,
            "revisions": [{"rev": 1, "at": AT, "actor": ACTOR, "basis": list(basis), "data": data, "factual_status": factual}]}


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> int:
    out = {}
    src_ids = {}
    for key, entry in S.items():
        rid = f"SRC-REL-{key}"
        src_ids[key] = rid
        data = entry["record"]
        basis = [ref(l["source_ref"]["id"]) for l in data["family_links"]]
        out[f"{SRC_DIR}/{rid}.json"] = record(rid, "source", data, basis, "source_reported")
    run_ids = []

    # Existing records (other lanes) that R004 occurrences resolve to.
    def target_ref(target):
        if target.startswith("SRC-"):
            for lane in ("research/sources/brier/records", "research/novelty/records"):
                path = ROOT / lane / f"{target}.json"
                if path.exists():
                    return {"id": target, "rev": len(json.loads(path.read_text(encoding="utf-8"))["revisions"])}
            raise SystemExit(f"unknown existing record {target}")
        return ref(src_ids[target])

    provenance = {}

    def note(target, run_id):
        rid = target if target.startswith("SRC-") else src_ids[target]
        provenance.setdefault(rid, set()).add(run_id)

    # Web searches (Track G discovery, negative cases, access).
    web = json.loads((ROOT / WEB).read_text(encoding="utf-8"))
    web_ref = known({"path": WEB, "sha256": sha(WEB)})
    web_match = {(label, n): (target, expect) for label, n, target, expect in WEB_MATCH}
    handoff = set(TRACK_E_HANDOFF)
    seen = set()
    for batch in web["batches"]:
        for run in batch["runs"]:
            rid = "SRCH-R004-" + run["label"].replace("-", "")
            run_ids.append(rid)
            out[f"{SRCH_DIR}/{rid}.json"] = record(rid, "search_run", {
                "lane": "related", "protocol_version": "v1", "mode": "production", "status": "partial",
                "platform": "General web search engine via the agent's WebSearch tool", "interface": "WebSearch tool, standard mode, US-only results",
                "query": run["query"], "filters": ["No user-set filters; tool default US-only results"],
                "coverage": {"start": missing("unknown", "The engine does not state its index coverage"), "end": missing("unknown", "The engine does not state its index coverage")},
                "started_at": known(run["called_at"]), "finished_at": known(batch["window_end"]),
                "reported_count": missing("not_reported", "The engine reports no total hit count"),
                "retrieved_count": len(run["results"]), "export": web_ref,
                "pagination": {"complete": False, "detail": "One page of top results only."}, "failures": [],
                "boundary": (f"Track G {run['purpose']} search for the {run['cluster']} cluster (protocol v1 §7"
                             + (".3 negative case" if run["purpose"] == "negative" else "") + "). Discovery only; no coverage is claimed."),
            })
            for res in run["results"]:
                hid = f"HIT-R004-{run['label'].replace('-', '')}-{res['ordinal']:02d}"
                data = {"search_ref": ref(rid), "ordinal": res["ordinal"], "raw_metadata": f"{res['title']} | {res['url']}",
                        "returned_identifiers": [{"scheme": "url", "value": res["url"]}], "status": "unresolved",
                        "resolution_reason": "Publication identity not checked for this occurrence."}
                basis = [ref(rid)]
                key = (run["label"], res["ordinal"])
                if key in web_match:
                    target, expect = web_match[key]
                    if expect.lower() not in (res["title"] + " " + res["url"]).lower():
                        raise SystemExit(f"web match {key} does not contain {expect!r}")
                    seen.add(key)
                    tref = target_ref(target)
                    data.update(status="resolved", source_ref=tref,
                                resolution_reason="Title or stable identifier in the result matches the source record; the page itself was opened only where the access ledger says so.")
                    basis.append(tref)
                    note(target, rid)
                elif key in handoff:
                    seen.add(key)
                    data["resolution_reason"] = ("Looks like an empirical study relevant to Track E; flagged for #6 screening and the #5 search. "
                                                 "Identity not checked in R004.")
                out[f"{SRCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", data, basis)
    missing_keys = (set(web_match) | handoff) - seen
    if missing_keys:
        raise SystemExit(f"web matches not found: {sorted(missing_keys)}")

    # Identity lookups (Crossref, Open Library, arXiv API).
    manifest = json.loads((ROOT / LOOKUPS).read_text(encoding="utf-8"))
    lookup_ref = known({"path": LOOKUPS, "sha256": sha(LOOKUPS)})
    first = {k: ({v: LOOKUP_TO_SOURCE.get(k, k)} if v is not None else {}) for k, v in LOOKUP_MATCH.items()}
    second = {k: {v: LOOKUP_TO_SOURCE.get(k, k)} for k, v in ROUND2_MATCH.items()}
    platforms = {"crossref": "Crossref REST API", "crossref-doi": "Crossref REST API (DOI filter)", "openlibrary": "Open Library search API",
                 "openlibrary-ta": "Open Library search API (title and author fields)", "arxiv": "arXiv API (export.arxiv.org)"}
    filters = {"crossref": "rows=3", "crossref-doi": "filter=doi, rows=3", "openlibrary": "limit=5", "openlibrary-ta": "limit=5", "arxiv": "id_list"}
    for section, prefix, matches in (("lookups", "LK", first), ("round2", "LK2", second), ("round3", "LK3", ROUND3_MATCH), ("round4", "LK4", ROUND4_MATCH)):
        for key, entry in manifest[section].items():
            rid = f"SRCH-R004-{prefix}-{key}"
            run_ids.append(rid)
            raw_bytes = (ROOT / entry["file"]).read_bytes()
            if hashlib.sha256(raw_bytes).hexdigest() != entry["sha256"]:
                raise SystemExit(f"hash mismatch for {entry['file']}")
            if entry["route"] == "arxiv":
                items = [{"arxiv": e} for e in re.findall(r"<entry>(.*?)</entry>", raw_bytes.decode("utf-8"), re.S)]
            else:
                body = json.loads(raw_bytes)
                items = body["message"]["items"] if entry["route"].startswith("crossref") else body.get("docs", [])
            out[f"{SRCH_DIR}/{rid}.json"] = record(rid, "search_run", {
                "lane": "related", "protocol_version": "v1", "mode": "production", "status": "completed",
                "platform": platforms[entry["route"]],
                "interface": "HTTPS request from the workspace shell; response kept unchanged", "query": entry["query"],
                "filters": [filters[entry["route"]]],
                "coverage": {"start": missing("not_applicable", "Known-item lookup"), "end": missing("not_applicable", "Known-item lookup")},
                "started_at": known(entry["at"]), "finished_at": known(entry["at"]),
                "reported_count": missing("not_reported", "Total-results count not used for a known-item lookup"),
                "retrieved_count": len(items), "export": lookup_ref,
                "pagination": {"complete": True, "detail": "Known-item lookup: only the top results were requested and all returned items are recorded."},
                "failures": [], "boundary": f"Identity lookup for R004 candidate {key}; file {entry['file']} (sha256 {entry['sha256']}).",
            }, factual="discovery")
            for cand in LOOKUP_CANDIDATE.get(key, [key]):
                if cand in src_ids:
                    note(cand, rid)
            for n, item in enumerate(items, 1):
                hid = f"HIT-R004-{prefix}-{key}-{n:02d}"
                if entry["route"] == "arxiv":
                    e = item["arxiv"]
                    ident = re.search(r"<id>(.*?)</id>", e).group(1)
                    raw = f"{' '.join(re.search(r'<title>(.*?)</title>', e, re.S).group(1).split())} | {ident}"
                    idents = [{"scheme": "url", "value": ident}]
                elif entry["route"].startswith("crossref"):
                    raw = f"{(item.get('title') or [''])[0]} | {(item.get('container-title') or [''])[0]} | {item.get('DOI')}"
                    idents = [{"scheme": "doi", "value": item["DOI"]}] if item.get("DOI") else []
                else:
                    raw = f"{item.get('title')} | {', '.join(item.get('author_name', []) or [])} | {item.get('first_publish_year')} | {item.get('key')}"
                    idents = [{"scheme": "other", "value": "Open Library " + item["key"]}]
                data = {"search_ref": ref(rid), "ordinal": n, "raw_metadata": raw, "returned_identifiers": idents,
                        "status": "unresolved", "resolution_reason": "Returned by the lookup but not the adjudicated match."}
                basis = [ref(rid)]
                target = matches.get(key, {}).get(n - 1)
                if target is not None and (target in src_ids or target.startswith("SRC-")):
                    tref = target_ref(target)
                    data.update(status="resolved", source_ref=tref,
                                resolution_reason="Adjudicated match: title, author and year agree with the source record (R004 source map).")
                    basis.append(tref)
                    note(target, rid)
                out[f"{SRCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", data, basis)

    # Brier's reference lists (T2 dependency tracing).
    brl = json.loads((ROOT / BRL).read_text(encoding="utf-8"))
    brl_ref = known({"path": BRL, "sha256": sha(BRL)})
    t2_counts = {}
    author_counts = {}
    labels = [lst["label"] for lst in brl["lists"]]
    for lst in brl["lists"]:
        rid = "SRCH-R004-" + lst["label"].replace("-", "")
        run_ids.append(rid)
        out[f"{SRCH_DIR}/{rid}.json"] = record(rid, "search_run", {
            "lane": "related", "protocol_version": "v1", "mode": "production", "status": "completed",
            "platform": f"Reference list of {lst['source_record']}, parsed from the downloaded file",
            "interface": f"Direct HTTPS download (sha256 {lst['sha256']}, {lst['bytes']} bytes, {lst['pages']} pages) and pdftotext",
            "query": "Every entry of the article's reference list", "filters": ["None"],
            "coverage": {"start": missing("not_applicable", "Reference list"), "end": missing("not_applicable", "Reference list")},
            "started_at": known(brl["downloaded"]["start"]), "finished_at": known(brl["downloaded"]["end"]),
            "reported_count": missing("not_reported", "No entry count printed"),
            "retrieved_count": len(lst["entries"]), "export": brl_ref,
            "pagination": {"complete": True, "detail": "Whole reference section parsed; entry splitting is heuristic and some running heads remain inside entries."},
            "failures": [], "boundary": "Track G tier T2 tracing: which works Brier actually cites (protocol v1 §7.1). Citation is not evidence that a passage depends on the work.",
        }, [ref(lst["source_record"])])
        for e in lst["entries"]:
            m = re.match(r"\s*([A-Z][A-Za-zÀ-ÿ'\-]+(?: [a-z]+)?)", e["text"])
            author = m.group(1) if m else "(unparsed)"
            author_counts.setdefault(author, dict.fromkeys(labels, 0))[lst["label"]] += 1
            hid = f"HIT-R004-{lst['label'].replace('-', '')}-{e['ordinal']:03d}"
            data = {"search_ref": ref(rid), "ordinal": e["ordinal"], "raw_metadata": e["text"], "returned_identifiers": [],
                    "status": "unresolved", "resolution_reason": "Brier reference entry not matched to an R004 source record."}
            basis = [ref(rid)]
            for pattern, key in BRL_MATCH:
                if re.search(pattern, e["text"]):
                    data.update(status="resolved", source_ref=ref(src_ids[key]),
                                resolution_reason="Entry names this work (author, year, title); the edition Brier cites may differ (see the source record).")
                    basis.append(ref(src_ids[key]))
                    t2_counts[key] = t2_counts.get(key, 0) + 1
                    note(key, rid)
                    break
            out[f"{SRCH_DIR}/hits/{hid}.json"] = record(hid, "search_hit", data, basis)

    # Derived first-author tally of Brier's reference lists.
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["first_author", *labels, "total", "lists_citing"])
    for author, counts in sorted(author_counts.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])):
        w.writerow([author, *[counts[l] for l in labels], sum(counts.values()), sum(1 for l in labels if counts[l])])
    (ROOT / AUTHORS).write_text(buf.getvalue(), encoding="utf-8")

    # Derived source map.
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["source_record", "tier", "cluster", "role", "metadata_status", "access_status", "reading_extent", "rights", "language_and_translation",
                "brier_list_entries", "search_provenance", "role_basis"])
    for key, entry in S.items():
        d = entry["record"]
        rid = src_ids[key]
        if not provenance.get(rid):
            if key not in KNOWN_ITEM:
                raise SystemExit(f"{rid} has no search provenance")
            provenance[rid] = {KNOWN_ITEM[key]}
        w.writerow([rid, entry["tier"], entry["cluster"], entry["role"], d["metadata_status"], d["access_status"], entry["reading"],
                    d["rights"]["status"], entry["translation"], t2_counts.get(key, 0), " ".join(sorted(provenance[rid])),
                    "orientation from title, catalogue data or background; source-check before use" if entry["reading"] == "Not read"
                    else "passages listed under reading_extent"])
    for rid, (tier, cluster, role) in EXISTING.items():
        w.writerow([rid, tier, cluster, role, "see record", "see record", "see record", "see record", "see record", 0,
                    " ".join(sorted(provenance.get(rid, set()))) or "R002 novelty audit (see record)", "see record"])
    (ROOT / SOURCE_MAP).write_text(buf.getvalue(), encoding="utf-8")

    out[f"{SRC_DIR}/AID-R004-RELATED-CORPUS.json"] = record("AID-R004-RELATED-CORPUS", "assistance", {
        "subtype": "assistance",
        "task": ("Build the Track G related-theory corpus under protocol v1 §7: trace Brier's dependencies from his own reference lists, "
                 "identify comparator, reception and auditory-semiotics sources, verify identity with Crossref and Open Library, run negative-case searches, "
                 "fetch lawful open copies of key comparators, and map concepts for #8."),
        "input_refs": [ref("SRC-BRIER-2013-IR"), ref("SRC-NOV-BRIER-2015"), ref("SRC-BRIER-2015-GL-AM")],
        "output_refs": [ref(i) for i in sorted(src_ids.values())] + [ref(i) for i in run_ids],
        "artifacts": [WEB, LOOKUPS, BRL, LEDGER, SOURCE_MAP, AUTHORS, CONCEPT_MAP, MEMO],
        "verification_steps": [
            "Every identifier comes from a retained Crossref or Open Library response, a fetched page or the source file itself; DOIs were not typed from memory.",
            "Lookup responses were adjudicated by title, author and year; mismatches and conflicts are kept as candidate or conflict status.",
            "Reading statements in the memo are limited to the passages listed as read for each source; everything else is marked as not read.",
        ],
        "limitations": ("Single agent; purposive sampling only; most sources identified but not read; no human check. "
                        "Concept-map correspondences are the agent's hypotheses for #8, not findings."),
        "status": "performed", "performed_at": known(AT),
        "independence": "Single executing agent. Not a human check and not independent of the work it describes.",
    }, [ref("SRC-BRIER-2013-IR"), ref("SRC-NOV-BRIER-2015"), ref("SRC-BRIER-2015-GL-AM")], "researcher_interpretation")

    for path, row in sorted(out.items()):
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dumps(row), encoding="utf-8")
    print(f"wrote {len(out)} records; sources {len(src_ids)}; runs {len(run_ids)}; Brier-list matches {t2_counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
