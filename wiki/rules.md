---
title: 已验证规则
type: meta
updated: 2026-04-18
---

# Rules / 规则

> 这里记录被重复证据验证过的模式。LLM 做研究时会检查本文件，并主动提示冲突。

## Rule Lifecycle

```text
observation -> pattern (seen 2x) -> RULE (confirmed 3x+) -> under review -> retired/updated
```

- **Promotion / 提升**：某个模式在不同实体/来源中被确认 3 次以上后，LLM 可以建议把它提升为正式规则，需用户确认。
- **Under Review / 复核中**：新证据与现行规则冲突时，把它移到 “Rules Under Review”。
- **Retirement / 退役**：规则被证明错误或已不再适用时，移动到 “Retired Rules”，不要删除。
- **Update / 更新**：规则仍然成立，但需要修正表述或边界时，原地更新并记录到 Promotion Log。

## Active Rules

| # | Rule | Source | Confirmation count | First confirmed | Last confirmed |
|---|---|---|---|---|---|
| R1 | _示例：当需求突然爆发时，真正的瓶颈往往不在最显眼的那个零部件，而在上游两层供应链。_ | (你的假设 ID) | 0 | YYYY-MM-DD | YYYY-MM-DD |

> 删掉上面的示例行，换成你自己的规则。格式尽量简短、可检索、可验证。

## Domain Playbooks

> 可选。这里放经过多次验证后形成的长一点的方法论，比如“我如何处理 X 类问题”。不要预设式编写，要从真实经验中长出来。

(empty)

## Rules Under Review

> 被新证据挑战中的规则，留待周复盘时处理。
> 格式：`R{N} - <contradicting evidence> - <date flagged> - <source>`

(none)

## Retired Rules

> 已被证伪或不再适用的规则。保留它们，是为了从失败里学习。
> 格式：`R{N} - <original rule> - <why retired> - <date retired>`

(none)

## Promotion Log

> 记录规则生命周期中的每一次事件：提升、复核、退役、更新。

| Date | Rule # | Action | Trigger |
|---|---|---|---|
| YYYY-MM-DD | - | template init | initialized empty |
