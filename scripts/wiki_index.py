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
from datetime import datetime, timedelta
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
EXCLUDED_FILES = {"_schema.md", "_log.md", "_index.json", "overview.md", "inbox-digest.md", "inbox-archive.md", "_attention.md", "_protocols.md", "_template.md"}
EXCLUDED_DIRS = {"raw", "_template"}
EXCLUDED_PATHS = {"decisions/README.md"}

# Scaffolding pages have intentional placeholder links and should not affect health metrics.
SCAFFOLD_SKIP_PATTERNS = ("_template", "EXAMPLE")
LINT_SKIP_PATTERNS = SCAFFOLD_SKIP_PATTERNS

# Root-level meta files don't need inbound wikilinks (LLM finds them via schema)
ROOT_META_FILES = {"rules.md", "false-beliefs.md", "inbox-digest.md", "overview.md"}

# Stale threshold (days). Pages with confidence: high but not updated in this window are flagged.
STALE_DAYS = 90

# New scaffold pages are often intentionally isolated for a few days.
FRESH_PAGE_DAYS = 7

# Report thresholds (--report mode)
REPORT_LONELY_DAYS = 14         # "lonely recents" = created within this window with 0 inbound
REPORT_HUB_FAN_OUT = 4          # min distinct outbound targets to qualify as a hub source
REPORT_HUB_TYPE_SPAN = 2        # min distinct types those targets must span

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
        if rel.as_posix() in EXCLUDED_PATHS:
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


def display_title(page: dict) -> str:
    """Best human-readable name for a page.

    Falls back to parent directory for entity-style pages whose title is just
    'profile' / 'tracker' / 'notes'.
    """
    title = str(page.get("title", "")).strip()
    if title and title not in {"profile", "tracker", "notes"}:
        return title
    parent = PurePosixPath(page["path"]).parent.name
    return parent or PurePosixPath(page["path"]).stem


def is_skipped_for_report(page: dict) -> bool:
    """Skip scaffolding pages from report metrics."""
    return (
        any(pattern in page["path"] for pattern in SCAFFOLD_SKIP_PATTERNS)
        or page["path"] in EXCLUDED_PATHS
    )


