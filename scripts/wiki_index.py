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
from pathlib import Path, PurePosixPath

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

# New scaffold pages are often intentionally isolated for a few days.
FRESH_PAGE_DAYS = 7

FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_scalar(value: str):
    value = value.strip().strip("'\"")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_frontmatter(content: str) -> dict:
    """Parse simple YAML frontmatter into a dict.

    Supports:
    - scalar values: `key: value`
    - inline lists: `key: [a, b]`
    - simple block lists:
        key:
          - a
          - b
    """
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}

    block = match.group(1)
    out = {}
    current_key = None

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if current_key and line[:1].isspace():
            item = stripped
            if item.startswith("- ") and isinstance(out.get(current_key), list):
                out[current_key].append(parse_scalar(item[2:].strip()))
                continue

        current_key = None
        key, sep, value = line.partition(":")
        if not sep:
            continue

        key = key.strip()
        value = value.strip()

        if not value:
            out[key] = []
            current_key = key
            continue

        if value.startswith("[") and value.endswith("]"):
            items = [parse_scalar(item) for item in value[1:-1].split(",") if item.strip()]
            out[key] = items
            continue

        out[key] = parse_scalar(value)

    return out


def extract_wikilinks(content: str) -> list[str]:
    """Find all [[wikilinks]] in content. Strips display text after |.

    Ignores wikilinks inside fenced code blocks and inline code spans —
    those are usually template/example placeholders, not real links.
    """
    content = re.sub(r"```[\s\S]*?```", "", content)
    content = re.sub(r"`[^`\n]*`", "", content)
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)


def normalize_link_target(target: str) -> str:
    return target.strip().replace("\\", "/").removesuffix(".md").strip("/")


def page_aliases(page: dict) -> set[str]:
    path = PurePosixPath(page["path"])
    path_no_ext = path.with_suffix("").as_posix()
    aliases = {
        normalize_link_target(path_no_ext),
        normalize_link_target(path.stem),
        normalize_link_target(str(page["title"])),
    }

    if path.name in {"profile.md", "tracker.md", "notes.md"}:
        aliases.add(normalize_link_target(path.parent.name))
        aliases.add(normalize_link_target(f"{path.parent.name}/{path.stem}"))
        aliases.add(normalize_link_target(path.parent.as_posix()))

    return {alias for alias in aliases if alias}


def build_link_lookup(pages: list[dict]) -> dict[str, set[str]]:
    lookup = {}
    for page in pages:
        for alias in page_aliases(page):
            lookup.setdefault(alias.lower(), set()).add(page["path"])
    return lookup


def resolve_link(link: str, lookup: dict[str, set[str]]) -> list[str]:
    return sorted(lookup.get(normalize_link_target(link).lower(), set()))


def is_fresh_page(page: dict, days: int = FRESH_PAGE_DAYS) -> bool:
    for field in ("updated", "created"):
        value = page.get(field)
        if not value:
            continue
        try:
            age_days = (datetime.now() - datetime.strptime(value, "%Y-%m-%d")).days
            return age_days <= days
        except ValueError:
            continue
    return False


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
            content = path.read_text(encoding="utf-8-sig")
        except Exception as e:
            log(f"WARN: could not read {rel}: {e}")
            continue
        yield rel, content


def build_index() -> dict:
    """Walk wiki/, parse frontmatter, return index dict."""
    pages = []
    by_type = {}
    by_domain = {}

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
        for domain in domains:
            if domain:
                by_domain.setdefault(domain, []).append(page["path"])

    link_lookup = build_link_lookup(pages)
    inbound_links = {}

    for page in pages:
        resolved = []
        for link in page["outbound_links"]:
            matches = resolve_link(link, link_lookup)
            resolved.extend(matches)
            for match in matches:
                inbound_links.setdefault(match, []).append(page["path"])
        page["resolved_outbound_links"] = sorted(set(resolved))

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_pages": len(pages),
        "pages": pages,
        "by_type": by_type,
        "by_domain": by_domain,
        "inbound_links": inbound_links,
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
        for path in paths:
            lines.append(f"- [{path}](./{path})")
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
    link_lookup = build_link_lookup(index["pages"])
    issues = {"broken_links": [], "orphans": [], "missing_frontmatter": [], "stale_high_confidence": []}

    for page in index["pages"]:
        if any(pattern in page["path"] for pattern in LINT_SKIP_PATTERNS):
            continue

        if page["type"] == "unknown":
            issues["missing_frontmatter"].append(page["path"])
            continue

        for link in page["outbound_links"]:
            if not resolve_link(link, link_lookup):
                issues["broken_links"].append(f"{page['path']} → [[{link}]]")

        page_name = PurePosixPath(page["path"]).name
        if page["path"] not in ROOT_META_FILES and page_name != "README.md":
            inbound = index["inbound_links"].get(page["path"], [])
            if not inbound and not page["resolved_outbound_links"] and not is_fresh_page(page):
                issues["orphans"].append(page["path"])

        if page["confidence"] == "high" and page["updated"]:
            try:
                updated = datetime.strptime(page["updated"], "%Y-%m-%d")
                age_days = (datetime.now() - updated).days
                if age_days > STALE_DAYS:
                    issues["stale_high_confidence"].append(f"{page['path']} (last updated {age_days}d ago)")
            except ValueError:
                pass

    print("=" * 60)
    print("Wiki Lint Report")
    print("=" * 60)
    for category, items in issues.items():
        print(f"\n{category} ({len(items)}):")
        for item in items[:20]:
            print(f"  - {item}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")

    total = sum(len(values) for values in issues.values())
    print("\n" + "=" * 60)
    print(f"Total issues: {total}")
    sys.exit(0 if total == 0 else 1)


def cmd_stats():
    index = build_index()
    print(f"Total pages: {index['total_pages']}")
    print("\nBy type:")
    for page_type, paths in sorted(index["by_type"].items()):
        print(f"  {page_type}: {len(paths)}")
    print("\nBy domain:")
    for domain, paths in sorted(index["by_domain"].items()):
        print(f"  {domain}: {len(paths)}")


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
