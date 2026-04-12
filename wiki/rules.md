---
title: Validated Rules
type: meta
updated: 2026-04-07
---

# Rules

> Patterns confirmed by repeated evidence. The LLM checks this file during research and flags conflicts.

## Rule Lifecycle

Rules have a clear promotion and demotion path:

```
observation → pattern (seen 2x) → RULE (confirmed 3x+) → under review → retired/updated
```

- **Promotion**: A pattern confirmed 3+ times across different entities/sources → the LLM proposes adding it here as a new rule. User confirms before adding.
- **Under Review**: New evidence contradicts an active rule → move it to "Rules Under Review" with the contradicting evidence. Discuss in next weekly review.
- **Retirement**: Rule is proven wrong or no longer applies → move to "Retired Rules" with the reason. Never delete — failed rules teach as much as successful ones.
- **Update**: Rule is still valid but needs refinement → update in place, bump confirmation count, note the refinement in the Promotion Log.

## Active Rules

| # | Rule | Source | Confirmation count | First confirmed | Last confirmed |
|---|------|--------|--------------------|-----------------|-----------------|
| R1 | _Example: When demand spikes, the bottleneck is rarely the obvious component — check supply chains two layers upstream._ | (your hypothesis ID) | 0 | YYYY-MM-DD | YYYY-MM-DD |

> Delete the example row above and add your own. Format: short rule, then source, then confirmation count.

## Domain Playbooks

> Optional: longer-form playbooks that go beyond a one-line rule. Use this section for "how I handle X" recipes you've validated multiple times. Playbooks should emerge from multiple rules and real experience, not be written speculatively.

(empty)

## Rules Under Review

> Rules whose validity is being questioned by new evidence. Discuss in your weekly review.
> Format: `R{N} — <contradicting evidence> — <date flagged> — <source>`

(none)

## Retired Rules

> Rules that turned out to be wrong or no longer apply. Keep them here as a record so you can learn from failure.
> Format: `R{N} — <original rule> — <why retired> — <date retired>`

(none)

## Promotion Log

> Track every rule lifecycle event: promotion, review, retirement, update.

| Date | Rule # | Action | Trigger |
|------|--------|--------|---------|
| YYYY-MM-DD | — | template init | initialized empty |
