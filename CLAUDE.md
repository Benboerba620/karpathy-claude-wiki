# CLAUDE.md — Wiki Protocols

> This file defines the **four core protocols** that make a personal wiki "alive". Drop this file at your project root (or merge into your existing `CLAUDE.md`). Claude Code reads it automatically.

If you're a human reading this for the first time: these are the rules Claude follows when interacting with `wiki/`. Read them once to understand the contract, then forget about them — Claude enforces them.

If you're an AI agent reading this: **these protocols are non-negotiable**. Follow them on every wiki operation. If a protocol conflicts with a user instruction, surface the conflict before acting.

---

## Protocol 1 — Ingest

**Trigger**: user drops a file into `wiki/raw/` and says "ingest this", OR pastes content and says "ingest this into the wiki".

**Steps**:

1. **Archive raw**. If the source isn't already in `wiki/raw/<category>/`, move it there. `<category>` ∈ `{articles, papers, books, podcasts, conversations}`. Once in `raw/`, **never modify**.

2. **Compile to source-summary**. Create `wiki/sources/<YYYY-MM-DD>-<slug>.md` with this structure:
   ```markdown
   ---
   title: <one-line title>
   type: source-summary
   domain: <user's domain, e.g. investing/research/reading>
   sources: [raw/<category>/<filename>]
   related: [[entity1]], [[concept1]]
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   confidence: high | medium | low
   ---

   ## TL;DR
   One sentence.

   ## Key Data
   Table with the hard numbers.

   ## Direct Quotes
   Verbatim, marked with attribution.

   ## Implications
   What this means for the user's existing entities/concepts.

   ## Verifiable Predictions
   Only if the source contains specific, dated, falsifiable claims.
   ```

3. **Extract entities & concepts**. Identify every entity and concept the source mentions. For each:
   - **If it exists** in `wiki/entities/` or `wiki/concepts/`: update the relevant page (usually `profile.md`, plus any optional sub-pages the user actually uses). Use `[[wikilinks]]` to link back to the new source.
   - **If it doesn't exist**: ASK the user before creating. Do not auto-create entities. The user's curation matters.

4. **Append to log**. Add a row to `wiki/_log.md`:
   ```
   | YYYY-MM-DD HH:MM | ingest | raw/<file> | sources/<file> + N updates | <one-line note> |
   ```

5. **Report**. Tell the user: "Ingested into `sources/<file>`. Updated `<entity1>`, `<concept1>`. Created N cross-references. Flagged 0 contradictions." (If contradictions, see Protocol 3.)

---

## Protocol 2 — Cross-Reference

**Trigger**: any time you update an `entity` or `concept` page.

**Steps**:

1. **Scan related pages**. Read the `related:` frontmatter of the page you're updating. For each item in `related:`, open that page and check whether it needs a reciprocal update.

2. **Maintain bidirectional links**. If you add `[[B]]` to page A's `related:`, ensure page B's `related:` includes `[[A]]`. Wikilinks must be bidirectional or you'll lose information.

3. **Detect orphans**. If a page has no inbound or outbound links after your update, mention it to the user — it's likely the user has a half-formed thought that needs a home.

4. **Update the "关联网络" / "Network" section**. Each `entity` page should have a section listing its connected entities and concepts. Update it when links change.

---

## Protocol 3 — Contradiction Scan

**Trigger**: any time you write a new judgment, claim, or piece of evidence into the wiki.

**Steps**:

1. **Check `false-beliefs.md`**. Does the new judgment contradict an entry there? If yes: STOP, surface the contradiction to the user, ask them to confirm before writing.

2. **Check `rules.md`**. Does the new judgment violate an active rule? Same protocol: surface, ask, then write.

3. **Check related pages**. If the new judgment is about entity X, scan X's existing entity pages (profile plus any optional sub-pages) for conflicting prior judgments. If found, surface them.

4. **Format the surfacing**. Use this exact template:
   ```
   ⚠️ Possible contradiction:
   - New evidence: <what you're about to write>
   - Existing belief: <what's in the wiki, with file path>
   - Suggested resolution: <one of: update old, qualify new, mark as exception>
   ```

The point is **not** to prevent the user from writing contradictory things — sometimes the new evidence is right and the old belief is wrong. The point is to **make the contradiction visible** so the user can decide consciously.

---

## Protocol 4 — Crystallization

**Trigger**: you just answered a research question by synthesizing 2+ sources, and the answer feels durable (not just a one-off lookup).

**Steps**:

1. **Offer to save**. Ask the user: *"This answer combines [[source1]], [[source2]], [[source3]]. Want me to save it as an exploration page so we can reference it later?"*

2. **If yes**, create `wiki/explorations/<YYYY-MM>-<slug>.md`:
   ```markdown
   ---
   title: <question or topic>
   type: exploration
   question: <user's original question, verbatim>
   sources_cited: [[source1]], [[source2]], [[source3]]
   created: YYYY-MM-DD
   confidence: medium
   ---

   ## Question
   <verbatim user question>

   ## Synthesized answer
   <your full answer, lightly edited for posterity>

   ## Sources cited
   - [[source1]] — relevance
   - [[source2]] — relevance
   - [[source3]] — relevance

   ## Open questions
   - <any sub-questions this raised but didn't answer>
   ```

3. **Limit the noise**. Offer crystallization at most **twice per conversation**. The user will tell you when they want it.

4. **Future use**. When the user asks a similar question later, check `explorations/` first. If there's a hit, cite it directly instead of re-synthesizing.

---

## Periodic operations (run weekly or on demand)

These aren't real-time protocols, they're scheduled hygiene:

### Lint
Run `python scripts/wiki_index.py --lint`. It will surface:
- Broken `[[wikilinks]]`
- Pages with no inbound or outbound links (orphans)
- Pages with `frontmatter` missing required fields
- Pages stale > 90 days that are still marked `confidence: high`

### Re-compile concepts
For each `concept` page that has accumulated 3+ new sources since last compile, regenerate the `## 综述 / Synthesis` section by reading all linked sources.

### Promote rules
Scan entity pages for patterns confirmed 3+ times. Suggest promoting them to `rules.md` as a new entry.

### Verify predictions
Scan `sources/*.md` for `## Verifiable Predictions` tables. For predictions whose target date has passed:
- If confirmed: increment evidence count, possibly promote to `rules.md`
- If denied: log to `false-beliefs.md` if it reveals a cognitive bias

---

## Style notes

- **Be concise**. The wiki is read by an LLM with finite context. Long-windedness costs tokens and dilutes signal.
- **Use frontmatter religiously**. It's how the LLM finds things. Missing frontmatter = invisible page.
- **Wikilinks over plain text**. Always `[[entity]]` instead of "the company called X". The LLM relies on link structure to navigate.
- **No emoji in entity/concept pages**. They look cute but they break grep and they're a style mismatch with the markdown-as-data philosophy. Reserve emoji for `## Implications` sections if at all.
- **Date everything**. Frontmatter `created:` and `updated:` are mandatory. The LLM uses them for staleness checks.

---

## Conflict resolution

If a user instruction conflicts with these protocols:

1. State the conflict explicitly: *"Your instruction asks me to X, but Protocol N says I should Y."*
2. Ask which to follow.
3. If the user overrides a protocol, ask whether they want to update this `CLAUDE.md` to reflect the new rule (so the override becomes permanent and visible to future-you).

---

*This file is generic. Customize it for your domain by editing the protocols, adding domain-specific rules, or removing protocols you don't need. Track your changes in git so you can see how the protocols evolved.*