def cmd_report():
    """Generate attention/structure report (god nodes, concentration, hubs, lonely recents).

    Inspired by Graphify's GRAPH_REPORT.md. Pure graph computation, zero LLM.

    Outputs:
      - JSON to stdout (machine-readable, for downstream tools)
      - wiki/_attention.md (human-readable, for skim review)
    """
    index = build_index()
    pages = [p for p in index["pages"] if not is_skipped_for_report(p)]
    pages_by_path = {p["path"]: p for p in pages}
    # Filter inbound links to only count ones from non-skipped pages and pointing to non-skipped pages
    inbound_links = {
        path: [src for src in srcs if src in pages_by_path]
        for path, srcs in index["inbound_links"].items()
        if path in pages_by_path
    }

    today = datetime.now()
    cutoff_lonely = (today - timedelta(days=REPORT_LONELY_DAYS)).strftime("%Y-%m-%d")

    # ----- god nodes (top 15 by inbound count) -----
    god_nodes = []
    for path in sorted(inbound_links, key=lambda p: len(inbound_links[p]), reverse=True):
        sources = inbound_links[path]
        if not sources:
            continue
        if len(god_nodes) >= 15:
            break
        page = pages_by_path.get(path)
        if not page:
            continue
        god_nodes.append({
            "path": path,
            "title": display_title(page),
            "type": page.get("type", ""),
            "inbound_count": len(sources),
        })

    # ----- attention concentration (top 5 share) -----
    all_counts = sorted((len(s) for s in inbound_links.values()), reverse=True)
    total_inbound = sum(all_counts)
    top5_inbound = sum(all_counts[:5])
    concentration = {
        "top5_share_pct": round(100 * top5_inbound / total_inbound, 1) if total_inbound else 0,
        "top5_count": top5_inbound,
        "total_count": total_inbound,
    }

    # ----- hub sources (high fan-out, cross-type) -----
    # A "hub source" is a source-summary whose resolved outbound spans many distinct
    # pages and at least 2 types. Often a survey-style report or a multi-company interview.
    hub_sources = []
    for page in pages:
        if page.get("type") != "source-summary":
            continue
        targets = set(page.get("resolved_outbound_links", []))
        if len(targets) < REPORT_HUB_FAN_OUT:
            continue
        target_types = {pages_by_path[t]["type"] for t in targets if t in pages_by_path}
        if len(target_types) < REPORT_HUB_TYPE_SPAN:
            continue
        hub_sources.append({
            "path": page["path"],
            "title": display_title(page),
            "fan_out": len(targets),
            "spans_types": sorted(t for t in target_types if t),
            "inbound_count": len(inbound_links.get(page["path"], [])),
        })
    hub_sources.sort(key=lambda b: (-b["fan_out"], b["inbound_count"]))

    # ----- lonely recents (recently created, zero inbound) -----
    lonely_recents = []
    for page in pages:
        created = page.get("created", "")
        if not created or str(created) < cutoff_lonely:
            continue
        if len(inbound_links.get(page["path"], [])) > 0:
            continue
        lonely_recents.append({
            "path": page["path"],
            "title": display_title(page),
            "type": page.get("type", ""),
            "created": created,
        })
    lonely_recents.sort(key=lambda x: x["created"], reverse=True)

    # ----- top concepts by source-reference count -----
    concept_pages = [p for p in pages if p.get("type") == "concept"]
    source_pages = [p for p in pages if p.get("type") == "source-summary"]
    concept_source_count = []
    for cp in concept_pages:
        cp_path = cp["path"]
        count = sum(1 for sp in source_pages if cp_path in sp.get("resolved_outbound_links", []))
        if count > 0:
            concept_source_count.append({
                "path": cp_path,
                "title": display_title(cp),
                "source_count": count,
            })
    concept_source_count.sort(key=lambda c: -c["source_count"])

    summary = {
        "top_god_node": (
            f"{god_nodes[0]['title']} ({god_nodes[0]['type']}, {god_nodes[0]['inbound_count']} inbound)"
        ) if god_nodes else None,
        "concentration_pct": concentration["top5_share_pct"],
        "hub_sources_count": len(hub_sources),
        "lonely_recents_count": len(lonely_recents),
        "top_concept": (
            f"{concept_source_count[0]['title']} ({concept_source_count[0]['source_count']} sources)"
        ) if concept_source_count else None,
    }

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "god_nodes": god_nodes,
        "concentration": concentration,
        "hub_sources": hub_sources[:10],
        "lonely_recents": lonely_recents,
        "top_concepts_by_source_count": concept_source_count[:10],
    }

    write_attention_md(report)
    log(
        f"Report: concentration {summary['concentration_pct']}% | "
        f"hub sources {summary['hub_sources_count']} | "
        f"lonely recents {summary['lonely_recents_count']}"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def write_attention_md(report: dict) -> None:
    """Render the report as wiki/_attention.md (human-readable companion to the JSON)."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "---",
        "title: Wiki Attention Report",
        "type: meta",
        f"updated: {today}",
        "---",
        "",
        "# Wiki Attention Report",
        "",
        f"> Auto-generated {today}. Refresh: `python scripts/wiki_index.py --report`",
        "",
        "## Concentration",
        "",
        f"- Top 5 inbound share: **{report['concentration']['top5_share_pct']}%** "
        f"({report['concentration']['top5_count']} / {report['concentration']['total_count']})",
        "",
        "## God nodes (top 15 by inbound count)",
        "",
        "| # | Title | Type | Inbound |",
        "|---|-------|------|---------|",
    ]
    if not report["god_nodes"]:
        lines.append("| _ | _none_ | _ | _ |")
    for i, n in enumerate(report["god_nodes"], 1):
        link = f"[[{n['path'].removesuffix('.md')}|{n['title']}]]"
        lines.append(f"| {i} | {link} | {n['type']} | {n['inbound_count']} |")

    lines += [
        "",
        f"## Hub sources (fan-out >= {REPORT_HUB_FAN_OUT}, spans >= {REPORT_HUB_TYPE_SPAN} types)",
        "",
        "> One source connecting many entities/concepts — likely a survey-style report",
        "> or multi-company interview worth backlinking from each touched page.",
        "",
        "| Source | fan-out | spans types | inbound |",
        "|--------|---------|-------------|---------|",
    ]
    if not report["hub_sources"]:
        lines.append("| _none_ | _ | _ | _ |")
    for h in report["hub_sources"]:
        link = f"[[{h['path'].removesuffix('.md')}|{h['title']}]]"
        spans = ", ".join(h["spans_types"])
        lines.append(f"| {link} | {h['fan_out']} | {spans} | {h['inbound_count']} |")

    lines += [
        "",
        f"## Lonely recents (< {REPORT_LONELY_DAYS}d old, 0 inbound)",
        "",
        "| Title | Type | Created |",
        "|-------|------|---------|",
    ]
    if not report["lonely_recents"]:
        lines.append("| _none_ | _ | _ |")
    for n in report["lonely_recents"]:
        link = f"[[{n['path'].removesuffix('.md')}|{n['title']}]]"
        lines.append(f"| {link} | {n['type']} | {n['created']} |")

    lines += [
        "",
        "## Concepts ranked by source-reference count",
        "",
        "| Title | Sources referencing |",
        "|-------|---------------------|",
    ]
    if not report["top_concepts_by_source_count"]:
        lines.append("| _none_ | _ |")
    for c in report["top_concepts_by_source_count"]:
        link = f"[[{c['path'].removesuffix('.md')}|{c['title']}]]"
        lines.append(f"| {link} | {c['source_count']} |")

    out_path = WIKI_DIR / "_attention.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"Wrote {out_path.relative_to(SCRIPT_DIR.parent)}")


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
    parser = argparse.ArgumentParser(description="Wiki index + search + lint + report")
    parser.add_argument("--search", metavar="QUERY", help="Search pages by keyword")
    parser.add_argument("--lint", action="store_true", help="Run health check")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--report", action="store_true",
                        help="Generate attention report (god nodes, hub sources, lonely recents)")
    args = parser.parse_args()

    if args.search:
        cmd_search(args.search)
    elif args.lint:
        cmd_lint()
    elif args.stats:
        cmd_stats()
    elif args.report:
        cmd_report()
    else:
        cmd_default()


if __name__ == "__main__":
    main()
