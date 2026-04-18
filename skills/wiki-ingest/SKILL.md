---
name: wiki-ingest
description: Ingest new source material into the wiki. Use when the user drops files into `wiki/raw/`, pastes content to archive and summarize, wants a flat raw inbox instead of category folders, or asks to optionally include an Obsidian `Clippings` folder during source discovery.
---

# Wiki Ingest

## Workflow

1. Treat `wiki/raw/` as the default immutable inbox. Do not require category subfolders. If the user already placed a file in `wiki/raw/`, leave it there unchanged.
2. If the user wants external scanning, run `python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings`. If no Obsidian installation or `Clippings` folder is found, continue without error.
3. If the scan reports multiple Obsidian `Clippings` candidates, ask the user which one to include. If it reports exactly one, confirm before using it as an input source.
4. Create one `wiki/sources/YYYY-MM-DD-slug.md` page per source with frontmatter that points back to the immutable raw file path.
5. Update existing entity and concept pages for referenced items. Ask before creating new entities or concepts that do not already exist.
6. Append the ingest event to `wiki/_log.md`, update `wiki/inbox-digest.md`, and run `python scripts/wiki_index.py --lint` when the ingest batch is complete.

## Source Handling

- Keep the original file immutable after it enters `wiki/raw/`.
- Prefer `sources: [raw/<filename>]` for files stored directly under `wiki/raw/`.
- If the user intentionally keeps nested folders under `wiki/raw/`, preserve the relative path instead of flattening it during ingest.
- If pasted content has no backing file, write a new timestamped Markdown file into `wiki/raw/` before summarizing it.

## Obsidian Clippings

- Obsidian `Clippings` support is optional.
- The scan script first checks common Windows locations for Obsidian and likely vault roots, then looks for `Clippings` directories.
- If Obsidian is not installed or no candidate folder exists, treat that as "feature unavailable" and proceed with `wiki/raw/` only.
- Do not silently ingest from a detected external folder unless the user opted in.

## Outputs

Each source-summary should include:

- short TL;DR
- key facts or data
- direct quotes when they matter
- implications for existing entity or concept pages
- verifiable predictions only when the source itself makes dated, falsifiable claims

## Validation

- Run `python scripts/wiki_index.py --lint` after updating the wiki.
- If the scan script was used, prefer `--json` so its output is easy to inspect or pipe into other tooling.
