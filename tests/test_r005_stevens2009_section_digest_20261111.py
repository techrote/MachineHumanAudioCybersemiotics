"""R005 bounded original Stevens 2009 JATS section-byte/text fingerprints.

Only a pull-request Actions run with the exact issue-scoped branch makes one
unauthenticated public source request. All other tests use synthetic fixtures.
No source original XML is committed; no human or R006 screening is performed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import unittest
import urllib.request
import xml.etree.ElementTree as ET

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML"
DOI = "10.2478/v10053-008-0064-6"
PMCID = "PMC2865004"
SOURCE_ID = "SRC-R006-E-STEVENS-INFORMATIVE@1"
HIT_ID = "HIT-R005R-C1LOAD-EQ1-02138@2"
BRANCH = "mhac-r005/stevens2009-section-pins-20261111"
MAX_BYTES = 2_000_000


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def normalized_text(node):
    return " ".join(" ".join(node.itertext()).split())


def inspect_original(raw):
    """Hash actual bytes and bounded Method/Results passages, without inference."""
    if len(raw) < 120 or len(raw) > MAX_BYTES:
        raise ValueError("Original response outside bounded byte range")
    if b"<!ENTITY" in raw.upper():
        raise ValueError("Entity declarations are not accepted")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("Original response is not valid JATS XML") from exc
    if root.tag != "article":
        raise ValueError("Original XML root is not article")
    dois = ["".join(n.itertext()).strip().lower() for n in
            root.findall("./front/article-meta/article-id[@pub-id-type='doi']")]
    if DOI not in dois:
        raise ValueError("Original XML publication DOI mismatch")
    if root.find("./body") is None or root.find("./back") is None:
        raise ValueError("Original article body/back absent")

    sections = []
    for index, sec in enumerate(root.findall("./body/sec"), start=1):
        t = sec.find("title")
        if t is None:
            continue
        heading = normalized_text(t)
        if heading not in ("Method", "Results"):
            continue
        # Each digest covers the complete actual top-level section including
        # nested subsection text, not just the heading or abstract metadata.
        body_text = normalized_text(sec)
        nested = [normalized_text(n) for n in sec.findall("./sec/title")]
        sections.append({
            "original_xpath": f"/article/body/sec[{index}]",
            "heading": heading,
            "nested_section_headings": nested,
            "normalized_text_sha256": hashlib.sha256(body_text.encode("utf-8")).hexdigest(),
            "normalized_text_characters": len(body_text),
            "paragraph_elements": len(sec.findall(".//p")),
            "reading": "machine inventory and full-section text fingerprint; not human semantic review",
        })
    if sorted(s["heading"] for s in sections) != ["Method", "Results"]:
        raise ValueError("Complete Method and Results top-level sections not found")
    method = next(s for s in sections if s["heading"] == "Method")
    results = next(s for s in sections if s["heading"] == "Results")
    if not {"Participants", "Stimuli", "Procedure"} <= set(method["nested_section_headings"]):
        raise ValueError("Original Method participant/stimulus/procedure boundaries absent")
    if not {"Learning Phase", "Test Phase"} <= set(results["nested_section_headings"]):
        raise ValueError("Original Results phase boundaries absent")
    if any(s["normalized_text_characters"] < 100 or s["paragraph_elements"] < 1 for s in sections):
        raise ValueError("Section has insufficient original body text")
    return {
        "source_id": SOURCE_ID,
        "representative_hit_id": HIT_ID,
        "edition": "Europe PMC JATS/NLM original-article XML (not publisher PDF)",
        "doi_in_article": DOI,
        "original_response_sha256": hashlib.sha256(raw).hexdigest(),
        "original_response_bytes": len(raw),
        "method_results": sections,
        "direct_original_fulltext_section_fingerprints": True,
        "numeric_outcome_extraction": False,
        "human_or_second_assessor": False,
        "rights_or_retention_approved": False,
        "bytes_retained": False,
        "source_manifestation_registered": False,
        "publication_study_experiment_sample_admissions": 0,
    }


def one_live_request():
    receipt = {
        "started_utc": utc_now(),
        "request_url": URL,
        "actor": "GPT-6 R005 on exact-branch GitHub Actions",
        "access_basis": "public unauthenticated Europe PMC full-text API",
        "source_id": SOURCE_ID,
        "representative_hit_id": HIT_ID,
        "frozen_publication_cutoff": "2026-10-04",
        "does_not_change_r006": True,
    }
    try:
        req = urllib.request.Request(URL, headers={
            "User-Agent": "MHAC-R005-section-fingerprint/2026-11-11",
            "Accept-Encoding": "identity"})
        with urllib.request.urlopen(req, timeout=25) as response:
            receipt.update({
                "http_status": response.status,
                "response_url": response.url,
                "http_date": response.headers.get("Date"),
                "content_type": response.headers.get("Content-Type"),
                "opened_utc": utc_now(),
            })
            if response.status != 200 or response.url != URL:
                raise ValueError("Original source HTTP/URL mismatch")
            if "xml" not in response.headers.get("Content-Type", "").lower():
                raise ValueError("Response is not XML")
            raw = response.read(MAX_BYTES + 1)
            receipt["finished_utc"] = utc_now()
        receipt.update(inspect_original(raw))
        receipt["status"] = "ORIGINAL_METHOD_RESULTS_SECTION_FINGERPRINTS_OBSERVED"
    except Exception as exc:
        receipt.update({
            "status": "SOURCE_ATTEMPT_BLOCKED",
            "error_type": type(exc).__name__,
            "error_detail": str(exc)[:250],
            "finished_utc": utc_now(),
        })
    return receipt


SYNTHETIC = b"""<?xml version="1.0"?>
<article><front><article-meta>
<article-id pub-id-type="doi">10.2478/v10053-008-0064-6</article-id>
</article-meta></front><body>
<sec><title>Introduction</title><p>synthetic filler text</p></sec>
<sec><title>Method</title>
<sec><title>Participants</title><p>synthetic example only, not a real human study. Synthetic example only, not a real study.</p></sec>
<sec><title>Stimuli</title><p>synthetic warning patterns invented for validating structural parsing and text fingerprints.</p></sec>
<sec><title>Procedure</title><p>synthetic sequence for test use only, never a reported actual experiment.</p></sec>
</sec>
<sec><title>Results</title>
<sec><title>Learning Phase</title><p>synthetic output without participant results, for software validation only.</p></sec>
<sec><title>Test Phase</title><p>synthetic output without measurements, for negative controls only.</p></sec>
</sec></body><back><ref-list/></back></article>"""


class TestStevensSectionPins(unittest.TestCase):
    def test_synthetic_original_structure(self):
        result = inspect_original(SYNTHETIC)
        self.assertEqual([s["heading"] for s in result["method_results"]], ["Method", "Results"])
        self.assertTrue(all(len(s["normalized_text_sha256"]) == 64 for s in result["method_results"]))
        self.assertFalse(result["bytes_retained"])
        self.assertFalse(result["human_or_second_assessor"])
        self.assertEqual(result["publication_study_experiment_sample_admissions"], 0)

    def test_hash_binds_original_bytes_and_complete_sections(self):
        before = inspect_original(SYNTHETIC)
        altered = SYNTHETIC.replace(b"synthetic warning patterns", b"altered synthetic patterns")
        after = inspect_original(altered)
        self.assertNotEqual(before["original_response_sha256"], after["original_response_sha256"])
        self.assertNotEqual(before["method_results"][0]["normalized_text_sha256"],
                            after["method_results"][0]["normalized_text_sha256"])
        self.assertEqual(before["method_results"][1]["normalized_text_sha256"],
                         after["method_results"][1]["normalized_text_sha256"])

    def test_mismatched_doi_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "DOI mismatch"):
            inspect_original(SYNTHETIC.replace(DOI.encode(), b"10.1111/another-work"))

    def test_metadata_only_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "body/back"):
            inspect_original(SYNTHETIC.split(b"<body>")[0] + b"</article>")

    def test_missing_method_participant_boundary_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "participant"):
            inspect_original(SYNTHETIC.replace(b"<title>Participants</title>", b"<title>Other</title>"))

    def test_missing_results_phase_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "phase"):
            inspect_original(SYNTHETIC.replace(b"<title>Test Phase</title>", b"<title>Other</title>"))

    def test_missing_method_or_results_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Complete Method"):
            inspect_original(SYNTHETIC.replace(b"<title>Results</title>", b"<title>Claims</title>"))

    def test_standard_jats_doctype_is_permitted_without_entity_expansion(self):
        # An ordinary Europe PMC/JATS DOCTYPE is not an unsafe XML entity.
        header = b'<!DOCTYPE article PUBLIC "-//NLM//DTD Journal Publishing DTD//EN" "JATS.dtd">'
        xml = SYNTHETIC.replace(b"<article>", header + b"\n<article>", 1)
        self.assertEqual(inspect_original(xml)["doi_in_article"], DOI)

    def test_entity_declaration_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Entity"):
            inspect_original(b"<!DOCTYPE article [<!ENTITY bad 'x'>]>" + SYNTHETIC)

    def test_no_network_except_exact_branch_pr_head(self):
        if not (os.environ.get("GITHUB_ACTIONS") == "true"
                and os.environ.get("GITHUB_HEAD_REF") == BRANCH):
            self.skipTest("live original-source request only on issue-scoped PR Actions")
        receipt = one_live_request()
        print("MHAC_R005_STEVENS_SECTION_PINS=" + json.dumps(receipt, sort_keys=True), flush=True)
        # Green CI proves reporting structure, not successful acquisition or science.
        self.assertFalse(receipt["does_not_change_r006"] is False)
        self.assertEqual(receipt["frozen_publication_cutoff"], "2026-10-04")


if __name__ == "__main__":
    unittest.main()
