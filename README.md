# karpathy-claude-wiki

> A personal LLM Knowledge Base template, **inspired by [Andrej Karpathy's tweet](https://x.com/karpathy/status/2039805659525644595)** on building personal wikis with LLMs. Optimized for [Claude Code](https://claude.com/claude-code) but works with any AI agent that can read & write files.

**Status**: Empty template. You install it, you fill it. The LLM does the bookkeeping forever after.

---

## What is this?

A markdown-based personal wiki where **you curate, the LLM maintains**. Drop a research note into `wiki/raw/`, and the LLM compiles it into structured `sources/`, updates `concepts/` and `entities/`, builds cross-references, and flags contradictions with what you already believe.

This is the architecture:

```
wiki/
├── _schema.md          # The constitution. AI reads this before every action.
├── _log.md             # Operation log (who changed what, when, why).
├── raw/                # Immutable original materials (PDFs, articles, transcripts).
├── sources/            # Compiled summaries, one page per source. Frontmatter required.
├── entities/           # Companies, people, books, projects — anything you track.
├── concepts/           # Themes, frameworks, ideas that connect entities.
├── explorations/       # Crystallized answers to research questions (write-back).
├── decisions/          # Decision log with reasoning + trade-offs.
├── rules.md            # Rules confirmed by 3+ instances.
├── false-beliefs.md    # Conventional wisdom that data has refuted.
└── comparisons/        # Side-by-side comparisons (A vs B).
```

The five layers are organized by **rate of change**:

| Layer | Speed | Example |
|---|---|---|
| `raw/` | never changes | PDFs, full-text articles |
| `sources/` | rarely changes | structured summaries |
| `entities/` + `concepts/` | weekly–monthly | profiles, themes |
| `explorations/` + `decisions/` | per-query | crystallized answers |
| `rules.md` + `false-beliefs.md` | quarterly | hard-won lessons |

---

## Why this is different from Notion / Obsidian / RAG

| Dimension | Traditional KB | This template |
|---|---|---|
| **Read by** | You (someday) | LLM (every query) |
| **Maintained by** | You (which is why it dies) | LLM (which is why it lives) |
| **Organization** | Folders + tags | Layered by change-rate + explicit cross-refs |
| **Output** | You open files | You ask, AI reasons across the wiki |

The crucial shift: **maintenance cost approaches zero**, because the LLM does the bookkeeping. You become a curator, not a janitor.

---

## Quick Start (Humans, 5 minutes)

### 1. Clone

```bash
git clone https://github.com/YOUR-USERNAME/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

### 2. Read the schema

```bash
cat wiki/_schema.md
```

This is your wiki's "constitution". The AI will read it before every operation.

### 3. Move CLAUDE.md to your project root

```bash
# If you already have a CLAUDE.md, append the contents instead of overwriting
cp CLAUDE.md ../my-project/CLAUDE.md
```

### 4. Drop your first source into raw/

```bash
cp ~/Downloads/some-research-paper.md wiki/raw/papers/
```

### 5. Open Claude Code and say:

> "Read `wiki/_schema.md` and `CLAUDE.md`, then ingest `wiki/raw/papers/some-research-paper.md` into the wiki following the ingest protocol."

That's it. Claude will:
- Create a `wiki/sources/<date>-<slug>.md` with structured summary
- Detect entities and concepts mentioned, create or update those pages
- Add cross-references using `[[wikilinks]]`
- Append to `_log.md`

After the first ingest, refine the schema based on what worked. Then ingest more.

---

## AI Auto-Install Protocol

> **For AI agents (Claude Code, Cursor, Cline, etc.)**: if a user pastes this README's URL and says "install this for me", follow the steps below **in order**. Do not skip the clarification phase.

### Phase 1 — Clarify (ask the user, one question at a time)

1. **"Where should the wiki live?"** Default: `./wiki/` in the current project.
2. **"What's your primary domain?"** Options: `investing`, `research`, `reading`, `writing`, `mixed`. This determines how I'll customize the templates.
3. **"Do you already have a `CLAUDE.md` at your project root?"** (yes / no)
4. **"What's one example entity you want to start tracking?"** (e.g., a company ticker, a book title, a person's name, a project codename). Store this answer for Phase 5.

### Phase 2 — Clone & extract

```bash
git clone https://github.com/YOUR-USERNAME/karpathy-claude-wiki.git .karpathy-tmp
```

Move:
- `.karpathy-tmp/wiki/` → user's chosen path (default `./wiki/`)
- `.karpathy-tmp/scripts/wiki_index.py` → `./scripts/wiki_index.py` (create `scripts/` if needed)

Then delete `.karpathy-tmp/`.

### Phase 3 — Customize for the user's domain

Open `wiki/_schema.md` and apply the domain-specific edits:

| Domain | Edit |
|---|---|
| `investing` | Keep as-is. `entities/` = companies, `concepts/` = themes/frameworks. |
| `research` | Rename `entities/` → `subjects/`. Simplify `rules.md` to just "validated patterns". |
| `reading` | Rename `entities/` → `authors/`, `concepts/` → `themes/`. Drop `decisions/`. |
| `writing` | Rename `entities/` → `references/`, `concepts/` → `topics/`. Drop `rules.md`. |
| `mixed` | Keep `entities/` + add sibling dirs as needed. |

After renaming, do a project-wide find-replace in `_schema.md` and `CLAUDE.md` to fix references.

### Phase 4 — Integrate `CLAUDE.md`

- **If the user has an existing `CLAUDE.md`**: APPEND the contents of `.karpathy-tmp/CLAUDE.md` under a new section `## Wiki Protocols (from karpathy-claude-wiki)`. Tell the user what you appended.
- **If the user has no `CLAUDE.md`**: Copy `.karpathy-tmp/CLAUDE.md` to the user's project root.

### Phase 5 — Scaffold the first entity

Use the example entity name from Phase 1 Q4. Create:

```
wiki/entities/<NAME>/profile.md
```

Use `wiki/entities/_template/profile.md` as the template. Fill in basic frontmatter (title, type, created date). Leave the body sections empty for the user to populate.

### Phase 6 — Verify and hand off

1. Show the user a tree of the new `wiki/` directory.
2. Confirm `CLAUDE.md` integration worked (cat the relevant section).
3. Tell the user, verbatim:
   > "Wiki installed. To do your first ingest: drop a file into `wiki/raw/<category>/`, then say 'ingest this following the protocol'. The first ingest will refine the schema for your specific domain."

Stop after Phase 6. Do not pre-populate content. The user fills the wiki by living with it.

---

## How the LLM-as-bookkeeper actually works

The key insight (from Karpathy and verified across many implementations): **bookkeeping is what kills traditional knowledge bases**. Not thinking. Not curation. Bookkeeping. Tagging, linking, deduping, summarizing, re-organizing.

LLMs are extraordinarily good at bookkeeping. They get bored doing it the way you do, but they don't get bored the way you do.

So the design principle is:

1. **You decide what enters the wiki** (curation)
2. **You decide what to ask of it** (queries)
3. **The LLM does everything else** (compilation, cross-referencing, contradiction-scanning, write-backs)

The four protocols in `CLAUDE.md` encode this division of labor:

- **Ingest protocol**: when a user gives me a new source, I summarize it into `sources/`, extract entities/concepts, and update those pages.
- **Cross-reference protocol**: when I update an entity, I check whether related concepts and other entities need synchronization.
- **Contradiction-scan protocol**: when I write a new judgment, I check `false-beliefs.md` and `rules.md` for conflicts and flag them.
- **Crystallization protocol**: when a query produces a particularly useful answer, I offer to save it as an `exploration` page.

These four protocols are what make the wiki "alive". Read `CLAUDE.md` for the exact wording.

---

## What's NOT in this template

- **No vector database**. Markdown + frontmatter + LLM context window is enough. Karpathy's insight: your personal wiki is small enough that you don't need RAG.
- **No GUI**. Use Obsidian, VSCode, or any markdown editor. Or don't use any at all — talk to the LLM.
- **No specific domain content**. This is intentionally empty. Yibo's investing wiki has 34 entities and 111 sources after 2 months; yours will look different.

---

## Credit & inspiration

- [Andrej Karpathy](https://x.com/karpathy/status/2039805659525644595) — original idea & framing
- [Karpathy's gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the "idea file"
- [Stewart Brand's *How Buildings Learn*](https://en.wikipedia.org/wiki/How_Buildings_Learn) — shearing layers principle
- [Claude Code](https://claude.com/claude-code) — the agent harness this was designed for

---

## License

MIT. Fork it, change it, ship it. Tell me what you build.

---

*If you build something interesting on top of this, open an issue or PR — would love to see it.*
