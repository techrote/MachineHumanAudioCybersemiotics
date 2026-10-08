"""Verify all retained payload SHA-256 digests. Run before creating rerun output here."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys


def main() -> int:
    root = Path(__file__).resolve().parent
    expected = {}
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        path = (root / name).resolve()
        if not path.is_relative_to(root) or name in expected:
            raise ValueError("Unsafe or duplicate manifest path")
        expected[name] = digest
    errors = []
    for name, digest in expected.items():
        path = root / name
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(name)
    extras = sorted(str(p.relative_to(root)) for p in root.rglob("*")
                    if p.is_file() and str(p.relative_to(root)) not in expected and p.name != "SHA256SUMS")
    if errors or extras:
        print({"failed_or_missing": errors, "extra_files": extras})
        return 1
    print(f"VERIFIED: {len(expected)} payload files; manifest excludes itself; external ZIP digest covers it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
