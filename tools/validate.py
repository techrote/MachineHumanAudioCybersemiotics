"""Validate repository and research-record structure, not scientific truth.

Python 3.11+, standard library only. Run from any directory; --root is optional.
Markdown checks cover inline local file targets, not anchors or full CommonMark.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import unquote

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schemas import ValidationError
from tools.record_io import dumps, read_json, unique_object

REPOSITORY = "techrote/MachineHumanAudioCybersemiotics"
REQUIRED = (
    "README.md", "AGENTS.md", "RAG.md", "KICKOFF.md", "programme.json",
    "docs/PROGRAMME.md", "docs/AGENT_RUNBOOK.md", "docs/RESEARCH_PROTOCOL.md",
    "docs/SEARCH_STRATEGY.md", "docs/SEED_SOURCES.md", "docs/DATA_MODEL.md",
    "docs/SYNTHESIS_METHOD.md", "docs/RESEARCH_INTEGRITY.md",
    "docs/PROJECT_FOUNDATIONS.md", "docs/EXPERIMENTS.md", "docs/PAPER_PLAN.md",
    "docs/HUMAN_GATES.md", "docs/VALIDATION.md", "research/README.md",
    "research/templates/README.md", ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/research-ci.yml", "tools/validate.py", "tests/test_validate.py",
    "schemas/__init__.py", "schemas/v1.py", "schemas/README.md",
    "research/registry/state.json", "research/registry/bibliography.json",
    "research/registry/README.md",
)
PHASES = {"foundation", "protocol", "corpus", "analysis", "design", "dossier",
          "paper", "audit", "package", "human_gate"}
SKIP = {".git", ".venv", "node_modules", "build", "dist", "local-sources",
        "private-data", "private-correspondence", "__pycache__"}
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def string_list(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValidationError(f"{field} must be a list of nonblank strings")
    if nonempty and not value:
        raise ValidationError(f"{field} must not be empty")
    if len(value) != len(set(value)):
        raise ValidationError(f"{field} contains duplicates")
    return value


def validate_programme(data: Any) -> None:
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValidationError("Programme schema_version must be integer 1")
    if data.get("repository") != REPOSITORY:
        raise ValidationError("Programme repository does not match this project")
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValidationError("Programme tasks must be a nonempty list")
    graph: dict[str, list[str]] = {}
    issues: set[int] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValidationError("Each task must be an object")
        task_id = task.get("id")
        if not isinstance(task_id, str) or re.fullmatch(r"MHAC-R\d{3}", task_id) is None:
            raise ValidationError(f"Invalid task ID: {task_id!r}")
        if task_id in graph:
            raise ValidationError(f"Duplicate task ID: {task_id}")
        issue = task.get("issue")
        if type(issue) is not int or issue < 1 or issue in issues:
            raise ValidationError(f"Invalid or duplicate issue number for {task_id}")
        issues.add(issue)
        title = task.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError(f"Missing title for {task_id}")
        phase = task.get("phase")
        if not isinstance(phase, str) or phase not in PHASES:
            raise ValidationError(f"Invalid phase for {task_id}")
        if type(task.get("human_gate")) is not bool:
            raise ValidationError(f"human_gate must be Boolean for {task_id}")
        if task["human_gate"] != (phase == "human_gate"):
            raise ValidationError(f"Human-gate phase mismatch for {task_id}")
        deps = string_list(task.get("depends_on"), f"{task_id}.depends_on")
        string_list(task.get("docs"), f"{task_id}.docs", nonempty=True)
        string_list(task.get("owns"), f"{task_id}.owns", nonempty=True)
        graph[task_id] = deps
    for task_id, deps in graph.items():
        for dep in deps:
            if dep not in graph:
                raise ValidationError(f"Unknown dependency {dep} in {task_id}")
            if dep == task_id:
                raise ValidationError(f"Self-dependency in {task_id}")
    active: set[str] = set()
    done: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            raise ValidationError(f"Dependency cycle at {node}")
        if node in done:
            return
        active.add(node)
        for dep in graph[node]:
            visit(dep)
        active.remove(node)
        done.add(node)

    for node in graph:
        visit(node)


def local_path(root: Path, base: Path, target: str) -> Path:
    decoded = unquote(target.split("#", 1)[0].split("?", 1)[0])
    path = (root / decoded.lstrip("/") if decoded.startswith("/") else base / decoded).resolve()
    if not path.is_relative_to(root):
        raise ValidationError(f"Local path escapes repository: {target}")
    return path


def markdown_targets(text: str) -> list[str]:
    targets: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        for match in LINK.finditer(line):
            target = match.group(1).strip().split(" ", 1)[0].strip("<>")
            if target and not target.startswith(("#", "//")) and not SCHEME.match(target):
                targets.append(target)
    return targets


def validate_repository(root: Path, *, previous: dict | None = None,
                        write_exports: bool = False) -> dict:
    root = root.resolve()
    for relative in REQUIRED:
        if not (root / relative).is_file():
            raise ValidationError(f"Missing required file: {relative}")
    data = read_json(root / "programme.json")
    validate_programme(data)
    for task in data["tasks"]:
        for doc in task["docs"]:
            if not local_path(root, root, doc).is_file():
                raise ValidationError(f"Missing authority {doc} for {task['id']}")
    for path in sorted(root.rglob("*")):
        if not path.is_file() or set(path.relative_to(root).parts) & SKIP:
            continue
        if path.suffix == ".json":
            read_json(path)
        elif path.suffix == ".md":
            for target in markdown_targets(path.read_text(encoding="utf-8")):
                if not local_path(root, path.parent, target).exists():
                    raise ValidationError(f"Broken local Markdown target in {path.relative_to(root)}: {target}")
    from tools.citations import validate_citations
    from tools.evidence_flow import render_exports
    from tools.record_graph import validate_graph
    from tools.record_io import contained_path, fail
    from tools.records import load_registry, validate_dataset

    dataset, state = load_registry(root)
    report = validate_dataset(dataset, expected_kind="live", previous=previous, root=root)
    report["citations"] = validate_citations(
        root, state["bibliography"], state["citation_manifests"], validate_graph(dataset["records"]))
    rendered = render_exports(dataset, report)
    export_root = contained_path(root, state["exports"], must_exist=False)
    if export_root.exists():
        for candidate in sorted(export_root.rglob("*")):
            relative = candidate.relative_to(root).as_posix()
            contained_path(root, relative)
            if candidate.is_file() and candidate.relative_to(export_root).as_posix() not in rendered:
                fail("UNEXPECTED_EXPORT", relative)
    for name, content in rendered.items():
        relative = state["exports"] + "/" + name
        path = contained_path(root, relative, must_exist=False)
        if write_exports:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        elif not path.is_file() or path.read_bytes() != content.encode("utf-8"):
            fail("STALE_EXPORT", f"{relative}; rebuild with --write-exports")
    report["checks"]["generated_exports"] = "passed"
    report["checks"]["repository_structure"] = "passed"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--records", type=Path, help="Validate a portable snapshot instead of the live repository")
    parser.add_argument("--dataset-kind", choices=("live", "fixture"),
                        help="Required caller-selected context with --records")
    history = parser.add_mutually_exclusive_group()
    history.add_argument("--previous", type=Path, help="Prior accepted portable snapshot")
    history.add_argument("--previous-ref", help="Full pre-fetched base commit SHA; no network access")
    parser.add_argument("--report", type=Path, help="Write the same deterministic JSON report printed to stdout")
    parser.add_argument("--write-exports", action="store_true",
                        help="Rebuild the four live generated views after successful record validation")
    args = parser.parse_args(argv)
    if bool(args.records) != bool(args.dataset_kind):
        parser.error("--records and --dataset-kind must be supplied together")
    if args.records and (args.previous_ref or args.write_exports):
        parser.error("--previous-ref and --write-exports require the live repository route")
    try:
        from tools.records import load_snapshot, snapshot_from_git, validate_dataset
        previous = load_snapshot(args.previous) if args.previous else (
            snapshot_from_git(args.root, args.previous_ref) if args.previous_ref else None)
        if args.records:
            report = validate_dataset(load_snapshot(args.records),
                                      expected_kind=args.dataset_kind,
                                      previous=previous, root=args.records.resolve().parent)
        else:
            report = validate_repository(args.root, previous=previous,
                                         write_exports=args.write_exports)
        code = 0
    except (ValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = {"structural_result": "fail", "error": str(exc)}
        code = 1
    except RecursionError:
        report = {"structural_result": "fail", "error": "INPUT_DEPTH_LIMIT: input nesting is excessive"}
        code = 1
    output = dumps(report)
    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(output, encoding="utf-8", newline="\n")
        except OSError as exc:
            print(dumps({"structural_result": "fail", "error": f"REPORT_WRITE: {exc}"}), end="")
            return 1
    print(output, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
