"""Strict offline JSON and repository-contained artifact access."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath
from typing import Any

from schemas import ValidationError


def fail(code: str, message: str) -> None:
    raise ValidationError(f"{code}: {message}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("JSON_DUPLICATE_KEY", key)
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    fail("JSON_NONFINITE", value)


def finite_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        fail("JSON_NONFINITE", value)
    return result


def loads(text: str) -> Any:
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=finite_float)


def read_json(path: Path) -> Any:
    return loads(path.read_text(encoding="utf-8"))


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + "\n"


def relative_path(value: Any) -> str:
    if (not isinstance(value, str) or not value.strip() or "\\" in value
            or ":" in value or value.startswith("/")
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        fail("PATH", f"Expected a normalized relative POSIX path: {value!r}")
    if str(PurePosixPath(value)) != value:
        fail("PATH", str(value))
    return value


def contained_path(root: Path, relative: str, *, must_exist: bool = True) -> Path:
    """Reject traversal and symlinks, including symlinked parent directories."""
    relative_path(relative)
    root = root.resolve()
    path = root
    for part in relative.split("/"):
        path = path / part
        if path.is_symlink():
            fail("SYMLINK", relative)
    if not path.resolve().is_relative_to(root):
        fail("PATH", relative)
    if must_exist and not path.exists():
        fail("MISSING_FILE", relative)
    return path


def verify_artifact(root: Path, artifact: dict[str, Any]) -> Path:
    if not isinstance(artifact, dict) or not {"path", "sha256"} <= set(artifact):
        fail("ARTIFACT", "An artifact needs path and sha256")
    path = contained_path(root, artifact["path"])
    if not path.is_file():
        fail("ARTIFACT", f"Not a regular file: {artifact['path']}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != artifact["sha256"]:
        fail("ARTIFACT_HASH", artifact["path"])
    return path
