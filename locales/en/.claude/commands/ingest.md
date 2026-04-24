---
description: Ingest a source into the wiki protocol. Use `/ingest` to process pending `wiki/raw/` files, or `/ingest <path>` to target a specific file.
argument-hint: [path-or-note]
disable-model-invocation: true
---

Run the wiki ingest workflow for this repository.

Start with the required context:

1. Read `wiki/_schema.md`, `wiki/_protocols.md`, and `CLAUDE.md` first.
2. Treat `wiki/raw/` as an immutable inbox. Do not rewrite raw files the user already placed there.
3. If the user explicitly wants external inbox scanning, such as Obsidian `Clippings`, run:
   `python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings`

Handle arguments using these rules:

1. If `$ARGUMENTS` is present:
   treat it as either the source path to ingest or a note that identifies which pending source to ingest.
2. If no arguments were passed:
   inspect `wiki/raw/` for pending files and ignore `.gitkeep`.
3. If there are 0 pending files:
   tell the user there is nothing to ingest right now.
4. If there is exactly 1 pending file:
   ingest it directly.
5. If there is more than 1 pending file:
   list the candidates briefly and ask the user which one to ingest. Do not batch-ingest without confirmation.

When executing the ingest:

1. If `scripts/wiki_cli.py` exists, prefer it for the boilerplate parts: archive handling, `sources/` page creation, `_log.md`, `inbox-digest.md`, and index/lint.
2. If the source is a large PDF or long document and `scripts/ingest_helper.py` exists, use the helper when it is appropriate before continuing the ingest.
3. Whether or not a script is used, the final result must conform to `wiki/_protocols.md`, not just the script's default output.
4. Update existing entity and concept pages; ask before creating new ones.
5. Maintain bidirectional `[[wikilinks]]`.
6. Confirm that `wiki/_log.md` and `wiki/inbox-digest.md` were updated.
7. If lint was not already run through `scripts/wiki_cli.py`, run:
   `python scripts/wiki_index.py --lint`

End with a short handoff:

- which raw file was ingested
- which `wiki/sources/...md` page was created
- which entity / concept pages were updated
- any remaining confirmation items
