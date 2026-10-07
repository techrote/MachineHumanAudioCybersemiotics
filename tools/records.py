"""Load canonical records, preserve history, and compose offline validation."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
from typing import Any

from schemas import ValidationError
from schemas.v1 import validate_record
from tools.record_io import contained_path, fail, loads, read_json, relative_path, verify_artifact

CONTRACT = "mhac-records/1"
STATE_PATH = "research/registry/state.json"
DATA_FIELDS = {"contract", "dataset_kind", "research_state", "records",
               "release_claims", "release_requirements", "stage_gates"}
STATE_FIELDS = (DATA_FIELDS - {"records"}) | {
    "record_roots", "bibliography", "citation_manifests", "exports"}
ALLOWED_AREAS = (
    "research/registry/records", "research/sources", "research/searches",
    "research/screening", "research/extractions", "research/appraisal",
    "research/claims", "research/design", "research/experiments",
    "research/amendments", "research/assistance", "research/gates",
    "research/identity", "research/novelty", "research/protocol",
    "research/review",
)
SUBSTANTIVE_KINDS = {
    "source", "search_run", "search_hit", "screening", "study", "experiment",
    "sample", "theoretical_extraction", "extraction", "appraisal", "claim",
    "requirement", "experiment_protocol",
}


def empty_dataset() -> dict:
    return {"contract": CONTRACT, "dataset_kind": "live",
            "research_state": "not_started", "records": [], "release_claims": [],
            "release_requirements": [], "stage_gates": []}


def check_envelope(data: Any, *, expected_kind: str) -> None:
    if not isinstance(data, dict) or set(data) != DATA_FIELDS:
        fail("DATASET_SHAPE", "Unexpected or missing snapshot fields")
    if data["contract"] != CONTRACT:
        fail("CONTRACT", "An explicit migration is needed for this record contract")
    if expected_kind not in {"live", "fixture"} or data["dataset_kind"] != expected_kind:
        fail("CONTAMINATION", "Dataset disagrees with caller-selected context")
    if not isinstance(data["research_state"], str) or data["research_state"] not in {
            "not_started", "in_progress", "complete"}:
        fail("RESEARCH_STATE", str(data["research_state"]))
    for field in ("records", "release_claims", "release_requirements", "stage_gates"):
        if not isinstance(data[field], list):
            fail("DATASET_SHAPE", f"{field} must be an array")
    substantive = any(isinstance(row, dict) and isinstance(row.get("kind"), str)
                      and row["kind"] in SUBSTANTIVE_KINDS
                      for row in data["records"])
    if not substantive and data["research_state"] != "not_started":
        fail("EMPTY_COMPLETION", "Empty live evidence is valid only as not_started")
    if substantive and data["research_state"] == "not_started":
        fail("RESEARCH_STATE", "Substantive records cannot be labelled not_started")
    if expected_kind == "fixture" and data["research_state"] == "complete":
        fail("SYNTHETIC_COMPLETION", "Synthetic evidence cannot complete real research")


def assert_append_only(previous: dict, current: dict) -> None:
    """History is compared against an independently supplied accepted snapshot."""
    check_envelope(previous, expected_kind=current["dataset_kind"])
    before: dict[str, dict] = {}
    for row in previous["records"]:
        validate_record(row, expected_kind=previous["dataset_kind"])
        if row["id"] in before:
            fail("DUPLICATE_ID", row["id"])
        before[row["id"]] = row
    after = {row["id"]: row for row in current["records"]}
    for rid, old in sorted(before.items()):
        if rid not in after:
            fail("HISTORY", f"Deleted record {rid}; retain history and record a disposition")
        new = after[rid]
        if {key: value for key, value in old.items() if key != "revisions"} != {
                key: value for key, value in new.items() if key != "revisions"}:
            fail("HISTORY", f"Changed immutable envelope of {rid}")
        if new["revisions"][:len(old["revisions"])] != old["revisions"]:
            fail("HISTORY", f"Rewrote or deleted revisions of {rid}")


def _verify_local_artifacts(data: dict, root: Path | None) -> None:
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if "path" in value and "sha256" in value:
                if root is None:
                    fail("ARTIFACT_ROOT", "Supply the repository or fixture root to check artifacts")
                verify_artifact(root, value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    for row in data["records"]:
        for revision in row["revisions"]:
            visit(revision["data"])
            if row["kind"] != "source":
                continue
            for manifestation in revision["data"]["manifestations"]:
                if "fixture_path" in manifestation:
                    if data["dataset_kind"] != "fixture":
                        fail("CONTAMINATION", "fixture_path cannot appear in a live record")
                    if root is None:
                        fail("ARTIFACT_ROOT", "Supply the fixture root to check source bytes")
                    verify_artifact(root, {"path": manifestation["fixture_path"],
                                           "sha256": manifestation["sha256"]})
                if "local_path" in manifestation:
                    if root is None:
                        fail("ARTIFACT_ROOT", "Supply the artifact root to check source bytes")
                    verify_artifact(root, {"path": manifestation["local_path"],
                                           "sha256": manifestation["sha256"]})


def validate_dataset(data: Any, *, expected_kind: str, previous: dict | None = None,
                     root: Path | None = None) -> dict:
    from tools.evidence_flow import evidence_flow
    from tools.record_graph import validate_graph
    from tools.research_gates import validate_gates

    check_envelope(data, expected_kind=expected_kind)
    ids: set[str] = set()
    for row in data["records"]:
        validate_record(row, expected_kind=expected_kind)
        if row["id"] in ids:
            fail("DUPLICATE_ID", row["id"])
        ids.add(row["id"])
    if previous is not None:
        assert_append_only(previous, data)
    graph = validate_graph(data["records"])
    for field, kind in (("release_claims", "claim"),
                        ("release_requirements", "requirement")):
        seen = set()
        for ref in data[field]:
            from schemas.v1 import pin
            key = pin(ref)
            if key in seen:
                fail("DUPLICATE_REFERENCE", field)
            seen.add(key)
            graph.require_current(ref, kind=kind)
    _verify_local_artifacts(data, root)
    gates = validate_gates(data, graph, root=root)
    flow = evidence_flow(graph)
    return {
        "contract": CONTRACT, "structural_result": "pass",
        "dataset_kind": expected_kind, "research_state": data["research_state"],
        "record_count": len(ids),
        "revision_count": sum(len(r["revisions"]) for r in data["records"]),
        "counts": flow,
        "currency": {
            "invalidated": [{"id": i, "rev": r} for i, r in sorted(graph.invalidated)],
            "stale": [{"id": i, "rev": r} for i, r in sorted(graph.stale)],
            "latest_stale_ids": sorted(rid for rid, row in graph.records.items()
                                       if (rid, len(row["revisions"])) in graph.stale),
        },
        "history_comparison": "checked" if previous is not None else "not_supplied",
        "stage_gates": gates,
        "checks": {"schemas": "passed", "references_and_graph": "passed",
                   "artifacts": "passed" if root is not None else "no_local_artifacts",
                   "release_currency": "passed", "evidence_flow": "passed"},
        "warnings": flow.get("warnings", []),
        "not_evaluated": [
            "source_fidelity", "scientific_validity", "statistical_method_adequacy",
            "truth_of_report_or_sample_identity", "truth_of_human_identity_or_independence",
            "protocol_specific_reading_sufficiency", "online_identifier_resolution",
            "external_peer_review_or_participant_performance",
        ],
    }


def _check_state(state: Any) -> None:
    if not isinstance(state, dict) or set(state) != STATE_FIELDS:
        fail("REGISTRY_STATE", "Unexpected or missing live manifest fields")
    roots = state["record_roots"]
    if not isinstance(roots, list) or not roots or len(set(map(str, roots))) != len(roots):
        fail("RECORD_ROOT", "record_roots must be a nonempty unique array")
    for relative in roots:
        relative_path(relative)
        if not any(relative == area or relative.startswith(area + "/") for area in ALLOWED_AREAS):
            fail("RECORD_ROOT", relative)
    for index, first in enumerate(roots):
        for second in roots[index + 1:]:
            if first.startswith(second + "/") or second.startswith(first + "/"):
                fail("RECORD_ROOT", "Canonical roots cannot overlap")
    relative_path(state["bibliography"])
    relative_path(state["exports"])
    if state["exports"] != "research/registry/generated" and not state["exports"].startswith(
            "research/registry/generated/"):
        fail("EXPORT_ROOT", "Use research/registry/generated or a child directory")
    if not isinstance(state["citation_manifests"], list):
        fail("CITATION_MANIFEST", "Expected an array")
    if len(set(map(str, state["citation_manifests"]))) != len(state["citation_manifests"]):
        fail("CITATION_MANIFEST", "Duplicate manifest path")
    for path in state["citation_manifests"]:
        relative_path(path)
    snapshot = {key: value for key, value in state.items() if key in DATA_FIELDS}
    snapshot["records"] = []
    # The research state is evaluated after canonical files have been loaded.
    if state["contract"] != CONTRACT or state["dataset_kind"] != "live":
        fail("REGISTRY_STATE", "Canonical manifests must declare the live v1 contract")


def load_registry(root: Path) -> tuple[dict, dict]:
    root = root.resolve()
    state = read_json(contained_path(root, STATE_PATH))
    _check_state(state)
    records, paths, ids = [], set(), set()
    for relative in sorted(state["record_roots"]):
        directory = contained_path(root, relative, must_exist=False)
        if directory.exists() and not directory.is_dir():
            fail("RECORD_ROOT", relative)
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                fail("SYMLINK", str(path.relative_to(root)))
            if not path.is_file() or path.suffix != ".json":
                continue
            rel = path.relative_to(root).as_posix()
            row = read_json(contained_path(root, rel))
            if not isinstance(row, dict) or path.name != str(row.get("id", "")) + ".json":
                fail("RECORD_FILENAME", rel)
            if row["id"] in ids:
                fail("DUPLICATE_ID", row["id"])
            ids.add(row["id"])
            paths.add(rel)
            records.append(row)
    # A record cannot silently escape validation by omitting its lane from the manifest.
    research = root / "research"
    for path in sorted(research.rglob("*.json")):
        if path.is_symlink():
            fail("SYMLINK", str(path.relative_to(root)))
        rel = path.relative_to(root).as_posix()
        contained_path(root, rel)
        if rel in paths or rel.startswith(state["exports"] + "/"):
            continue
        candidate = read_json(path)
        if isinstance(candidate, dict) and {"id", "kind", "revisions"} <= set(candidate):
            fail("UNREGISTERED_RECORD", rel)
    data = {key: value for key, value in state.items() if key in DATA_FIELDS}
    data["records"] = sorted(records, key=lambda r: str(r.get("id", "")))
    return data, state


def load_snapshot(path: Path, *, expected_kind: str | None = None) -> dict:
    if path.is_symlink():
        fail("SYMLINK", str(path))
    data = read_json(path)
    if expected_kind is not None:
        check_envelope(data, expected_kind=expected_kind)
    return data


def snapshot_from_git(root: Path, ref: str) -> dict:
    """Read a pre-fetched immutable base; never contacts the network."""
    if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", ref) is None:
        fail("HISTORY_REF", "Expected a full immutable commit SHA")

    def git(*args: str, missing: bool = False) -> str | None:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                text=True, encoding="utf-8")
        if result.returncode:
            if missing:
                return None
            fail("HISTORY_REF", result.stderr.strip() or "Git object unavailable")
        return result.stdout

    git("cat-file", "-e", ref + "^{commit}")
    state_text = git("show", ref + ":" + STATE_PATH, missing=True)
    entries = git("ls-tree", "-r", ref, "--", "research") or ""
    paths = []
    for line in entries.splitlines():
        meta, path = line.split("\t", 1)
        mode, object_type, _ = meta.split(" ")
        if path.endswith(".json"):
            if mode != "100644" or object_type != "blob":
                fail("HISTORY_PATH", path)
            paths.append(path)
    if state_text is None:
        for path in paths:
            value = loads(git("show", ref + ":" + path) or "")
            if isinstance(value, dict) and {"id", "kind", "revisions"} <= set(value):
                fail("HISTORY_STATE", "Base has records but no registry state")
        return empty_dataset()
    state = loads(state_text)
    _check_state(state)
    records = []
    for path in paths:
        if any(path.startswith(prefix + "/") for prefix in state["record_roots"]):
            row = loads(git("show", ref + ":" + path) or "")
            if not isinstance(row, dict) or Path(path).name != str(row.get("id", "")) + ".json":
                fail("RECORD_FILENAME", path)
            records.append(row)
    result = {key: value for key, value in state.items() if key in DATA_FIELDS}
    result["records"] = sorted(records, key=lambda row: row["id"])
    return result
