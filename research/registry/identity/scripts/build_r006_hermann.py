"""Reproduce a three-occurrence identity tranche; never screen or read a paper.

The first build records its actual UTC time. Later builds retain the recorded
time and original revision pins. ``--check`` verifies the frozen tranche without
writing. Existing later canonical revisions are preserved by the record writer.
"""
from __future__ import annotations

import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
import io
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.record_io import dumps, read_json  # noqa: E402
from tools.records import write_generated_records  # noqa: E402

AREA = "research/registry/identity"
LEDGER = AREA + "/R006-HERMANN-2008.json"
TABLE = AREA + "/R006-HERMANN-2008.csv"
SOURCE = "SRC-REL-HERMANN-2008"
SOURCE_PATH = "research/sources/related/records/" + SOURCE + ".json"
URL = "https://www.icad.org/Proceedings/2008/Hermann2008.pdf"
HITS = ("HIT-R005-IW6-07", "HIT-R005-IW9-08", "HIT-R005-C5LIST-0644")
AID = "AID-R006-HERMANN-IDENTITY"
ACTOR = {"kind": "agent", "id": "chatgpt-r006-identity-20261103",
         "model": "GPT-6 Astra Pro", "tool": "ChatGPT; local Python record comparison"}


def ref(rid, rev=1):
    return {"id": rid, "rev": rev}


def digest(value):
    return hashlib.sha256(dumps(value).encode("utf-8")).hexdigest()


