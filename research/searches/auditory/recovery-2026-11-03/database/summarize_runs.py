"""Verify compressed exports and summarize all production runs without screening."""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EXPORTS = ROOT / "research/searches/auditory/exports/openalex"
summary = {
    "schema": "mhac-r005-database-execution-summary/1",
    "unit_warning": "API work IDs and search occurrences are not eligible publications, studies or samples",
    "runs": [], "families": {}, "all_retained_occurrences": 0,
}
union = set()
family_unions = {}
for path in sorted(EXPORTS.glob("20261103-database*/MANIFEST.json")):
    manifest = json.loads(path.read_bytes())
    group = {"run_id": manifest["run_id"], "manifest": path.relative_to(ROOT).as_posix(),
             "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
             "complete": manifest.get("complete", False), "finished_at": manifest.get("finished_at"),
             "requests_made": manifest["requests_made"], "families": []}
    for label, run in manifest["runs"].items():
        ids = []
        for page in run["pages"]:
            if not page.get("file"):
                continue
            data_path = ROOT / page["file"]
            body = data_path.read_bytes()
            assert hashlib.sha256(body).hexdigest() == page["sha256"], data_path
            payload = gzip.decompress(body) if data_path.suffix == ".gz" else body
            if "payload_sha256" in page:
                assert hashlib.sha256(payload).hexdigest() == page["payload_sha256"], data_path
            data = json.loads(payload)
            for item in data.get("results", []):
                assert "abstract_inverted_index" not in item, data_path
                ids.append(item["id"])
        assert len(ids) == run["retrieved"], label
        assert len(set(ids)) == run["unique_retrieved"], label
        summary["all_retained_occurrences"] += len(ids)
        union.update(ids)
        family_unions.setdefault(label, set()).update(ids)
        row = {"label": label, "run_id": manifest["run_id"], "status": run["status"],
               "complete": run["complete"], "reported_count": run.get("reported_count"),
               "occurrences": len(ids), "unique_work_ids_within_run": len(set(ids)),
               "failures": run["failures"], "sort": run.get("sort", "provider default relevance")}
        group["families"].append(row)
        summary["families"].setdefault(label, []).append(row)
    summary["runs"].append(group)
summary["distinct_api_work_ids_across_all_runs"] = len(union)
summary["distinct_api_work_ids_by_family_across_attempts"] = {label: len(ids) for label, ids in sorted(family_unions.items())}
summary["completed_families"] = sorted(label for label, rows in summary["families"].items() if any(row["complete"] for row in rows))
summary["incomplete_families"] = sorted(set(summary["families"]) - set(summary["completed_families"]))
(HERE / "database-execution-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({key: summary[key] for key in ("all_retained_occurrences", "distinct_api_work_ids_across_all_runs", "completed_families", "incomplete_families")}, indent=2))
