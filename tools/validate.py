"""Validate bootstrap structure, not scientific truth or research completion.

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
)
PHASES = {"foundation", "protocol", "corpus", "analysis", "design", "dossier",
          "paper", "audit", "package", "human_gate"}
SKIP = {".git", ".venv", "node_modules", "build", "dist", "local-sources",
        "private-data", "private-correspondence", "__pycache__"}
LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class ValidationError(ValueError):
    """A deterministic repository invariant failed."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


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


def validate_repository(root: Path) -> None:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        validate_repository(args.root)
    except (ValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("OK: bootstrap repository integrity. Scientific validity and research-completion gates are not evaluated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