def build(root: Path, at: str) -> tuple[dict[str, dict], dict, str]:
    source_revision = read_json(root / SOURCE_PATH)["revisions"][0]
    source = source_revision["data"]
    if source["metadata_status"] != "verified" or not any(
            item["scheme"] == "url" and item["status"] == "verified" and item["value"] == URL
            for item in source["identifiers"]):
        raise ValueError("Pinned source revision no longer supports the exact verified URL")
    out, rows = {}, []
    for index, hid in enumerate(HITS):
        path = "research/searches/auditory/records/hits/" + hid + ".json"
        current = read_json(root / path)
        original = copy.deepcopy(current["revisions"][0])
        before = original["data"]
        if before["status"] != "unresolved" or before["returned_identifiers"] != [{"scheme": "url", "value": URL}]:
            raise ValueError("Pinned occurrence differs from the reviewed unresolved exact-URL case: " + hid)
        after = copy.deepcopy(before)
        after.update(source_ref=ref(SOURCE), status="resolved" if index == 0 else "duplicate",
                     resolution_reason="MHAC-R006: exact returned URL equals the verified publication URL on SRC-REL-HERMANN-2008 revision 1 (R004 access ledger row 16). Identity only; no new source reading or eligibility decision. See research/registry/identity/R006-HERMANN-2008.json.")
        basis = [before["search_ref"], ref(hid), ref(SOURCE), ref(AID)]
        if index:
            after["duplicate_of"] = ref(HITS[0], 2)
            basis.append(ref(HITS[0], 2))
        revision = {"rev": 2, "at": at, "actor": ACTOR, "basis": basis,
                    "factual_status": "derived", "data": after}
        out[path] = {**current, "revisions": [original, revision]}
        rows.append({"hit_id": hid, "input_ref": ref(hid), "input_revision_sha256": digest(original),
                     "output_ref": ref(hid, 2), "output_revision_sha256": digest(revision),
                     "source_ref": ref(SOURCE), "status": after["status"],
                     "duplicate_of": after.get("duplicate_of"), "exact_url": URL,
                     "original_search_ref": before["search_ref"], "original_ordinal": before["ordinal"]})
    inputs = [ref(SOURCE), *(ref(hid) for hid in HITS)]
    out[AREA + "/records/" + AID + ".json"] = {
        "id": AID, "issue": 6, "kind": "assistance", "schema_version": 1, "synthetic": False,
        "revisions": [{"rev": 1, "at": at, "actor": ACTOR, "basis": inputs,
                       "factual_status": "derived", "data": {
            "subtype": "assistance", "status": "performed", "performed_at": {"state": "known", "value": at},
            "task": "Resolve three preserved R005 occurrences to the existing R004 Hermann 2008 publication by exact equality with its verified URL; preserve duplicate discovery paths.",
            "input_refs": inputs, "output_refs": [ref(hid, 2) for hid in HITS],
            "artifacts": [LEDGER, TABLE, AREA + "/README.md", AREA + "/REVIEW-R006-INFRASTRUCTURE.md"],
            "verification_steps": [
                "Compared all three original returned URL strings with the verified URL on the pinned accepted R004 source revision; no URL normalization or fuzzy title matching was needed.",
                "Kept the source and every original hit revision unchanged; the two duplicate links point to the representative occurrence's new source-resolved revision.",
                "Selected IW6-07 as the representative within this tranche because its recorded query began before IW9 and the directory listing; no claim that it was the first global discovery.",
            ],
            "limitations": "Relies on R004's recorded metadata verification and previously recorded PDF hash. R006 did not retrieve or read the PDF, verify its contents, make an eligibility decision, or identify participants, studies or samples. Other discovery remains outside this tranche.",
            "independence": "One ChatGPT agent performed the identity comparison and self-review. No independent human review or external scholarly review.",
        }}],
    }
    ledger = {
        "artifact_kind": "bounded_identity_tranche", "issue": 6, "status": "partial_issue_work",
        "resolved_at": at, "actor": ACTOR, "implementation_base": "9eab42a6c8d899dbae9eb09b35758c188ddf5ed2",
        "method": "Exact URL-string equality with a previously verified publication identifier; retain all occurrences.",
        "source": {"source_ref": ref(SOURCE), "path": SOURCE_PATH,
                   "revision_sha256": digest(source_revision), "verified_url": URL,
                   "title": source["title"], "recorded_pdf_sha256": source["manifestations"][0]["sha256"],
                   "pdf_hash_status": "Inherited from R004; not a fresh PDF-byte verification in R006."},
        "occurrences": rows,
        "counts": {"occurrences": 3, "existing_publications": 1, "new_source_records": 0,
                   "resolved_representatives": 1, "duplicate_occurrences": 2,
                   "screening_decisions_created": 0, "study_records_created": 0, "sample_records_created": 0},
        "boundaries": ["No Track E or Track G eligibility is decided.",
                       "No complete source reading or new access observation is asserted.",
                       "Duplicate occurrences do not represent independent studies or samples.",
                       "Other unresolved discovery and every unmet R006 acceptance criterion remain open."],
    }
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["hit_id", "input_revision", "output_revision", "source_id", "source_revision", "status", "duplicate_of", "exact_url"])
    for row in rows:
        writer.writerow([row["hit_id"], 1, 2, SOURCE, 1, row["status"], HITS[0] + "@2" if row["duplicate_of"] else "", URL])
    return out, ledger, buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ledger_path = ROOT / LEDGER
    if args.check and not ledger_path.exists():
        raise SystemExit("Frozen tranche ledger is missing")
    at = (read_json(ledger_path)["resolved_at"] if ledger_path.exists()
          else datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"))
    records, ledger, table = build(ROOT, at)
    if ledger_path.exists() and read_json(ledger_path) != ledger:
        raise SystemExit("Frozen identity tranche ledger drift; preserve the reviewed input pins and recorded decisions")
    if args.check:
        if (ROOT / TABLE).read_text(encoding="utf-8") != table:
            raise SystemExit("Identity tranche ledger/table drift")
        for path, expected in records.items():
            actual = read_json(ROOT / path)
            prefix = {**actual, "revisions": actual["revisions"][:len(expected["revisions"])]}
            if prefix != expected:
                raise SystemExit("Identity tranche revision drift: " + path)
        print("Three-occurrence Hermann identity tranche reproduces; later revisions, if present, are preserved.")
        return 0
    write_generated_records(ROOT, records)
    ledger_path.write_text(dumps(ledger), encoding="utf-8")
    (ROOT / TABLE).write_text(table, encoding="utf-8")
    print("Recorded 3 occurrences -> 1 existing publication; no eligibility or study/sample decision.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
