# Ingest Workflow Notes

## Raw Inbox

- Default inbox: `wiki/raw/`
- Default storage model: flat directory
- Nested folders remain allowed for users who want manual organization, but the ingest flow must not require them

## Scan Script

Command:

```powershell
python skills/wiki-ingest/scripts/scan_pending_sources.py --json
python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings --json
python skills/wiki-ingest/scripts/scan_pending_sources.py --obsidian-clippings-path "C:\path\to\Clippings"
```

Output fields:

- `path`: absolute file path
- `relative_path`: path relative to the scanned root
- `source_root`: scanned root directory
- `source_kind`: `raw` or `obsidian-clippings`
- `modified_at`: ISO timestamp when available

## Source Summary Backlinks

Use the raw file path relative to `wiki/` in frontmatter:

```yaml
sources: [raw/example.md]
```

For nested files, keep the nested relative path:

```yaml
sources: [raw/imports/example.md]
```
