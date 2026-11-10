"""R005: once-only source-byte probe for already-registered Stevens et al. 2009.
A green suite is NOT evidence of source access. Read MHAC_R005_STEVENS2009
from the exact PR-head Actions job; source observations are ephemeral, no
original article bytes or participant data are committed here.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

DOI = "10.2478/v10053-008-0064-6"
PMCID = "PMC2865004"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2865004/fullTextXML"
BRANCH = "mhac-r005/stevens2009-open-article-20261110"
MAX_BYTES = 3_000_000
HIT = "HIT-R005R-C1LOAD-EQ1-02138@2"
SOURCE = "SRC-R006-E-STEVENS-INFORMATIVE@1"


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def classify_original(data, url):
    """Analyze only a real response body, never infer full-text from metadata."""
    row = {"request_url": url, "byte_count": len(data),
           "sha256": hashlib.sha256(data).hexdigest()}
    if not data.lstrip().startswith(b"<"):
        row["result"] = "BLOCKED_NOT_XML"
        return row
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        row["result"] = "BLOCKED_INVALID_XML"
        row["parse_error"] = str(exc)[:120]
        return row
    dois = ["".join(e.itertext()).strip().lower()
            for e in root.findall(".//article-id[@pub-id-type='doi']")]
    row["observed_article_dois"] = dois
    row["article_root_tag"] = root.tag
    if DOI.lower() not in dois or root.tag != "article":
        row["result"] = "BLOCKED_WRONG_ARTICLE"
        return row
    titles = []
    for sec in root.findall(".//body//sec"):
        tt = sec.find("title")
        if tt is not None:
            label = " ".join("".join(tt.itertext()).split())
            if label:
                titles.append(label)
    row["section_headings"] = titles[:80]
    row["fulltext_structure"] = bool(root.find(".//body") is not None and
                                     root.find(".//back") is not None)
    row["section_inventory_only"] = True
    row["license_links"] = sorted(set(
        e.attrib.get("{http://www.w3.org/1999/xlink}href", "")
        for e in root.findall(".//license")
        if e.attrib.get("{http://www.w3.org/1999/xlink}href")))
    row["result"] = ("ARTICLE_XML_BODY_RECEIVED" if row["fulltext_structure"]
                     else "BLOCKED_ARTICLE_BODY_INCOMPLETE")
    return row


def direct_probe():
    result = {"started_utc": utc(), "source": SOURCE,
              "representative_hit": HIT, "doi": DOI,
              "pmcid": PMCID, "original_endpoint": URL,
              "access_basis": "unauthenticated public Europe PMC full-text XML API",
              "no_rights_or_redistribution_attested": True,
              "actor_type": "AI-operated GitHub Actions tool",
              "human_or_scientific_screen": False,
              "empirical_study_or_sample_admitted": False,
              "requested_full_article_edition": "Europe PMC NLM XML full-text rendering; not publisher PDF"}
    try:
        req = urllib.request.Request(URL, headers={
            "User-Agent": "MHAC-R005-source-integrity/2026-11-10",
            "Accept-Encoding": "identity"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            result.update({"http_status": resp.status, "final_url": resp.url,
                           "http_date": resp.headers.get("Date"),
                           "content_type": resp.headers.get("Content-Type"),
                           "response_opened_utc": utc()})
            raw = resp.read(MAX_BYTES + 1)
            result["read_completed_utc"] = utc()
        if len(raw) > MAX_BYTES:
            result["result"] = "BLOCKED_OVERSIZE"
        else:
            result.update(classify_original(raw, URL))
    except Exception as exc:
        result["result"] = "BLOCKED_" + type(exc).__name__
        result["error_excerpt"] = str(exc)[:160]
        result["read_completed_utc"] = utc()
    return result


class TestStevensOriginalSource(unittest.TestCase):
    def test_original_identity_and_ownership(self):
        self.assertEqual(DOI, "10.2478/v10053-008-0064-6")
        self.assertTrue(URL.endswith("/PMC2865004/fullTextXML"))
        self.assertEqual(SOURCE, "SRC-R006-E-STEVENS-INFORMATIVE@1")
        self.assertEqual(HIT, "HIT-R005R-C1LOAD-EQ1-02138@2")

    def test_reject_wrong_article_and_non_xml(self):
        x = classify_original(b"not a pdf or xml", URL)
        self.assertEqual(x["result"], "BLOCKED_NOT_XML")
        wrong = b"<article><front><article-id pub-id-type='doi'>10.0000/fake</article-id></front><body/><back/></article>"
        self.assertEqual(classify_original(wrong, URL)["result"], "BLOCKED_WRONG_ARTICLE")

    def test_reject_metadata_only_promotion(self):
        d = b"<article><front><article-id pub-id-type='doi'>10.2478/v10053-008-0064-6</article-id></front></article>"
        self.assertEqual(classify_original(d, URL)["result"], "BLOCKED_ARTICLE_BODY_INCOMPLETE")

    def test_live_ephemeral_original_body_probe(self):
        # Do not turn all subsequent mainline CI into live-network requests.
        if not (os.getenv("GITHUB_ACTIONS") == "true" and
                os.getenv("GITHUB_HEAD_REF") == BRANCH):
            self.skipTest("one R005 PR-head original endpoint attempt only")
        row = direct_probe()
        print("MHAC_R005_STEVENS2009=" + json.dumps(row, sort_keys=True), flush=True)
        # The presence of this marker is evidence of an attempt, NOT a success.
        self.assertFalse(row["human_or_scientific_screen"])
        self.assertFalse(row["empirical_study_or_sample_admitted"])


if __name__ == "__main__":
    unittest.main()
