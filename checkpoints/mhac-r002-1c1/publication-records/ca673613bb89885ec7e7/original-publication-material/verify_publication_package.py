#!/usr/bin/env python3
"""Verify this archival package offline. Never executes research code or pushes Git refs."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_id(kind: str, data: bytes) -> str:
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def safe_path(name: str) -> str:
    path = PurePosixPath(name)
    require(bool(name) and not path.is_absolute() and ".." not in path.parts
            and "\\" not in name and "\x00" not in name, "Unsafe path: " + repr(name))
    return name


def manifest(data: bytes) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in data.decode("utf-8").splitlines():
        digest, name = line.split("  ", 1)
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "Bad checksum")
        safe_path(name)
        require(name not in result, "Duplicate manifest path: " + name)
        result[name] = digest
    return result


def check_directory(root: Path, name: str) -> dict[str, str]:
    expected = manifest((root / name).read_bytes())
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(actual == set(expected) | {name}, "Directory inventory mismatch: " + str(root))
    for rel, digest in expected.items():
        p = root / rel
        require(not p.is_symlink(), "Symlink not permitted: " + rel)
        require(sha256(p.read_bytes()) == digest, "Checksum mismatch: " + rel)
    return expected


def check_archive(data: bytes, top: str) -> tuple[dict[str, bytes], int]:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)), "Duplicate ZIP members")
        require(archive.testzip() is None, "ZIP CRC failure")
        require(all(n.startswith(top + "/") for n in names), "Unexpected archive root")
        require(all(not i.is_dir() and ((i.external_attr >> 16) & 0o170000) != 0o120000
                    for i in infos), "Unexpected ZIP member type")
        files = {safe_path(n[len(top) + 1:]): archive.read(n) for n in names}
    sums = manifest(files["SHA256SUMS"])
    require(set(files) == set(sums) | {"SHA256SUMS"}, "Archive inventory mismatch")
    for name, digest in sums.items():
        require(sha256(files[name]) == digest, "Archive checksum mismatch: " + name)
    return files, len(sums)


def run_git(git_dir: Path, *args: str) -> bytes:
    completed = subprocess.run(["git", "--git-dir=" + str(git_dir), *args],
                               capture_output=True, timeout=30, check=False)
    require(completed.returncode == 0,
            "Git command failed: " + " ".join(args) + "\n" + completed.stderr.decode(errors="replace"))
    return completed.stdout


def put_object(git_dir: Path, kind: str, data: bytes) -> str:
    raw = kind.encode() + b" " + str(len(data)).encode() + b"\0" + data
    oid = hashlib.sha1(raw).hexdigest()
    p = git_dir / "objects" / oid[:2] / oid[2:]
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(zlib.compress(raw))
    return oid


def verify_git(root: Path, plan: dict, saved_root: Path) -> dict:
    require(shutil.which("git") is not None, "Git is required for --git")
    with tempfile.TemporaryDirectory(prefix="mhac-checkpoint-verify-") as temporary:
        g = Path(temporary) / "verification.git"
        p = subprocess.run(["git", "init", "--bare", str(g)], capture_output=True, timeout=30)
        require(p.returncode == 0, "Could not initialize disposable Git object store")
        original_commit = (root / "provenance/BASE-COMMIT.raw").read_bytes()
        require(put_object(g, "commit", original_commit) == plan["parent"], "Base commit identity mismatch")
        base_info = json.loads((root / "provenance/BASE-TREE-VERIFICATION.json").read_text(encoding="utf-8"))
        with (root / "provenance/BASE-BLOB-INVENTORY.csv").open(encoding="utf-8", newline="") as f:
            inventory = list(csv.DictReader(f))
        entries: dict = {}
        for row in inventory:
            require(row["commit"] == plan["parent"], "Source inventory pin mismatch")
            parts = safe_path(row["path"]).split("/")
            node = entries
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = (row["mode"], row["reported_git_blob_sha1"])

        def make_tree(node: dict, path: str = "") -> str:
            children = []
            for name, value in node.items():
                if isinstance(value, dict):
                    mode = "40000"
                    oid = make_tree(value, (path + "/" + name).lstrip("/"))
                else:
                    mode, oid = value
                children.append((name, mode, oid))
            children.sort(key=lambda x: (x[0] + ("/" if x[1] == "40000" else "")).encode())
            data = b"".join(mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(oid)
                            for name, mode, oid in children)
            oid = put_object(g, "tree", data)
            require(oid == base_info["tree_objects_verified_against_live_api"][path],
                    "Base tree metadata mismatch: " + path)
            return oid

        require(make_tree(entries) == plan["base_tree"], "Base root mismatch")
        # This is a verification fixture with exact base metadata, not a full source clone.
        (g / "shallow").write_text(plan["parent"] + "\n", encoding="ascii")
        run_git(g, "update-ref", "refs/heads/source-base", plan["parent"])
        bundle = root / plan["bundle"]
        run_git(g, "bundle", "verify", str(bundle))
        run_git(g, "bundle", "unbundle", str(bundle))
        run_git(g, "update-ref", "refs/heads/" + plan["branch"], plan["commit"])
        require(run_git(g, "rev-parse", "refs/heads/" + plan["branch"]).decode().strip()
                == plan["commit"], "Imported local ref mismatch")
        require(run_git(g, "show", "-s", "--format=%P", plan["commit"]).decode().strip()
                == plan["parent"], "Parent mismatch")
        base_paths = run_git(g, "ls-tree", "-r", plan["parent"]).decode().splitlines()
        new_paths = run_git(g, "ls-tree", "-r", plan["commit"]).decode().splitlines()
        require(set(base_paths).issubset(set(new_paths)), "Original tree changed")
        changes = run_git(g, "diff-tree", "--no-commit-id", "--name-status", "-r",
                          plan["parent"], plan["commit"]).decode().splitlines()
        saved = sorted(p for p in saved_root.rglob("*") if p.is_file())
        expected_paths = {plan["directory"] + "/" + p.relative_to(saved_root).as_posix() for p in saved}
        require(set(changes) == {"A\t" + name for name in expected_paths}, "Non-additive or unexpected changes")
        for path in saved:
            rel = path.relative_to(saved_root).as_posix()
            received = run_git(g, "cat-file", "blob", plan["commit"] + ":" + plan["directory"] + "/" + rel)
            require(received == path.read_bytes(), "Imported byte mismatch: " + rel)
        indexes = list((g / "objects/pack").glob("*.idx"))
        require(len(indexes) == 1, "Expected exactly one imported pack")
        run_git(g, "verify-pack", "-v", str(indexes[0]))
        return {"bundle_import": "PASS", "saved_blobs_byte_verified": len(saved),
                "unchanged_original_source_identities": len(base_paths),
                "changes_outside_checkpoint": 0,
                "verification_fixture": "Exact base commit/tree metadata only; no full source checkout or source-history fsck."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--git", action="store_true", help="Exercise isolated incremental-bundle import")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        outer = check_directory(root, "SHA256SUMS")
        plan = json.loads((root / "PUBLICATION-PLAN.json").read_text(encoding="utf-8"))
        saved = root / safe_path(plan["payload_root"])
        sums = check_directory(saved, "SAVED-PAYLOAD.sha256")
        identity_bytes = (saved / "ORIGINAL-PAYLOAD.sha256").read_bytes()
        require(sha256(identity_bytes) == plan["payload_identity_sha256"], "Payload identity mismatch")
        require(sha256(identity_bytes)[:20] == plan["payload_id"], "Payload ID mismatch")
        originals = manifest(identity_bytes)
        for name, digest in originals.items():
            require(sha256((saved / name).read_bytes()) == digest, "Historical file mismatch: " + name)
        c_bytes = (saved / "originals/MHAC_R002_chunk1C1_packet_2026-10-04.zip").read_bytes()
        c_receipt = json.loads((saved / "originals/MHAC_R002_chunk1C1_archive_verification.json").read_bytes())
        require(sha256(c_bytes) == c_receipt["archive_sha256"], "1C1 receipt mismatch")
        c, cn = check_archive(c_bytes, "MHAC_R002_chunk1C1")
        require(c["CHECKPOINT.md"] == (saved / "originals/CHECKPOINT.md").read_bytes(), "Standalone checkpoint mismatch")
        for name, data in c.items():
            require(data == (saved / "packet/MHAC_R002_chunk1C1" / name).read_bytes(), "Extracted packet mismatch")
        b_bytes = c["inputs/MHAC_R002_chunk1B_packet_2026-10-04.zip"]
        require(sha256(b_bytes) == json.loads(c["inputs/MHAC_R002_chunk1B_archive_verification.json"])["archive_sha256"], "1B receipt mismatch")
        b, bn = check_archive(b_bytes, "MHAC_R002_chunk1B")
        a_bytes = b["inputs/MHAC_R002_chunk1A_packet_2026-10-04.zip"]
        require(sha256(a_bytes) == json.loads(b["inputs/MHAC_R002_chunk1A_archive_verification.json"])["archive_sha256"], "1A receipt mismatch")
        a, an = check_archive(a_bytes, "MHAC_R002_chunk1A")
        for item in json.loads(c["provenance/PRIOR_COPY_IDENTITIES.json"]):
            previous = {"1A": a, "1B": b}[item["packet"]]
            rel = item["original_member"].split("/", 1)[1]
            require(c[item["local_copy"]] == previous[rel], "Selected prior-copy mismatch")
        bundle = (root / plan["bundle"]).read_bytes()
        require(sha256(bundle) == plan["bundle_sha256"], "Bundle SHA-256 mismatch")
        header, pack = bundle.split(b"\n\n", 1)
        require(header.startswith(b"# v2 git bundle\n"), "Unsupported bundle header")
        require(("-" + plan["parent"] + " ").encode() in header, "Missing base prerequisite")
        require((plan["commit"] + " refs/heads/" + plan["branch"]).encode() in header, "Bundle ref mismatch")
        require(pack.startswith(b"PACK") and hashlib.sha1(pack[:-20]).digest() == pack[-20:], "Git pack checksum mismatch")
        require(git_id("commit", (root / "provenance/CHECKPOINT-COMMIT.raw").read_bytes()) == plan["commit"], "Raw checkpoint commit mismatch")
        require(git_id("commit", (root / "provenance/BASE-COMMIT.raw").read_bytes()) == plan["parent"], "Raw base commit mismatch")
        result = {"status": "PASS", "scope": "Offline archive/Git transport integrity only; not research acceptance or remote publication.",
                  "outer_files_hashed": len(outer), "saved_files": len(sums) + 1,
                  "historical_files": len(originals), "historical_manifest_hashes": cn + bn + an,
                  "bundle_sha256": plan["bundle_sha256"], "commit": plan["commit"],
                  "git_base_prerequisite": plan["parent"], "remote_writes": 0, "research_code_executed": False}
        if args.git:
            result["git_verification"] = verify_git(root, plan, saved)
        else:
            result["git_verification"] = "Not requested; add --git for isolated Git import."
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
