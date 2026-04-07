# INSTALL-FOR-AI.md — Auto-install protocol

> [中文](#中文-给-ai-agent-的安装协议) ｜ [English](#english--ai-agent-install-protocol)
>
> **Audience**: AI agents (Claude Code, Cursor, Cline, etc.).
> If a human user pastes the URL of this file and says *"install this for me"*, follow the steps below **in order**. Do not skip Phase 1 (clarification).

---

# 中文 — 给 AI agent 的安装协议

## 阶段 1 — 澄清（一次问一个问题）

1. **"wiki 应该放在哪？"** 默认：当前项目下的 `./wiki/`。
2. **"你的主要领域是什么？"** 选项：`investing`（投资）、`research`（研究）、`reading`（阅读）、`writing`（写作）、`mixed`（混合）。决定如何定制模板。
3. **"项目根目录是否已经有 `CLAUDE.md`？"**（yes / no）
4. **"举一个你想开始追踪的 entity 例子"**（股票代码 / 书名 / 人名 / 项目代号）。阶段 5 会用。

## 阶段 2 — 克隆与提取

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
```

移动：
- `.karpathy-tmp/wiki/` → 用户选择的路径（默认 `./wiki/`）
- `.karpathy-tmp/scripts/wiki_index.py` → `./scripts/wiki_index.py`（不存在则创建 `scripts/`）

⚠️ **此时不要删 `.karpathy-tmp/`** —— 阶段 4 还要用 `.karpathy-tmp/CLAUDE.md`。清理留到阶段 6。

## 阶段 3 — 按用户领域定制

> ⚠️ **如果用户选了 `investing`，跳过整个阶段 3** —— 模板默认就是 investing。

非 investing 领域的三步：

**3.1 重命名 entity 文件夹**

| 领域 | 新文件夹 | 术语映射 |
|---|---|---|
| `research` | `subjects/` | `entity` → `subject` |
| `reading` | `authors/` | `entity` → `author`（可删 `decisions/`） |
| `writing` | `references/` | `entity` → `reference`（可删 `rules.md`） |
| `mixed` | 保留 `entities/`，按需加 sibling | — |

**3.2 用词边界 find-replace**

只在以下两个文件里替换：
- `wiki/_schema.md`
- `.karpathy-tmp/CLAUDE.md`（**模板的**，不是用户项目根目录的）

⚠️ **必须用词边界正则**（如 `\bentities\b` → `\bsubjects\b`），否则单数 `entity` 和复数 `entities` 会被一起改坏，产出像"`entity` 页面应该列出它的 `subjects`"这种语义裂开的句子。

**3.3 同步模板 frontmatter**

打开 `wiki/<新文件夹>/_template/profile.md`，替换：
- `type: entity` → `type: <新单数>`（如 `subject`）
- `domain: [investing]` → `domain: [<用户领域>]`
- `judgment: watching/bullish/bearish/neutral` 是投资字段，不合适就改成更通用的词或保留 `watching` 当占位

> 💡 `rules.md` 和 `false-beliefs.md` 里的示例（P/E ratio、supply chain）是 investing 风格占位。本协议**不**自动重写——告诉用户那是示例，首次 ingest 后自行替换。

## 阶段 4 — 整合 `CLAUDE.md`

**情况 A：用户没有 `CLAUDE.md`** —— 直接 `cp .karpathy-tmp/CLAUDE.md ./CLAUDE.md`。

**情况 B：用户已经有 `CLAUDE.md`** —— 追加，但必须做两件事：

1. **裁掉模板的 standalone 引言**。`.karpathy-tmp/CLAUDE.md` 开头有 "If you're a human reading this for the first time..."，是写给独立文件的，merge 进去会变成尴尬的内嵌旁白。**只从 `## Protocol 1 — Ingest` 开始 append**，前面全部跳过。

2. **所有标题级别下移一级**。`# CLAUDE.md — Wiki Protocols` H1 整行删除；`## Protocol N` → `### Protocol N`，`### Phase N` → `#### Phase N`，依此类推。否则用户文件会出现两个 H1 + 层级混乱。

追加格式：
```markdown
[用户原本的 CLAUDE.md 内容]

## Wiki Protocols (from karpathy-claude-wiki)

### Protocol 1 — Ingest
[已下移层级的内容...]
```

完成后明确告诉用户：你裁掉了什么、追加了什么、改了哪些标题层级。

## 阶段 5 — 创建第一个 entity

用阶段 1 第 4 题的示例 entity 名称。**路径取决于阶段 3 是否做了 rename**：

- `investing`（默认）：`wiki/entities/<NAME>/profile.md`，模板 `wiki/entities/_template/profile.md`
- 已 rename：`wiki/<新文件夹>/<NAME>/profile.md`，模板 `wiki/<新文件夹>/_template/profile.md`

复制模板到新位置，填好基础 frontmatter（title、created 日期、domain），正文留空。**不要替用户编造 thesis 内容**。

## 阶段 6 — 验证并交付

1. **生成索引**：`python scripts/wiki_index.py`（无参数）。会生成 `wiki/_index.json` 和 `wiki/overview.md`。**没有这两个文件，wiki 没有索引，后续 lint/search 全都跑不起来**。如果用户没装 python，告诉他们装好后再手动跑。
2. **清理临时目录**：`rm -rf .karpathy-tmp`（PowerShell：`Remove-Item .\.karpathy-tmp -Recurse -Force`）。
3. 给用户展示新建的 `wiki/` 目录树。
4. 确认 `CLAUDE.md` 整合成功（打印相关章节）。
5. **告知 EXAMPLE 占位文件**（**不要自动删，让用户自己决定**）：
   > "模板里有几个 `EXAMPLE-*.md` 和 `EXAMPLE/` 文件展示页面结构。它们对 ingest 无害（Claude 会识别为占位并跳过）。要完全干净的起点：
   > ```bash
   > rm wiki/*/EXAMPLE-*.md 2>/dev/null; rm -rf wiki/*/EXAMPLE/ 2>/dev/null
   > ```
   > 不清也没事。"

6. 对用户说，原文如下：
   > "Wiki 安装完成。第一次 ingest：把一个文件放进 `wiki/raw/<category>/`（`articles` / `papers` / `books` / `podcasts` / `conversations`），然后说 '按协议摄入这个'。第一次 ingest 会根据你的具体领域优化 schema。"

阶段 6 之后停止。**不要预填内容**。用户通过日常使用来填充 wiki。

---

# English — AI agent install protocol

## Phase 1 — Clarify (one question at a time)

1. **"Where should the wiki live?"** Default: `./wiki/` in the current project.
2. **"What's your primary domain?"** Options: `investing`, `research`, `reading`, `writing`, `mixed`. Determines how I'll customize the templates.
3. **"Do you already have a `CLAUDE.md` at your project root?"** (yes / no)
4. **"What's one example entity you want to start tracking?"** (a stock ticker, book title, person's name, project codename). Store for Phase 5.

## Phase 2 — Clone & extract

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
```

Move:
- `.karpathy-tmp/wiki/` → user's chosen path (default `./wiki/`)
- `.karpathy-tmp/scripts/wiki_index.py` → `./scripts/wiki_index.py` (create `scripts/` if needed)

⚠️ **Do NOT delete `.karpathy-tmp/` yet** — Phase 4 still needs `.karpathy-tmp/CLAUDE.md`. Cleanup happens in Phase 6.

## Phase 3 — Customize for the user's domain

> ⚠️ **If the user picked `investing`, skip Phase 3 entirely** — investing is the default.

For other domains, do these three steps:

**3.1 Rename the entity folder**

| Domain | New folder | Term hint |
|---|---|---|
| `research` | `subjects/` | `entity` → `subject` |
| `reading` | `authors/` | `entity` → `author` (optionally drop `decisions/`) |
| `writing` | `references/` | `entity` → `reference` (optionally drop `rules.md`) |
| `mixed` | (keep `entities/`, add sibling dirs as needed) | — |

**3.2 Word-boundary find-replace**

Apply to two files:
- `wiki/_schema.md`
- `.karpathy-tmp/CLAUDE.md` (the **template's** CLAUDE.md, not the user's project CLAUDE.md)

⚠️ **You must use word-boundary regex** (e.g. `\bentities\b` → `\bsubjects\b`). A naive `s/entities/subjects/g` will leave the singular `entity` unchanged and produce broken sentences like "the `entity` page should list its connected `subjects`".

**3.3 Update the template's frontmatter**

Open `wiki/<new-name>/_template/profile.md` and replace:
- `type: entity` → `type: <new-singular>` (e.g. `subject`)
- `domain: [investing]` → `domain: [<chosen-domain>]`
- `judgment: watching/bullish/bearish/neutral` is investing-specific — replace with domain-appropriate values, or keep `watching` as a placeholder

> 💡 `rules.md` and `false-beliefs.md` ship with investing-flavored examples (P/E ratios, supply chains). This protocol does **not** auto-rewrite them — tell the user they're placeholders, and to replace them after the first real ingest.

## Phase 4 — Integrate `CLAUDE.md`

**Case A: user has no `CLAUDE.md`** — just `cp .karpathy-tmp/CLAUDE.md ./CLAUDE.md`. Done.

**Case B: user has an existing `CLAUDE.md`** — append, with two transformations:

1. **Trim the template's standalone intro.** `.karpathy-tmp/CLAUDE.md` starts with a "If you're a human reading this for the first time..." preamble that makes sense as a standalone file but becomes awkward in-file narration when merged. **Skip everything before `## Protocol 1 — Ingest` and only append from there.**

2. **Shift all heading levels down by one** so the appended content nests under the new parent section. Drop the `# CLAUDE.md — Wiki Protocols` H1 line entirely; turn `## Protocol N` → `### Protocol N`, `### Phase N` → `#### Phase N`, etc. Otherwise the user's file ends up with conflicting H1s and a broken hierarchy.

Append format:
```markdown
[user's existing CLAUDE.md content]

## Wiki Protocols (from karpathy-claude-wiki)

### Protocol 1 — Ingest
[shifted content...]
```

When done, tell the user explicitly: what you trimmed, what you appended, and which heading levels you shifted.

## Phase 5 — Scaffold the first entity

Use the example entity name from Phase 1 Q4. **The path depends on whether Phase 3 renamed anything**:

- If `investing` (default): use `wiki/entities/<NAME>/profile.md` and template `wiki/entities/_template/profile.md`
- If renamed: use `wiki/<new-folder>/<NAME>/profile.md` and template `wiki/<new-folder>/_template/profile.md`

Copy the template to the new location and fill in basic frontmatter (title, created date, domain). Leave the body sections empty. **Don't invent thesis content** — that's the user's job.

## Phase 6 — Verify and hand off

1. **Generate the index**: `python scripts/wiki_index.py` (no args). This produces `wiki/_index.json` and `wiki/overview.md`. **Without these, the wiki has no index and downstream lint/search commands won't work.** If python isn't available, tell the user to install it and run this command later.
2. **Cleanup**: `rm -rf .karpathy-tmp` (PowerShell: `Remove-Item .\.karpathy-tmp -Recurse -Force`).
3. Show the user a tree of the new `wiki/` directory.
4. Confirm `CLAUDE.md` integration worked (cat the relevant section).
5. **Tell the user about EXAMPLE placeholder files** (do NOT auto-delete — let them decide):
   > "The template ships with `EXAMPLE-*.md` and `EXAMPLE/` files that show what real entries look like. They're harmless (Claude recognizes them as placeholders and skips them on ingest). To get a fully clean slate:
   > ```bash
   > rm wiki/*/EXAMPLE-*.md 2>/dev/null; rm -rf wiki/*/EXAMPLE/ 2>/dev/null
   > ```
   > Leaving them is also fine."

6. Tell the user, verbatim:
   > "Wiki installed. To do your first ingest: drop a file into `wiki/raw/<category>/` where `<category>` is one of `articles`, `papers`, `books`, `podcasts`, `conversations`. Then say 'ingest this following the protocol'. The first ingest will refine the schema for your specific domain."

Stop after Phase 6. **Do not pre-populate content.** The user fills the wiki by living with it.
