#!/usr/bin/env python3
"""Scan wiki/raw and optional Obsidian Clippings folders for ingest candidates."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".pdf",
    ".html",
    ".htm",
    ".mhtml",
    ".docx",
}

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
WIKI_RAW_DIR = REPO_ROOT / "wiki" / "raw"
DEFAULT_SEARCH_ROOTS = (
    Path.home() / "Documents",
    Path.home() / "Desktop",
    Path.home() / "OneDrive" / "Documents",
    Path.home() / "OneDrive",
)


@dataclass
class Candidate:
    path: str
    relative_path: str
    source_root: str
    source_kind: str
    modified_at: str


def ensure_utf8() -> None:
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")


def file_timestamp(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")
    except OSError:
        return ""


def iter_supported_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        files.append(path)
    return sorted(files, key=lambda item: (item.stat().st_mtime, str(item).lower()), reverse=True)


def build_candidates(root: Path, source_kind: str, limit: int | None) -> list[Candidate]:
    files = iter_supported_files(root)
    if limit is not None:
        files = files[:limit]
    return [
        Candidate(
            path=str(path.resolve()),
            relative_path=str(path.relative_to(root)).replace("\\", "/"),
            source_root=str(root.resolve()),
            source_kind=source_kind,
            modified_at=file_timestamp(path),
        )
        for path in files
    ]


def obsidian_installed() -> bool:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    roaming_app_data = Path(os.environ.get("APPDATA", ""))
    candidates = (
        local_app_data / "Programs" / "Obsidian" / "Obsidian.exe",
        local_app_data / "Obsidian" / "Obsidian.exe",
        roaming_app_data / "obsidian",
    )
    return any(path.exists() for path in candidates)


def discover_obsidian_clippings() -> list[Path]:
    seen: set[str] = set()
    candidates: list[Path] = []

    if not obsidian_installed():
        return candidates

    for root in DEFAULT_SEARCH_ROOTS:
        if not root.exists():
            continue

        for obsidian_dir in root.rglob(".obsidian"):
            vault_root = obsidian_dir.parent
            clipping_dir = vault_root / "Clippings"
            if clipping_dir.is_dir():
                key = str(clipping_dir.resolve()).lower()
                if key not in seen:
                    seen.add(key)
                    candidates.append(clipping_dir.resolve())

        for clipping_dir in root.rglob("Clippings"):
            if not clipping_dir.is_dir():
                continue
            if ".obsidian" not in {child.name for child in clipping_dir.parent.iterdir() if child.is_dir()}:
                continue
            key = str(clipping_dir.resolve()).lower()
            if key not in seen:
                seen.add(key)
                candidates.append(clipping_dir.resolve())

    return sorted(candidates)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan wiki/raw and optional Obsidian Clippings for ingest candidates.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--limit", type=int, default=None, help="Limit results per source root.")
    parser.add_argument(
        "--include-obsidian-clippings",
        action="store_true",
        help="Auto-discover Obsidian Clippings folders and include them when found.",
    )
    parser.add_argument(
        "--obsidian-clippings-path",
        type=Path,
        default=None,
        help="Scan a specific Obsidian Clippings directory.",
    )
    return parser.parse_args()


def main() -> int:
    ensure_utf8()
    args = parse_args()

    result = {
        "raw_root": str(WIKI_RAW_DIR.resolve()),
        "raw_candidates": [asdict(item) for item in build_candidates(WIKI_RAW_DIR, "raw", args.limit)],
        "obsidian_clippings_roots": [],
        "obsidian_candidates": [],
    }

    clipping_roots: list[Path] = []
    if args.obsidian_clippings_path:
        if args.obsidian_clippings_path.is_dir():
            clipping_roots = [args.obsidian_clippings_path.resolve()]
    elif args.include_obsidian_clippings:
        clipping_roots = discover_obsidian_clippings()

    result["obsidian_clippings_roots"] = [str(path) for path in clipping_roots]
    for root in clipping_roots:
        result["obsidian_candidates"].extend(
            asdict(item) for item in build_candidates(root, "obsidian-clippings", args.limit)
        )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"raw_root: {result['raw_root']}")
    print(f"raw_candidates: {len(result['raw_candidates'])}")
    for item in result["raw_candidates"]:
        print(f"  - {item['relative_path']} ({item['modified_at']})")

    if clipping_roots:
        print("obsidian_clippings_roots:")
        for root in clipping_roots:
            print(f"  - {root}")
        print(f"obsidian_candidates: {len(result['obsidian_candidates'])}")
        for item in result["obsidian_candidates"]:
            print(f"  - {item['relative_path']} ({item['modified_at']})")
    else:
        print("obsidian_clippings_roots: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
