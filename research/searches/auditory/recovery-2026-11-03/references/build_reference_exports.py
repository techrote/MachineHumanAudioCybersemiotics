"""Reproduce bibliographic metadata from two hash-identified, lawfully obtained PDFs.

Full PDFs and extracted body text stay outside the public repository. This writes
reference entries only, with file-page coordinates; it makes no study decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = {
    "nees-liebman-am": {
        "source_id": "SRC-AUD-NEES-LIEBMAN-2023-AM",
        "sha256": "5585a4d7d64d84edaef80ab322863a273152e85eac572da4bbeec245540e2fbf",
        "url": "https://osf.io/download/zaqbh/",
        "pages": 52, "range": [33, 42], "expected_entries": 85,
        "section": "References (general bibliography, distinct from the 69-entry meta-analysis list)",
    },
    "sleep-review": {
        "source_id": "SRC-AUD-MCFARLANE-2020-REVIEW",
        "sha256": "5cc81d1275bafc8da1e3e3ac7e5b4f08801a19c7759667cd32368615a33e77b4",
        "url": "https://mdpi-res.com/d_attachment/clockssleep/clockssleep-02-00031/article_deploy/clockssleep-02-00031-v2.pdf",
        "pages": 18, "range": [14, 18], "expected_entries": 91,
        "section": "References, numbered 1–91 (printed pp.429–433)",
    },
}


def extract(label: str, pdf: Path, config: dict) -> list[dict]:
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != config["sha256"]:
        raise ValueError(f"Unexpected source bytes: {label}")
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    pages = text.split("\f")
    if pages[-1].strip() == "":
        pages.pop()
    if len(pages) != config["pages"]:
        raise ValueError(f"Unexpected page count: {label}")
    result, current = [], None
    in_references = False
    begin, end = config["range"]
    for page in range(begin, end + 1):
        for line in pages[page - 1].splitlines():
            stripped = line.strip()
            if stripped == "References":
                in_references = True
                continue
            if not in_references or not stripped or stripped.isdigit():
                continue
            if label == "sleep-review":
                if stripped.startswith("Clocks&Sleep"):
                    continue
                if stripped.startswith("Publisher’s Note:"):
                    break
                match = re.match(r"^(\d+)\.\s+(.*)", line)
                new = bool(match)
            else:
                match = None
                new = bool(re.match(r"^\S", line))
            if new:
                if current:
                    result.append(current)
                current = {
                    "ordinal": int(match[1]) if match else len(result) + 1,
                    "text": match[2].strip() if match else stripped,
                    "file_page_start": page, "file_page_end": page,
                }
            elif current:
                current["text"] += " " + stripped
                current["file_page_end"] = page
    if current:
        result.append(current)
    if [r["ordinal"] for r in result] != list(range(1, config["expected_entries"] + 1)):
        raise ValueError(f"Reference numbering/count mismatch: {label}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = {
        "schema": "mhac-r005-bibliographic-reference-recovery/1",
        "date": "2026-11-03",
        "method": "Poppler pdftotext -layout; ordered entry boundaries and page ranges checked by agent, with rendered first/last pages inspected. Bibliographic metadata only.",
        "boundary": "References are discovery occurrences, not included studies; original PDF extraction spelling is preserved and identifiers still require verification.",
        "sources": [],
    }
    for label, config in SOURCES.items():
        output["sources"].append({"label": label, **config,
                                  "entries": extract(label, args.source_directory / (label + ".pdf"), config)})
    rendered = json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    path = HERE / "REFERENCE-LISTS.json"
    if args.check:
        if path.read_text() != rendered:
            raise SystemExit("Reference-list export differs")
    else:
        if path.exists() and path.read_text() != rendered:
            raise SystemExit("Refusing to overwrite different retained reference evidence")
        path.write_text(rendered)
    print("Verified 85 Nees–Liebman general references and 91 McFarlane references.")


if __name__ == "__main__":
    main()
