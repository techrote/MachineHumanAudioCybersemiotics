#!/usr/bin/env python3
"""Reproduce three ordered C9 bibliographies from matching, locally held PDFs.

No article narrative or empirical results are exported. Input PDFs are deliberately
kept outside the repository. Geometry exceptions below are source layout facts,
not changes to the cited bibliography. Bibliographic field splits are discovery
hints; citation_text and citation_lines preserve the whole printed citation.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

import pdfplumber

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_INPUT = pathlib.Path("/tmp/mhac-r005-reviews")
CONFIG = {
    "totland-2021": {
        "file": "totland-2021-alias-response",
        "sha256": "caf75fd9f71016b869d1c27aa238c56a8f302a4ae2ce4459647203432e8d600d",
        "pages": 52, "reference_pages": [42, 47], "count": 47,
        "style": "hanging", "body_bottom": 750,
        "non_start_lines": [
            [44, "IEEE 92(4): 742-758."],
            [46, "https://www.ukessays.com/essays/psycology/validity-and-reliability-of-systematic-"],
            [46, "review.php?vref=1"],
        ],
    },
    "edworthy-2013": {
        "file": "edworthy-epmc.pdf",
        "sha256": "e708a1d3a57082e3532bebfd6ec37631fe66bea8af1bf99858e7ec5e573c7cb2",
        "pages": 6, "reference_pages": [5, 6], "count": 80,
        "style": "numbered_columns", "printed_offset": 583,
    },
    "ruskin-2020": {
        "file": "ruskin-2020.pdf",
        "sha256": "fa14019c4a211467a5f9e1622b4d96306823e5ffb69bc1ac4bcd5458604097ec",
        "pages": 79, "reference_pages": [55, 79], "count": 185,
        "style": "hanging", "body_bottom": 720, "non_start_lines": [],
    },
}


def lines_from_page(page, number, printed, column=None):
    """Return reading-order lines with top-left-origin PDF-point rectangles."""
    grouped = []
    for word in page.extract_words(x_tolerance=1, y_tolerance=3):
        if not grouped or abs(word["top"] - grouped[-1][0]) > 2:
            grouped.append((word["top"], []))
        grouped[-1][1].append(word)
    result = []
    for _, words in grouped:
        result.append({
            "pdf_page": number, "printed_page": str(printed), "column": column,
            "text": " ".join(word["text"] for word in words),
            "bbox_pdf_points": [round(min(w["x0"] for w in words), 3),
                                round(min(w["top"] for w in words), 3),
                                round(max(w["x1"] for w in words), 3),
                                round(max(w["bottom"] for w in words), 3)],
        })
    return result


def citation_fields(text):
    """Conservative structural hints, never external identity verification."""
    date = re.search(r"\((?:[12]\d{3}(?:[a-z]|\d{4}|,\s*[^)]{1,35})?|n\.d\.?)\)", text)
    if date:
        author = text[:date.start()].strip()
        date_text = date.group()[1:-1]
        rest = text[date.end():].lstrip(". ")
        method = "parenthesized-date split"
    else:
        parts = text.split(". ", 1)
        author = parts[0] if len(parts) == 2 else None
        rest = parts[1] if len(parts) == 2 else text
        dates = re.findall(r"(?<!\d)(?:18|19|20)\d{2}[a-z]?(?!\d)", rest)
        date_text = dates[0] if len(dates) == 1 else None
        method = "first-full-stop split; date only if one occurrence"
    boundary = re.search(r"[.!?](?=\s+)", rest)
    title = rest[:boundary.end()] if boundary else rest
    tail = rest[boundary.end():].strip() if boundary else ""
    # Wrapped strings remain faithful in citation_lines; regex matches here are
    # only literal tokens, without repairing a split URL or DOI.
    return {
        "authors_text": author,
        "date_text": date_text,
        "title_text": title,
        "remaining_bibliographic_text": tail,
        "doi_tokens_as_extracted": re.findall(r"10\.\d{4,9}/[^\s]+", text),
        "url_tokens_as_extracted": re.findall(r"https?://[^\s]+", text),
        "status": "unverified parser hints; use complete citation_text for identity work",
        "split_method": method,
    }


def extract(key, conf, input_root):
    path = input_root / conf["file"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != conf["sha256"]:
        raise ValueError(f"{path}: expected source SHA256 {conf['sha256']}, got {digest}")
    refs = []
    handled_exceptions = []
    with pdfplumber.open(path) as pdf:
        if len(pdf.pages) != conf["pages"]:
            raise ValueError(f"{key}: unexpected page count")
        for number in range(conf["reference_pages"][0], conf["reference_pages"][1] + 1):
            page = pdf.pages[number - 1]
            printed = number + conf.get("printed_offset", 0)
            if conf["style"] == "numbered_columns":
                boxes = [
                    ("left", (20, 50, page.width / 2, page.height - 35)),
                    ("right", (page.width / 2, 50, page.width - 20, page.height - 35)),
                ]
                lines = [line for col, box in boxes
                         for line in lines_from_page(page.crop(box), number, printed, col)]
            else:
                lines = [line for line in lines_from_page(page, number, printed)
                         if 55 < line["bbox_pdf_points"][1] < conf["body_bottom"]]
            for line in lines:
                text = line["text"]
                if text in {"REFERENCES", "References", "Reference list"}:
                    continue
                source_number = None
                if conf["style"] == "numbered_columns":
                    match = re.match(r"^(\d{1,2}) (.*)", text)
                    is_start = bool(match)
                    if match:
                        source_number = int(match.group(1))
                        citation_line = match.group(2)
                    else:
                        citation_line = text
                else:
                    exception = [number, text] in conf["non_start_lines"]
                    if exception:
                        handled_exceptions.append([number, text])
                    is_start = line["bbox_pdf_points"][0] < 90 and not exception
                    citation_line = text
                if is_start:
                    refs.append({
                        "occurrence_id": f"C9-{key.upper()}-REF{len(refs) + 1:03d}",
                        "ordinal": len(refs) + 1,
                        "source_number": source_number,
                        "citation_lines": [],
                        "_text_lines": [],
                    })
                if not refs:
                    raise ValueError(f"{key}: continuation before first reference: {text}")
                refs[-1]["citation_lines"].append(line)
                refs[-1]["_text_lines"].append(citation_line)
    if len(refs) != conf["count"]:
        raise ValueError(f"{key}: expected {conf['count']} references, found {len(refs)}")
    if conf["style"] == "numbered_columns" and [r["source_number"] for r in refs] != list(range(1, 81)):
        raise ValueError("Edworthy printed numbering is incomplete or out of order")
    if sorted(handled_exceptions) != sorted(conf.get("non_start_lines", [])):
        raise ValueError(f"{key}: a reviewed layout exception changed")
    for ref in refs:
        ref["citation_text"] = " ".join(ref.pop("_text_lines"))
        ref["pdf_pages"] = sorted({line["pdf_page"] for line in ref["citation_lines"]})
        ref["printed_pages"] = list(dict.fromkeys(line["printed_page"] for line in ref["citation_lines"]))
        ref["bibliographic_parse_hints"] = citation_fields(ref["citation_text"])
    return {
        "schema_version": "mhac-r005-c9-reference-occurrences-v1",
        "review_key": key,
        "source_file_basename": conf["file"],
        "source_sha256": digest,
        "source_pdf_pages": conf["pages"],
        "reference_pdf_pages_inclusive": conf["reference_pages"],
        "reference_count": len(refs),
        "reference_order": "source order; column left then right within each Edworthy page",
        "reading_extent": "bibliography and source identity metadata only; no empirical extraction",
        "normalization": "PDF text-layer words joined by spaces; line boundaries and boxes retained; no citation corrections",
        "extraction_software": {"name": "pdfplumber", "version": pdfplumber.__version__},
        "coordinate_system": "PDF points; [x0, top, x1, bottom] from top-left of each source page",
        "layout_exceptions": conf.get("non_start_lines", []),
        "references": refs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=pathlib.Path, default=DEFAULT_INPUT)
    parser.add_argument("--check", action="store_true", help="compare with committed JSON instead of writing")
    args = parser.parse_args()
    for key, conf in CONFIG.items():
        result = extract(key, conf, args.input_dir)
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        target = HERE / f"{key}-references.json"
        if args.check:
            if not target.exists() or target.read_text() != encoded:
                raise SystemExit(f"{target.name}: deterministic export mismatch")
        else:
            target.write_text(encoded)
        print(f"{key}: {result['reference_count']} references; SHA256 {result['source_sha256']}")


if __name__ == "__main__":
    main()
