#!/usr/bin/env python3
"""MHAC-X004: inspect Markdown sediment present in Git history but absent at HEAD.

This is an archive/branch archaeology tool, not a scientific acceptance oracle.
It treats a path's most recent add/modify blob reachable through --all as a
historical witness and never promotes that witness to accepted main.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sediment_atlas as base  # noqa: E402


def git(root: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, check=check,
        env={**os.environ, "TZ": "UTC"},
    )
    return proc.stdout


def latest_content_index(root: Path) -> dict[str, tuple[str, str]]:
    """Return latest reachable add/modify commit and UTC date for Markdown paths."""
    out = git(
        root, "log", "--all", "--diff-filter=AM",
        "--date=format-local:%Y-%m-%d", "--format=@@%H\t%ad",
        "--name-only", "--", "*.md",
    )
    current_sha = None
    current_date = None
    result: dict[str, tuple[str, str]] = {}
    for raw in out.splitlines():
        if raw.startswith("@@"):
            payload = raw[2:].split("\t", 1)
            current_sha = payload[0].strip()
            current_date = payload[1].strip() if len(payload) > 1 else ""
            continue
        path = raw.strip()
        if path and current_sha and path.endswith(".md") and base.eligible(path):
            result.setdefault(path, (current_sha, current_date or ""))
    return result


def historical_markdown_paths(root: Path) -> set[str]:
    return set(latest_content_index(root))


def current_markdown_paths(root: Path) -> set[str]:
    out = git(root, "ls-tree", "-r", "--name-only", "HEAD")
    return {
        line.strip()
        for line in out.splitlines()
        if line.strip().endswith(".md")
        and base.eligible(line.strip())
    }


def blob_text(root: Path, sha: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(root), "show", f"{sha}:{path}"],
        capture_output=True, check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def refs_containing(root: Path, sha: str) -> list[str]:
    out = git(
        root, "for-each-ref", "--format=%(refname:short)", "--contains", sha,
        "refs/heads", "refs/remotes/origin", check=False,
    )
    refs = sorted({line.strip() for line in out.splitlines() if line.strip()})
    return refs[:12]


def analyze_shadow(root: Path, max_docs: int = 400) -> dict:
    root = root.resolve()
    content_index = latest_content_index(root)
    historical = set(content_index)
    current = current_markdown_paths(root)
    absent = sorted(historical - current)
    witnesses = []
    skipped = []
    for path in absent[:max_docs]:
        entry = content_index.get(path)
        if not entry:
            skipped.append({"path": path, "reason": "no_add_or_modify_commit"})
            continue
        sha, date = entry
        text = blob_text(root, sha, path)
        if text is None:
            skipped.append({"path": path, "reason": "blob_unreadable_at_latest_content_commit"})
            continue
        words = base.tokens(text)
        witnesses.append({
            "path": path,
            "sha": sha,
            "date": date or None,
            "refs": [],
            "family": base.family(path),
            "fine_family": base.fine(path),
            "words": len(words),
            "motifs": base.motif_hits(text),
            "markers": {
                name: sum(len(__import__("re").findall(p, base.clean(text).lower(),
                                                       __import__("re").I | __import__("re").S))
                          for p in patterns)
                for name, patterns in base.STYLE.items()
            },
            "sha256": __import__("hashlib").sha256(text.encode("utf-8")).hexdigest(),
        })
    unique_by_hash = {}
    for witness in witnesses:
        unique_by_hash.setdefault(witness["sha256"], witness)
    total_words = sum(w["words"] for w in witnesses)
    unique_content_words = sum(w["words"] for w in unique_by_hash.values())
    motif_docs = Counter()
    motif_hits = Counter()
    families = Counter()
    fine = Counter()
    dates = Counter()
    refs = Counter()
    for w in witnesses:
        families[w["family"]] += 1
        fine[w["fine_family"]] += 1
        if w["date"]:
            dates[w["date"]] += 1
        for motif, hits in w["motifs"].items():
            motif_docs[motif] += 1
            motif_hits[motif] += hits
    ranked = sorted(
        witnesses,
        key=lambda w: (
            -len(w["motifs"]),
            -sum(w["motifs"].values()),
            -w["words"],
            w["path"],
        ),
    )
    # Ref membership is comparatively expensive. Resolve it only for the most
    # information-rich witnesses that will actually be shown.
    for witness in ranked[:30]:
        witness["refs"] = refs_containing(root, witness["sha"])
        for ref in witness["refs"]:
            refs[ref] += 1
    return {
        "schema": "mhac-intellectual-sediment-shadow-v1",
        "head_sha": base.head(root),
        "historical_markdown_paths": len(historical),
        "current_markdown_paths": len(current),
        "branch_or_history_only_paths": len(absent),
        "witnesses_loaded": len(witnesses),
        "unique_content_blobs": len(unique_by_hash),
        "duplicate_content_paths": len(witnesses) - len(unique_by_hash),
        "total_path_words": total_words,
        "unique_content_words": unique_content_words,
        "truncated": len(absent) > max_docs,
        "families": dict(sorted(families.items())),
        "fine_families": dict(sorted(fine.items())),
        "latest_content_dates": dict(sorted(dates.items())),
        "refs_by_witness_count": dict(refs.most_common(25)),
        "motif_documents": dict(sorted(motif_docs.items())),
        "motif_hits": dict(sorted(motif_hits.items())),
        "high_motif_witnesses": [
            {
                "path": w["path"],
                "sha": w["sha"],
                "date": w["date"],
                "refs": w["refs"][:5],
                "words": w["words"],
                "motifs": w["motifs"],
            }
            for w in ranked[:30]
        ],
        "skipped": skipped[:30],
        "interpretation_limits": [
            "A branch/history-only path is not accepted main and may be rejected, obsolete or duplicated.",
            "Latest reachable add/modify blob is a witness, not a canonical historical reconstruction.",
            "Git refs are repository mechanics, not independent intellectual contributors.",
            "Open PR branches can share copied templates or common ancestors.",
            "Motif counts are lexical and analyst-declared; they do not establish conceptual genealogy.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--json", type=Path)
    p.add_argument("--max-docs", type=int, default=400)
    p.add_argument("--print-ci-summary", action="store_true")
    args = p.parse_args()
    result = analyze_shadow(args.root, args.max_docs)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if args.print_ci_summary:
        compact = {
            k: result[k]
            for k in (
                "head_sha", "historical_markdown_paths", "current_markdown_paths",
                "branch_or_history_only_paths", "witnesses_loaded",
                "unique_content_blobs", "duplicate_content_paths",
                "total_path_words", "unique_content_words", "truncated",
                "families", "fine_families", "latest_content_dates",
                "refs_by_witness_count", "motif_documents", "motif_hits",
                "high_motif_witnesses",
            )
        }
        print("MHAC_X004_SHADOW=" + json.dumps(compact, sort_keys=True))
    elif not args.json:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
