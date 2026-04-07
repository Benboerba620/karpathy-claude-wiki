# Scripts

Helper scripts for maintaining the wiki. Currently:

## `wiki_index.py`

A combined index generator, search tool, and lint checker.

```bash
# Default: regenerate _index.json + overview.md
python scripts/wiki_index.py

# Search by keyword across all pages
python scripts/wiki_index.py --search "concept name"

# Run health check (broken links, orphans, stale pages, missing frontmatter)
python scripts/wiki_index.py --lint

# Quick stats by type and domain
python scripts/wiki_index.py --stats
```

This is a minimal version (~200 lines). The original it was distilled from is ~700 lines and has domain-specific extensions for entity sub-pages and concept directories. Customize freely.

## What you might add later

Common additions, in order of usefulness:

1. **`fix_broken_links.py`** — auto-repair common wikilink format issues (display text vs path)
2. **`split_sources.py`** — split a long accumulated source file into individual `sources/*.md` pages
3. **`promote_rules.py`** — scan tracker pages for 3+ confirmation patterns, suggest rule promotions
4. **`verify_predictions.py`** — for predictions whose target date has passed, ask the LLM to verify and update

None of these are essential. Build them when the pain shows up.

## Dependencies

The minimal script uses only the Python standard library. No `pip install` required.

If you want fancier YAML parsing (multi-line values, nested dicts), add `pyyaml` and replace `parse_frontmatter()`.
