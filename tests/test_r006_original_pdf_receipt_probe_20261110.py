"""One-time R006 provenance diagnostic; DO NOT MERGE as a permanent test.

Public author/institutional PDF byte retrieval on a GitHub-hosted ephemeral runner.
No source bytes are committed or uploaded. No full reading or screening occurs.
This file is scoped to a draft-only diagnostic PR, to be closed after checkpoint.
"""
import datetime
import io
import importlib
import tempfile
import sys
import hashlib
import json
import os
import re
import shutil
import subprocess
import unittest
from urllib import request

URLS = [
    ("becker_2025", "https://www2.informatik.uni-hamburg.de/wtm/publications/2025/BBCKOAGSFW25/3706066.pdf"),
    ("romeo_2025_attempt_1", "https://research.chalmers.se/publication/546010/file/546010_Fulltext.pdf"),
    ("romeo_2025_attempt_2", "https://research.chalmers.se/publication/546010/file/546010_Fulltext.pdf"),
]
MAX_BYTES = 30 * 1024 * 1024

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds")

def observe(source_name, url):
    row = {"source": source_name, "requested_url": url, "started_utc": utcnow(),
           "mechanism": "GitHub Actions Ubuntu / Python urllib public HTTPS GET",
           "copyright": "No file bytes are deposited; content/license review is separate"}
    try:
        req = request.Request(
            url,
            headers={"User-Agent": "MHAC-provenance-recovery/2026-11-10 (public-source research)",
                     "Accept": "application/pdf", "Accept-Encoding": "identity"})
        with request.urlopen(req, timeout=16) as resp:
            row["http_status"] = resp.status
            row["final_url"] = resp.url
            row["headers"] = {k: resp.headers.get(k) for k in
                              ("Date", "Content-Type", "Content-Length", "ETag", "Last-Modified",
                               "Content-Disposition") if resp.headers.get(k) is not None}
            row["response_opened_utc"] = utcnow()
            buf = resp.read(MAX_BYTES + 1)
            row["read_completed_utc"] = utcnow()
        if len(buf) > MAX_BYTES:
            row["result"] = "BLOCKED: response exceeds 30MiB safety cap"
            return row
        row["byte_count"] = len(buf)
        row["content_sha256"] = hashlib.sha256(buf).hexdigest()
        row["is_pdf_header"] = buf[:5] == b"%PDF-"
        if not row["is_pdf_header"]:
            row["result"] = "BLOCKED: body is not original PDF bytes"
            return row
        # Pin the parser installed on this *ephemeral* runner, for a real
        # page-count derived from the exact bytes just SHA-256 hashed.
        try:
            from pypdf import PdfReader, __version__ as pypdf_version
        except ImportError:
            vendor = tempfile.mkdtemp(prefix="mhac_pdf_parser_")
            install = subprocess.run([sys.executable, "-m", "pip", "install",
                                      "--disable-pip-version-check", "--quiet",
                                      "--target", vendor, "pypdf==6.1.1"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=35)
            row["pypdf_install_exit"] = install.returncode
            if install.returncode:
                row["pypdf_install_error"] = install.stderr.decode("utf-8", "replace")[-280:]
                PdfReader = None
            else:
                sys.path.insert(0, vendor)
                importlib.invalidate_caches()
                try:
                    from pypdf import PdfReader, __version__ as pypdf_version
                except ImportError as exc:
                    row["pypdf_import_error"] = str(exc)[:240]
                    PdfReader = None
        if PdfReader is not None:
            try:
                reader = PdfReader(io.BytesIO(buf), strict=False)
                row["pdf_pages"] = len(reader.pages)
                row["pypdf_version"] = pypdf_version
            except Exception as exc:
                row["pdf_pages"] = None
                row["pdf_parse_error"] = str(exc)[:200]
        else:
            row["pdf_pages"] = None
        row["result"] = "RECEIVED_PDF_BYTES"
    except Exception as e:
        row["result"] = "BLOCKED: " + type(e).__name__ + ": " + str(e)[:300]
        row["read_completed_utc"] = utcnow()
    return row

class R006EphemeralOriginalPdfReceiptProbe(unittest.TestCase):
    def test_author_and_institutional_original_pdf_delivery(self):
        if os.environ.get("GITHUB_ACTIONS") != "true":
            self.skipTest("ephemeral CI-only source receipt; never fetch on local runs")
        rows = [observe(name, url) for name, url in URLS]
        for row in rows:
            print("MHAC_R006_PDF_RECEIPT " + json.dumps(row, sort_keys=True), flush=True)
        a, b, c = rows
        if b.get("content_sha256") and c.get("content_sha256"):
            print("MHAC_R006_ROMEO_URL_BYTE_STABLE " +
                  str(b["content_sha256"] == c["content_sha256"]), flush=True)
        # Diagnostic verdicts are in the immutable CI log, not inferred from a
        # green structural suite; never fabricate a source or a receipt.
        self.assertTrue(all(row["requested_url"].startswith("https://") for row in rows))


    def test_romeo_2023_public_zenodo_v1_supplementary(self):
        if os.environ.get("GITHUB_ACTIONS") != "true":
            self.skipTest("CI-only Zenodo record and authorised public file receipt")
        url = "https://zenodo.org/api/records/8042317"
        row = {"requested_url": url, "started_utc": utcnow(), "source": "romeo_2023_zenodo_v1"}
        try:
            req = request.Request(url, headers={
                "User-Agent": "MHAC-source-recovery/2026-11-10",
                "Accept": "application/json"})
            with request.urlopen(req, timeout=18) as rsp:
                raw = rsp.read(2000001)
                row["http_status"] = rsp.status
                row["http_date"] = rsp.headers.get("Date")
                row["response_opened_utc"] = utcnow()
            if len(raw) > 2000000:
                row["result"] = "BLOCKED: oversized metadata"
            else:
                obj = json.loads(raw)
                files = obj.get("files", [])
                row.update({"result":"PUBLIC_API_RECEIVED",
                            "raw_json_sha256": hashlib.sha256(raw).hexdigest(),
                            "record_id": obj.get("id"), "doi": obj.get("doi"),
                            "file_count": len(files),
                            "files": [{"key": f.get("key"), "id": f.get("id"),
                                       "checksum": f.get("checksum"), "size": f.get("size"),
                                       "content_url": f.get("links", {}).get("content")}
                                      for f in files[:8]]})
                for f in files[:2]:
                    link = f.get("links", {}).get("content")
                    a = {"key": f.get("key"), "content_url": link, "started_utc": utcnow()}
                    if not link or not link.startswith("https://zenodo.org/"):
                        a["result"] = "BLOCKED: no declared public Zenodo file URL"
                    else:
                        try:
                            with request.urlopen(request.Request(link, headers={
                                    "User-Agent":"MHAC-source-recovery/2026-11-10"}), timeout=22) as resp:
                                data = resp.read(MAX_BYTES + 1)
                                a["status"] = resp.status
                                a["http_date"] = resp.headers.get("Date")
                                a["receipt_utc"] = utcnow()
                            if len(data) > MAX_BYTES:
                                a["result"] = "BLOCKED: >30 MiB"
                            else:
                                a.update({"result":"PUBLIC_FILE_RECEIVED", "bytes":len(data),
                                          "sha256":hashlib.sha256(data).hexdigest()})
                        except Exception as e:
                            a["result"] = "BLOCKED: " + type(e).__name__ + ": " + str(e)[:180]
                    print("MHAC_R006_ZENODO_FILE_RECEIPT " + json.dumps(a, sort_keys=True), flush=True)
        except Exception as e:
            row["result"] = "BLOCKED: " + type(e).__name__ + ": " + str(e)[:180]
        row["completed_utc"] = utcnow()
        print("MHAC_R006_ZENODO_RECORD_RECEIPT " + json.dumps(row, sort_keys=True), flush=True)
        self.assertEqual(row["requested_url"], url)
