#!/usr/bin/env python3
"""Preflight checks before publishing a public repo.

The check scans files that would be visible in Git and blocks common leaks:
- real-looking API keys or access tokens
- local machine / sync-drive traces
- user data directories such as reports, output, raw materials, or portfolios
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".env",
    ".example",
    ".ini",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{24,})"),
]

LOCAL_TRACE_PATTERNS = [
    re.compile(r"BaiduSyncdisk", re.IGNORECASE),
    re.compile(r"\.baiduyun\.(uploading|downloading)\.cfg", re.IGNORECASE),
    re.compile(r"冲突文件"),
    re.compile(r"ASUS@|LAPTOP-", re.IGNORECASE),
]

FORBIDDEN_PATH_PARTS = {
    ".env",
    ".ruff_cache",
    "__pycache__",
    ".pytest_cache",
    "daily-watchlist-reports",
    "output",
    "reports",
    "wiki/raw",
}

FORBIDDEN_FILENAMES = {
    "holdings.csv",
    "trades.csv",
    "config.yaml",
}

PLACEHOLDER_MARKERS = {
    "your_api_key",
    "your_fmp_api_key",
    "your_fmp_key",
    "your_key_here",
    "your_deepseek_api_key_here",
    "sk-xxx",
    "sk-xxxxxxxx",
    "provider-specific-test-key",
}


def repo_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return [root / line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]


def is_placeholder(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS) or re.search(
        r"sk-x{8,}", lowered
    )


def is_documented_safety_line(rel: str, line: str) -> bool:
    """Allow docs/code that describe ignore rules for local artifacts."""
    if rel in {".gitignore", "CHANGELOG.md", "CONTRIBUTING.md", "scripts/preflight_public_repo.py"}:
        return True
    return "SKIP_PATTERNS" in line or "Skipping conflict/version artifact" in line


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {".gitignore", "LICENSE"}


def check_path(root: Path, path: Path) -> list[str]:
    rel = path.relative_to(root).as_posix()
    lowered = rel.lower()
    findings: list[str] = []

    if path.name in FORBIDDEN_FILENAMES and not lowered.startswith(("examples/", "templates/")):
        findings.append(f"{rel}: user data filename should not be tracked")

    for part in FORBIDDEN_PATH_PARTS:
        if part in lowered and not rel.endswith(".gitkeep"):
            if ".example" not in lowered and "sample" not in lowered:
                findings.append(f"{rel}: local/generated/private path should not be tracked")

    return findings


def check_text(root: Path, path: Path) -> list[str]:
    if not is_text_file(path):
        return []
    rel = path.relative_to(root).as_posix()
    findings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_placeholder(line):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(f"{rel}:{lineno}: possible secret")
                break
        for pattern in LOCAL_TRACE_PATTERNS:
            if is_documented_safety_line(rel, line):
                continue
            if pattern.search(line):
                findings.append(f"{rel}:{lineno}: local machine or sync-drive trace")
                break
    return findings


def run(root: Path) -> int:
    findings: list[str] = []
    for path in repo_files(root):
        if not path.exists() or ".git" in path.parts:
            continue
        findings.extend(check_path(root, path))
        findings.extend(check_text(root, path))

    if findings:
        print("Public repo preflight failed:", file=sys.stderr)
        for item in findings:
            print(f"  - {item}", file=sys.stderr)
        return 1

    print("Public repo preflight passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan")
    args = parser.parse_args()
    return run(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
