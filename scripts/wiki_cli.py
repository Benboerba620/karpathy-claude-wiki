#!/usr/bin/env python3
"""Command-line utilities for karpathy-claude-wiki.

Primary command:
  python scripts/wiki_cli.py ingest path/to/source.md

The ingest command is intentionally pragmatic rather than magical:
- archives the raw file into wiki/raw/ when needed
- creates wiki/sources/YYYY-MM-DD-slug.md
- updates wiki/_log.md
- updates wiki/inbox-digest.md
- links existing entity/concept pages back to the new source when matches exist
- regenerates the index and runs lint unless --skip-lint is used

For large PDFs, pair it with scripts/ingest_helper.py:
  python scripts/ingest_helper.py --pdf report.pdf --out /tmp/report.json
  python scripts/wiki_cli.py ingest report.pdf --summary-json /tmp/report.json
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Iterable


for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


FRONTMATTER_RE = re.compile(r"\A(?:\ufeff)?---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


@dataclass
class WikiPage:
    path: Path
    rel_path: str
    page_type: str
    title: str
    aliases: list[str]


def parse_scalar(value: str):
    value = value.strip().strip("'\"")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_frontmatter(content: str) -> dict:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}

    block = match.group(1)
    out: dict[str, object] = {}
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


def render_frontmatter(frontmatter: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value)
            if key == "related" and rendered:
                lines.append(f"{key}: {rendered}")
            else:
                lines.append(f"{key}: [{rendered}]")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def replace_frontmatter(content: str, frontmatter: dict[str, object]) -> str:
    rendered = render_frontmatter(frontmatter)
    if FRONTMATTER_RE.match(content):
        return FRONTMATTER_RE.sub(rendered + "\n\n", content, count=1)
    return rendered + "\n\n" + content.lstrip()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    normalized = re.sub(r"[^\w\s-]", " ", normalized, flags=re.UNICODE)
    normalized = re.sub(r"[-\s]+", "-", normalized, flags=re.UNICODE).strip("-_")
    return normalized or "source"


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).strip()).casefold()


def clean_text_line(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_iso_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if re.fullmatch(r"20\d{2}-\d{2}-\d{2}", value):
        return value
    return None


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PDF ingest requires either `--summary-json`, `--use-ingest-helper`, or `pip install pypdf`."
        ) from exc

    reader = PdfReader(str(path))
    parts = []
    for index, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        parts.append(f"\n\n--- Page {index} ---\n{extracted}")
    return "".join(parts).strip()


def read_source_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return read_pdf_text(path)
    return read_text_file(path)


def extract_title_from_text(path: Path, text: str) -> str:
    frontmatter = parse_frontmatter(text)
    title = frontmatter.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return path.stem.replace("-", " ").replace("_", " ").strip() or path.stem


def extract_date_from_text(text: str) -> str | None:
    frontmatter = parse_frontmatter(text)
    for field in ("date", "published", "published_at", "created", "updated"):
        value = frontmatter.get(field)
        if isinstance(value, str) and DATE_RE.search(value):
            return DATE_RE.search(value).group(1)

    match = DATE_RE.search(text[:4000])
    return match.group(1) if match else None


def extract_author_from_text(text: str) -> str | None:
    frontmatter = parse_frontmatter(text)
    for field in ("author", "authors", "by"):
        value = frontmatter.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list) and value:
            return ", ".join(str(item) for item in value)
    return None


def extract_tldr(text: str) -> str:
    text_wo_frontmatter = FRONTMATTER_RE.sub("", text, count=1)
    for raw_line in text_wo_frontmatter.splitlines():
        line = clean_text_line(raw_line)
        if not line:
            continue
        if line.startswith(("#", "---", "```", "|", "- ", "* ")):
            continue
        if len(line) < 20:
            continue
        return line[:240]
    return "Summary pending refinement."


def extract_quotes(text: str, limit: int = 3) -> list[str]:
    quotes: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(">"):
            quote = stripped.lstrip(">").strip()
            if quote and quote not in quotes:
                quotes.append(quote[:240])
        if len(quotes) >= limit:
            return quotes

    for match in re.finditer(r'"([^"\n]{24,240})"', text):
        quote = clean_text_line(match.group(1))
        if quote and quote not in quotes:
            quotes.append(quote)
        if len(quotes) >= limit:
            break
    return quotes


def heuristic_summary(path: Path, text: str) -> dict[str, object]:
    return {
        "title": extract_title_from_text(path, text),
        "date": normalize_iso_date(extract_date_from_text(text)),
        "author": extract_author_from_text(text),
        "tldr": extract_tldr(text),
        "key_data": [],
        "quotes": extract_quotes(text),
        "implications": "Command-ingested source. Review and expand this section if the source matters.",
        "entities_mentioned": [],
        "concepts_mentioned": [],
        "verifiable_predictions": [],
        "open_questions": [],
    }


def merge_summary(base: dict[str, object], override: dict[str, object]) -> dict[str, object]:
    merged = dict(base)
    for key, value in override.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and not value:
            continue
        merged[key] = value
    return merged


def resolve_repo_root(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def detect_default_domain(wiki_dir: Path) -> str:
    candidates = [
        wiki_dir / "sources" / "EXAMPLE-source-summary.md",
        wiki_dir / "entities" / "_template" / "profile.md",
    ]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        frontmatter = parse_frontmatter(candidate.read_text(encoding="utf-8", errors="ignore"))
        domain = frontmatter.get("domain")
        if isinstance(domain, list) and domain:
            return str(domain[0])
        if isinstance(domain, str) and domain.strip():
            return domain.strip()
    return "investing"


def ensure_unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def archive_raw_file(source_path: Path, raw_dir: Path) -> tuple[Path, str]:
    source_resolved = source_path.resolve()
    raw_dir_resolved = raw_dir.resolve()

    try:
        source_resolved.relative_to(raw_dir_resolved)
        raw_path = source_resolved
    except ValueError:
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = ensure_unique_path(raw_dir / source_path.name)
        shutil.copy2(source_resolved, raw_path)

    rel = PurePosixPath("raw") / PurePosixPath(raw_path.relative_to(raw_dir_resolved).as_posix())
    return raw_path, rel.as_posix()


def discover_pages(wiki_dir: Path) -> list[WikiPage]:
    pages: list[WikiPage] = []
    for path in wiki_dir.rglob("*.md"):
        if "raw" in path.relative_to(wiki_dir).parts:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        frontmatter = parse_frontmatter(content)
        page_type = str(frontmatter.get("type", "")).strip()
        if page_type not in {"entity", "concept"}:
            continue

        aliases: list[str] = []
        title = str(frontmatter.get("title", path.stem)).strip()
        aliases.append(title)
        alias_field = frontmatter.get("aliases")
        if isinstance(alias_field, list):
            aliases.extend(str(item).strip() for item in alias_field if str(item).strip())
        aliases.append(path.stem)
        if path.name == "profile.md":
            aliases.append(path.parent.name)

        pages.append(
            WikiPage(
                path=path,
                rel_path=path.relative_to(wiki_dir).as_posix(),
                page_type=page_type,
                title=title,
                aliases=sorted({alias for alias in aliases if alias}),
            )
        )
    return pages


def resolve_existing_related(
    pages: Iterable[WikiPage],
    text: str,
    entity_names: list[str],
    concept_names: list[str],
) -> tuple[list[WikiPage], list[WikiPage]]:
    pages = list(pages)
    normalized_text = normalize_name(text)
    explicit_entities = {normalize_name(name) for name in entity_names if name}
    explicit_concepts = {normalize_name(name) for name in concept_names if name}

    entities: list[WikiPage] = []
    concepts: list[WikiPage] = []

    for page in pages:
        aliases = {normalize_name(alias) for alias in page.aliases if alias}
        matched = False
        if page.page_type == "entity" and aliases & explicit_entities:
            matched = True
        elif page.page_type == "concept" and aliases & explicit_concepts:
            matched = True
        elif any(alias and alias in normalized_text for alias in aliases):
            matched = True

        if not matched:
            continue

        if page.page_type == "entity":
            entities.append(page)
        else:
            concepts.append(page)

    entities.sort(key=lambda item: item.title.casefold())
    concepts.sort(key=lambda item: item.title.casefold())
    return entities, concepts


def build_source_frontmatter(
    title: str,
    domain: str,
    raw_rel_path: str,
    related_links: list[str],
    created_date: str,
    confidence: str,
) -> dict[str, object]:
    frontmatter: dict[str, object] = {
        "title": title,
        "type": "source-summary",
        "domain": [domain],
        "sources": [raw_rel_path],
        "related": related_links,
        "created": created_date,
        "updated": created_date,
        "confidence": confidence,
    }
    return frontmatter


def render_key_data_rows(items: list[dict[str, object]]) -> list[str]:
    if not items:
        return ["| (none extracted) | | |", ""]

    rows = []
    for item in items:
        metric = clean_text_line(str(item.get("metric", ""))) or "(unnamed)"
        value = clean_text_line(str(item.get("value", "")))
        note = clean_text_line(str(item.get("note", "")))
        rows.append(f"| {metric} | {value} | {note} |")
    rows.append("")
    return rows


def render_quotes(quotes: list[str]) -> list[str]:
    if not quotes:
        return ["(none extracted)", ""]
    lines = []
    for quote in quotes:
        lines.append(f"> {clean_text_line(quote)}")
        lines.append("")
    return lines


def render_predictions(predictions: list[dict[str, object]]) -> list[str]:
    lines = [
        "| Prediction | Target date | Status | Verified date | Result |",
        "|---|---|---|---|---|",
    ]
    if not predictions:
        lines.append("| (none) | | | | |")
        lines.append("")
        return lines

    for item in predictions:
        claim = clean_text_line(str(item.get("claim", ""))) or "(unspecified)"
        target_date = clean_text_line(str(item.get("target_date", "")))
        status = clean_text_line(str(item.get("status", ""))) or "pending"
        verified_date = clean_text_line(str(item.get("verified_date", "")))
        result = clean_text_line(str(item.get("result", "")))
        lines.append(f"| {claim} | {target_date} | {status} | {verified_date} | {result} |")
    lines.append("")
    return lines


def render_list(items: list[str], fallback: str = "(none)") -> list[str]:
    if not items:
        return [fallback, ""]
    return [f"- {clean_text_line(item)}" for item in items] + [""]


def render_source_page(
    frontmatter: dict[str, object],
    title: str,
    raw_rel_path: str,
    source_date: str | None,
    author: str | None,
    tldr: str,
    key_data: list[dict[str, object]],
    quotes: list[str],
    implications: str,
    open_questions: list[str],
    predictions: list[dict[str, object]],
) -> str:
    lines = [render_frontmatter(frontmatter), "", f"# {title}", ""]
    lines.extend(
        [
            "## Source Details / 来源信息",
            "",
            f"- Raw file: `{raw_rel_path}`",
            f"- Source date: {source_date or 'unknown'}",
            f"- Author: {author or 'unknown'}",
            "",
            "## TL;DR / 一句话摘要",
            "",
            clean_text_line(tldr),
            "",
            "## Key Data / 关键数据",
            "",
            "| Metric | Value | Notes |",
            "|---|---|---|",
        ]
    )
    lines.extend(render_key_data_rows(key_data))
    lines.extend(["## Direct Quotes / 原始引文", ""])
    lines.extend(render_quotes(quotes))
    lines.extend(["## Implications / 启示", "", implications.strip() or "(needs refinement)", ""])
    lines.extend(["## Open Questions / 开放问题", ""])
    lines.extend(render_list(open_questions))
    lines.extend(["## Verifiable Predictions / 可验证预测", ""])
    lines.extend(render_predictions(predictions))
    return "\n".join(lines).rstrip() + "\n"


def ensure_unique_source_path(sources_dir: Path, source_date: str, slug: str) -> Path:
    base = sources_dir / f"{source_date}-{slug}.md"
    return ensure_unique_path(base)


def update_log(log_path: Path, timestamp: str, raw_rel_path: str, output_rel_path: str, note: str) -> None:
    line = f"| {timestamp} | ingest | {raw_rel_path} | {output_rel_path} | {note} |"
    content = log_path.read_text(encoding="utf-8", errors="ignore").rstrip()
    if not content.endswith("\n"):
        content += "\n"
    content += line + "\n"
    log_path.write_text(content, encoding="utf-8")


def monday_of_week(value: date) -> date:
    return value - timedelta(days=value.weekday())


def update_inbox_digest(digest_path: Path, source_rel_path: str, title: str, filed_under: str, takeaway: str, today: date) -> None:
    content = digest_path.read_text(encoding="utf-8", errors="ignore")
    week_start = monday_of_week(today).isoformat()
    source_target = source_rel_path.removesuffix(".md")
    row = f"| [[{source_target}|{Path(source_rel_path).stem}]] | {title} | {filed_under} | {takeaway} |"
    pattern = re.compile(
        rf"(?ms)^## Week of {re.escape(week_start)} \((\d+) items\)\n\n\| Source \| Title \| Filed under \| One-line takeaway \|\n\|[-| ]+\|\n"
    )
    match = pattern.search(content)

    if match:
        count = int(match.group(1)) + 1
        replacement_header = (
            f"## Week of {week_start} ({count} items)\n\n"
            "| Source | Title | Filed under | One-line takeaway |\n"
            "|---|---|---|---|\n"
            f"{row}\n"
        )
        start = match.start()
        insert_at = match.end()
        content = content[:start] + replacement_header + content[insert_at:]
    elif "| (empty - run your first ingest) | | | |" in content:
        content = content.replace(
            "## Week of YYYY-MM-DD (N items)\n\n| Source | Title | Filed under | One-line takeaway |\n|---|---|---|---|\n| (empty - run your first ingest) | | | |",
            f"## Week of {week_start} (1 items)\n\n| Source | Title | Filed under | One-line takeaway |\n|---|---|---|---|\n{row}",
        )
    elif "| (empty — run your first ingest) | | | |" in content:
        content = content.replace(
            "## Week of YYYY-MM-DD (N items)\n\n| Source | Title | Filed under | One-line takeaway |\n|--------|-------|-------------|-------------------|\n| (empty — run your first ingest) | | | |",
            f"## Week of {week_start} (1 items)\n\n| Source | Title | Filed under | One-line takeaway |\n|---|---|---|---|\n{row}",
        )
    else:
        marker = "<!--"
        block = (
            f"## Week of {week_start} (1 items)\n\n"
            "| Source | Title | Filed under | One-line takeaway |\n"
            "|---|---|---|---|\n"
            f"{row}\n\n"
        )
        if marker in content:
            content = content.replace(marker, block + marker, 1)
        else:
            content = content.rstrip() + "\n\n" + block

    content = re.sub(
        r"(?m)^updated:\s*\d{4}-\d{2}-\d{2}\s*$",
        f"updated: {today.isoformat()}",
        content,
        count=1,
    )
    digest_path.write_text(content, encoding="utf-8")


def add_inline_source_reference(content: str, source_link: str) -> str | None:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        lower = stripped.casefold()
        if "related sources:" not in lower and "相关来源" not in lower:
            continue
        if source_link in line:
            return None
        separator = "：" if "：" in line and ":" not in line else ":"
        if separator in line:
            prefix, suffix = line.split(separator, 1)
        else:
            prefix, suffix = line, ""
        suffix_lower = suffix.casefold()
        if (
            not suffix.strip()
            or "(none" in suffix_lower
            or "none yet" in suffix_lower
            or "add via ingest" in suffix_lower
        ):
            lines[index] = f"{prefix}{separator} {source_link}"
        elif line.rstrip().endswith((":", "：")):
            lines[index] = line + f" {source_link}"
        else:
            lines[index] = line.rstrip() + f", {source_link}"
        return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
    return None


def insert_source_list_item(content: str, heading_patterns: list[str], item: str, fallback_heading: str) -> str | None:
    if item in content:
        return None

    lines = content.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if any(re.fullmatch(pattern, stripped) for pattern in heading_patterns):
            insert_at = index + 1
            while insert_at < len(lines) and not lines[insert_at].startswith("## "):
                insert_at += 1
            block = ["", item]
            lines[insert_at:insert_at] = block
            return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

    suffix = "\n".join(
        [
            "",
            fallback_heading,
            "",
            item,
            "",
        ]
    )
    return content.rstrip() + suffix


def update_page_updated_field(content: str, updated_date: str) -> str:
    frontmatter = parse_frontmatter(content)
    if not frontmatter:
        return content
    frontmatter["updated"] = updated_date
    return replace_frontmatter(content, frontmatter)


def update_related_page(page: WikiPage, source_link: str, updated_date: str) -> bool:
    content = page.path.read_text(encoding="utf-8", errors="ignore")
    new_content: str | None = None

    if page.page_type == "entity":
        new_content = add_inline_source_reference(content, source_link)
        if new_content is None:
            new_content = insert_source_list_item(
                content,
                heading_patterns=[r"## Related Sources(?: / 相关来源)?", r"## 相关来源(?: / Related Sources)?"],
                item=f"- {source_link}",
                fallback_heading="## Related Sources / 相关来源",
            )
    elif page.page_type == "concept":
        new_content = insert_source_list_item(
            content,
            heading_patterns=[
                r"## Sources Cited(?: / 引用来源)?",
                r"## 引用来源(?: / Sources Cited)?",
            ],
            item=f"- {source_link} - added via command ingest",
            fallback_heading="## Sources Cited / 引用来源",
        )

    if not new_content or new_content == content:
        return False

    new_content = update_page_updated_field(new_content, updated_date)
    page.path.write_text(new_content, encoding="utf-8")
    return True


def run_scan_subcommand(repo_root: Path, args: argparse.Namespace) -> int:
    scan_script = repo_root / "skills" / "wiki-ingest" / "scripts" / "scan_pending_sources.py"
    if not scan_script.is_file():
        raise FileNotFoundError(f"Scan script not found: {scan_script}")

    command = [sys.executable, str(scan_script)]
    if args.json:
        command.append("--json")
    if args.limit is not None:
        command.extend(["--limit", str(args.limit)])
    if args.include_obsidian_clippings:
        command.append("--include-obsidian-clippings")
    if args.obsidian_clippings_path:
        command.extend(["--obsidian-clippings-path", str(args.obsidian_clippings_path)])

    completed = subprocess.run(command)
    return completed.returncode


def load_summary_from_helper(repo_root: Path, source_path: Path, provider: str | None) -> dict[str, object]:
    helper_script = repo_root / "scripts" / "ingest_helper.py"
    if not helper_script.is_file():
        raise FileNotFoundError("scripts/ingest_helper.py not found. Install the optional helper first.")

    source_flag = "--pdf" if source_path.suffix.lower() == ".pdf" else "--text"
    command = [sys.executable, str(helper_script), source_flag, str(source_path)]
    if provider:
        command.extend(["--provider", provider])

    completed = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(completed.stdout)


def coerce_key_data(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, object]] = []
    for item in value:
        if isinstance(item, dict):
            result.append(item)
    return result


def coerce_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def run_index(repo_root: Path) -> None:
    script = repo_root / "scripts" / "wiki_index.py"
    subprocess.run([sys.executable, str(script)], cwd=repo_root, check=True)
    subprocess.run([sys.executable, str(script), "--lint"], cwd=repo_root, check=True)


def ingest(repo_root: Path, args: argparse.Namespace) -> int:
    wiki_dir = (repo_root / args.wiki_dir).resolve()
    if not wiki_dir.is_dir():
        raise FileNotFoundError(f"Wiki directory not found: {wiki_dir}")

    raw_dir = wiki_dir / "raw"
    sources_dir = wiki_dir / "sources"
    log_path = wiki_dir / "_log.md"
    digest_path = wiki_dir / "inbox-digest.md"

    for required_path in (raw_dir, sources_dir, log_path, digest_path):
        if not required_path.exists():
            raise FileNotFoundError(f"Required wiki path not found: {required_path}")

    source_path = Path(args.source).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    raw_abs_path, raw_rel_path = archive_raw_file(source_path, raw_dir)

    source_text = ""
    if raw_abs_path.suffix.lower() != ".pdf" or (not args.summary_json and not args.use_ingest_helper):
        source_text = read_source_text(raw_abs_path)
        summary = heuristic_summary(raw_abs_path, source_text)
    else:
        summary = {
            "title": raw_abs_path.stem.replace("-", " ").replace("_", " ").strip() or raw_abs_path.stem,
            "date": None,
            "author": None,
            "tldr": "Summary provided via external helper.",
            "key_data": [],
            "quotes": [],
            "implications": "Command-ingested source. Review and expand this section if the source matters.",
            "entities_mentioned": [],
            "concepts_mentioned": [],
            "verifiable_predictions": [],
            "open_questions": [],
        }

    if args.summary_json:
        helper_summary = json.loads(Path(args.summary_json).read_text(encoding="utf-8"))
        summary = merge_summary(summary, helper_summary)
    elif args.use_ingest_helper:
        helper_summary = load_summary_from_helper(repo_root, raw_abs_path, args.provider)
        summary = merge_summary(summary, helper_summary)

    title = str(summary.get("title") or raw_abs_path.stem).strip()
    source_date = normalize_iso_date(str(summary.get("date") or "").strip())
    created_date = source_date or date.today().isoformat()
    author = str(summary.get("author") or "").strip() or None
    tldr = str(summary.get("tldr") or "Summary pending refinement.").strip()
    implications = str(summary.get("implications") or "").strip() or "Command-ingested source."
    key_data = coerce_key_data(summary.get("key_data"))
    quotes = coerce_string_list(summary.get("quotes"))
    open_questions = coerce_string_list(summary.get("open_questions"))
    predictions = coerce_key_data(summary.get("verifiable_predictions"))
    entities_mentioned = coerce_string_list(summary.get("entities_mentioned"))
    concepts_mentioned = coerce_string_list(summary.get("concepts_mentioned"))

    pages = discover_pages(wiki_dir)
    entity_pages, concept_pages = resolve_existing_related(
        pages,
        source_text,
        entities_mentioned + args.entity,
        concepts_mentioned + args.concept,
    )

    related_links = [f"[[{page.rel_path.removesuffix('.md')}]]" for page in entity_pages + concept_pages]
    domain = args.domain or detect_default_domain(wiki_dir)
    slug = slugify(args.slug or title or raw_abs_path.stem)
    source_md_path = ensure_unique_source_path(sources_dir, created_date, slug)
    source_rel_path = source_md_path.relative_to(wiki_dir).as_posix()
    source_link = f"[[{source_rel_path.removesuffix('.md')}]]"

    frontmatter = build_source_frontmatter(
        title=title,
        domain=domain,
        raw_rel_path=raw_rel_path,
        related_links=related_links,
        created_date=created_date,
        confidence=args.confidence,
    )
    source_page = render_source_page(
        frontmatter=frontmatter,
        title=title,
        raw_rel_path=raw_rel_path,
        source_date=source_date,
        author=author,
        tldr=tldr,
        key_data=key_data,
        quotes=quotes,
        implications=implications,
        open_questions=open_questions,
        predictions=predictions,
    )
    source_md_path.write_text(source_page, encoding="utf-8")

    updated_related = 0
    for page in entity_pages + concept_pages:
        if update_related_page(page, source_link, created_date):
            updated_related += 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    note = args.note or f"command ingest; matched {len(entity_pages)} entities, {len(concept_pages)} concepts"
    update_log(log_path, timestamp, raw_rel_path, source_rel_path, note)

    filed_under_names = [page.title for page in entity_pages + concept_pages]
    filed_under = ", ".join(f"[[{name}]]" for name in filed_under_names) if filed_under_names else domain
    update_inbox_digest(digest_path, source_rel_path, title, filed_under, tldr[:120], date.today())

    if not args.skip_lint:
        run_index(repo_root)

    payload = {
        "raw_file": raw_rel_path,
        "source_page": source_rel_path,
        "updated_related_pages": updated_related,
        "matched_entities": [page.title for page in entity_pages],
        "matched_concepts": [page.title for page in concept_pages],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Command-line tools for karpathy-claude-wiki.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Archive a source and generate wiki/source summary files.")
    ingest_parser.add_argument("source", help="Path to the raw source file.")
    ingest_parser.add_argument("--wiki-dir", default="wiki", help="Wiki directory relative to repo root. Default: wiki")
    ingest_parser.add_argument("--summary-json", help="Optional JSON output generated by scripts/ingest_helper.py.")
    ingest_parser.add_argument(
        "--use-ingest-helper",
        action="store_true",
        help="Run scripts/ingest_helper.py first and merge its JSON into the source page.",
    )
    ingest_parser.add_argument("--provider", help="Optional provider passed through to ingest_helper.py.")
    ingest_parser.add_argument("--domain", help="Override the wiki domain for this source-summary.")
    ingest_parser.add_argument("--slug", help="Override the generated slug.")
    ingest_parser.add_argument("--confidence", default="medium", choices=["high", "medium", "low"])
    ingest_parser.add_argument("--note", help="Optional note written to wiki/_log.md.")
    ingest_parser.add_argument("--skip-lint", action="store_true", help="Skip wiki_index.py and wiki_index.py --lint.")
    ingest_parser.add_argument("--entity", action="append", default=[], help="Force-link an existing entity by name.")
    ingest_parser.add_argument("--concept", action="append", default=[], help="Force-link an existing concept by name.")

    scan_parser = subparsers.add_parser("scan", help="Run the optional source scanner.")
    scan_parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    scan_parser.add_argument("--limit", type=int, help="Limit results per source root.")
    scan_parser.add_argument("--include-obsidian-clippings", action="store_true")
    scan_parser.add_argument("--obsidian-clippings-path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = resolve_repo_root(Path(__file__))

    try:
        if args.command == "scan":
            return run_scan_subcommand(repo_root, args)
        if args.command == "ingest":
            return ingest(repo_root, args)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or str(exc) + "\n")
        return exc.returncode or 1
    except Exception as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
