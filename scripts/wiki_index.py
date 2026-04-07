#!/usr/bin/env python3
"""Wiki index generator + search + lint.

Usage:
  python scripts/wiki_index.py              # regenerate _index.json + overview.md
  python scripts/wiki_index.py --search Q   # search for keyword Q across all pages
  python scripts/wiki_index.py --lint       # health check (broken links, orphans, stale)
  python scripts/wiki_index.py --stats      # quick stats

This is the minimal version. Customize freely.

Adapted from a working private wiki (~700 lines) — this template strips
domain-specific logic and keeps only the essentials.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout/stderr (Windows console default is GBK, breaks Chinese output)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

# Resolve wiki dir relative to this script's parent
SCRIPT_DIR = Path(__file__).resolve().parent
WIKI_DIR = SCRIPT_DIR.parent / "wiki"
INDEX_JSON = WIKI_DIR / "_index.json"
OVERVIEW_MD = WIKI_DIR / "overview.md"

# Files / dirs to exclude from indexing
EXCLUDED_FILES = {"_schema.md", "_log.md", "_index.json", "overview.md", "inbox-digest.md"}
EXCLUDED_DIRS = {"raw", "_template"}

# Files to skip in lint (templates and examples have intentional placeholder wikilinks)
LINT_SKIP_PATTERNS = ("_template", "EXAMPLE")

# Root-level meta files don't need inbound wikilinks (LLM finds them via schema)
ROOT_META_FILES = {"rules.md", "false-beliefs.md", "inbox-digest.md", "overview.md"}

# Stale threshold (days). Pages with confidence: high but not updated in this window are flagged.
STALE_DAYS = 90


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter into a dict. Supports strings, lists, simple types."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    block = content[3:end].strip()
    out = {}
    for line in block.split("\n"):
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [x.strip().strip("'\"") for x in value[1:-1].split(",") if x.strip()]
            out[key] = items
        else:
            out[key] = value.strip("'\"")
    return out


def extract_wikilinks(content: str) -> list[str]:
    """Find all [[wikilinks]] in content. Strips display text after |.

    Ignores wikilinks inside fenced code blocks and inline code spans —
    those are usually template/example placeholders, not real links.
    """
    # Strip fenced code blocks ```...```
    content = re.sub(r"```[\s\S]*?```", "", content)
    # Strip inline code spans `...`
    content = re.sub(r"`[^`\n]*`", "", content)
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)


def iter_pages():
    """Yield (relative_path, content) for every indexable .md page in wiki/."""
    if not WIKI_DIR.exists():
        log(f"ERROR: wiki dir not found at {WIKI_DIR}")
        sys.exit(1)
    for path in WIKI_DIR.rglob("*.md"):
        rel = path.relative_to(WIKI_DIR)
        if path.name in EXCLUDED_FILES:
            continue
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            log(f"WARN: could not read {rel}: {e}")
            continue
        yield rel, content


def build_index() -> dict:
    """Walk wiki/, parse frontmatter, return index dict."""
    pages = []
    by_type = {}
    by_domain = {}
    all_links = {}  # link_target → list of pages that link to it

    for rel, content in iter_pages():
        fm = parse_frontmatter(content)
        links = extract_wikilinks(content)
        page = {
            "path": str(rel).replace("\\", "/"),
            "title": fm.get("title", rel.stem),
            "type": fm.get("type", "unknown"),
            "domain": fm.get("domain", []),
            "created": fm.get("created", ""),
            "updated": fm.get("updated", ""),
            "confidence": fm.get("confidence", "unknown"),
            "outbound_links": links,
        }
        pages.append(page)
        by_type.setdefault(page["type"], []).append(page["path"])
        domains = page["domain"] if isinstance(page["domain"], list) else [page["domain"]]
        for d in domains:
            by_domain.setdefault(d, []).append(page["path"])
        for link in links:
            all_links.setdefault(link, []).append(page["path"])

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_pages": len(pages),
        "pages": pages,
        "by_type": by_type,
        "by_domain": by_domain,
        "inbound_links": all_links,
    }


def write_index(index: dict) -> None:
    INDEX_JSON.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Wrote {INDEX_JSON.relative_to(SCRIPT_DIR.parent)} ({index['total_pages']} pages)")


def write_overview(index: dict) -> None:
    """Generate human-readable overview.md."""
    lines = ["---", "title: Wiki Overview", "type: meta", f"updated: {datetime.now().date()}", "---", ""]
    lines.append("# Wiki Overview")
    lines.append("")
    lines.append(f"_Generated by `scripts/wiki_index.py`. {index['total_pages']} pages total._")
    lines.append("")
    for page_type in sorted(index["by_type"].keys()):
        paths = sorted(index["by_type"][page_type])
        lines.append(f"## {page_type} ({len(paths)})")
        lines.append("")
        for p in paths:
            lines.append(f"- [{p}](./{p})")
        lines.append("")
    OVERVIEW_MD.write_text("\n".join(lines), encoding="utf-8")
    log(f"Wrote {OVERVIEW_MD.relative_to(SCRIPT_DIR.parent)}")


def cmd_default():
    index = build_index()
    write_index(index)
    write_overview(index)
    log("Done.")


def cmd_search(query: str):
    """Simple substring search across page titles + content."""
    query_lower = query.lower()
    hits = []
    for rel, content in iter_pages():
        fm = parse_frontmatter(content)
        title = fm.get("title", rel.stem)
        if query_lower in title.lower() or query_lower in content.lower():
            hits.append((str(rel), title))
    log(f"Found {len(hits)} hits for '{query}':")
    for path, title in hits:
        print(f"  {path}\t{title}")


def cmd_lint():
    """Check for broken links, orphans, stale pages, missing frontmatter."""
    index = build_index()
    all_paths = {p["path"] for p in index["pages"]}
    all_titles = {p["title"]: p["path"] for p in index["pages"]}
    issues = {"broken_links": [], "orphans": [], "missing_frontmatter": [], "stale_high_confidence": []}

    for page in index["pages"]:
        # Skip templates and EXAMPLE pages — they have intentional placeholder content
        if any(pat in page["path"] for pat in LINT_SKIP_PATTERNS):
            continue

        # Missing frontmatter
        if page["type"] == "unknown":
            issues["missing_frontmatter"].append(page["path"])
            continue

        # Broken outbound links
        for link in page["outbound_links"]:
            # Try matching by title or by path stem
            link_clean = link.split("/")[-1].replace(".md", "")
            matched = (
                link in all_titles
                or any(link_clean == p["title"] for p in index["pages"])
                or any(link_clean in p["path"] for p in index["pages"])
            )
            if not matched:
                issues["broken_links"].append(f"{page['path']} → [[{link}]]")

        # Orphans (no inbound or outbound links).
        # Exempt: root meta files + any README.md (READMEs are entry points, not nodes).
        page_name = page["path"].split("/")[-1]
        if page["path"] not in ROOT_META_FILES and page_name != "README.md":
            inbound = index["inbound_links"].get(page["title"], [])
            if not inbound and not page["outbound_links"]:
                issues["orphans"].append(page["path"])

        # Stale high-confidence pages
        if page["confidence"] == "high" and page["updated"]:
            try:
                updated = datetime.strptime(page["updated"], "%Y-%m-%d")
                age_days = (datetime.now() - updated).days
                if age_days > STALE_DAYS:
                    issues["stale_high_confidence"].append(f"{page['path']} (last updated {age_days}d ago)")
            except ValueError:
                pass

    # Report
    print("=" * 60)
    print("Wiki Lint Report")
    print("=" * 60)
    for category, items in issues.items():
        print(f"\n{category} ({len(items)}):")
        for item in items[:20]:
            print(f"  - {item}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")

    total = sum(len(v) for v in issues.values())
    print("\n" + "=" * 60)
    print(f"Total issues: {total}")
    sys.exit(0 if total == 0 else 1)


def cmd_stats():
    index = build_index()
    print(f"Total pages: {index['total_pages']}")
    print("\nBy type:")
    for t, paths in sorted(index["by_type"].items()):
        print(f"  {t}: {len(paths)}")
    print("\nBy domain:")
    for d, paths in sorted(index["by_domain"].items()):
        print(f"  {d}: {len(paths)}")


def main():
    parser = argparse.ArgumentParser(description="Wiki index + search + lint")
    parser.add_argument("--search", metavar="QUERY", help="Search pages by keyword")
    parser.add_argument("--lint", action="store_true", help="Run health check")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    args = parser.parse_args()

    if args.search:
        cmd_search(args.search)
    elif args.lint:
        cmd_lint()
    elif args.stats:
        cmd_stats()
    else:
        cmd_default()


if __name__ == "__main__":
    main()
