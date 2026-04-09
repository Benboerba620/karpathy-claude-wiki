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

先做一件事：**无论用户有没有现成 `CLAUDE.md`，都要把完整 wiki 协议写入 `wiki/_protocols.md`**。这个文件由模板 `CLAUDE.md` 中 `## Protocol 1 — Ingest` 及其后续内容组成。

**情况 A：用户没有 `CLAUDE.md`** —— 直接把模板的 `CLAUDE.md` 复制到项目根目录；同时写入 `wiki/_protocols.md`。

**情况 B：用户已经有 `CLAUDE.md`** —— **不要把整套 wiki 协议原样 append 到用户主 `CLAUDE.md`**。改成下面这种轻量接入：

1. 把完整 wiki 协议写入 `wiki/_protocols.md`
2. 在用户现有 `CLAUDE.md` 末尾追加一个短章节，内容如下：

```markdown
## Wiki Protocols (karpathy-claude-wiki)

When working with `wiki/`, first read:
- `wiki/_schema.md`
- `wiki/_protocols.md`

Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.
If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.
```

这样做的目的：
- 不把用户原本的主 `CLAUDE.md` 撑得很长
- 让完整 wiki 协议留在 `wiki/` 内部，只有处理 wiki 时才读取
- 保留用户自己已有的工作流、行业背景和命令系统

完成后明确告诉用户：
- 你是否复制了完整 `CLAUDE.md`
- 你是否写入了 `wiki/_protocols.md`
- 如果用户已有 `CLAUDE.md`，你只追加了一个轻量入口，而不是整套协议

## 阶段 5 — 创建第一个 entity

用阶段 1 第 4 题的示例 entity 名称。**路径取决于阶段 3 是否做了 rename**：

- `investing`（默认）：`wiki/entities/<NAME>/profile.md`，模板 `wiki/entities/_template/profile.md`
- 已 rename：`wiki/<新文件夹>/<NAME>/profile.md`，模板 `wiki/<新文件夹>/_template/profile.md`

复制模板到新位置，填好基础 frontmatter（title、created 日期、domain），正文留空。**不要替用户编造 thesis 内容**。

## 阶段 6 — 验证并交付

1. **生成索引**：`python scripts/wiki_index.py`（无参数）。会生成 `wiki/_index.json` 和 `wiki/overview.md`。**没有这两个文件，wiki 没有索引，后续 lint/search 全都跑不起来**。如果用户没装 python，告诉他们装好后再手动跑。
2. **清理临时目录**：`rm -rf .karpathy-tmp`（PowerShell：`Remove-Item .\.karpathy-tmp -Recurse -Force`）。
3. 给用户展示新建的 `wiki/` 目录树。
4. 确认 `CLAUDE.md` 轻量接入或复制成功，并展示 `wiki/_protocols.md` 已写入。
5. **告知用户生成文件是按需生成的**：
   > "模板现在默认是干净起点。`_index.json`、`overview.md`、`_attention.md` 都是运行脚本后才生成的文件，不是初始内容；没有它们也可以先正常开始使用。"


6. 对用户说，原文如下：
   > "Wiki 安装完成。第一次 ingest：把一个文件放进 `wiki/raw/<category>/`（`articles` / `papers` / `books` / `podcasts` / `conversations`），然后说 '按协议摄入这个'。第一次 ingest 前，先确保 agent 读过 `wiki/_schema.md`、`wiki/_protocols.md` 和 `CLAUDE.md`。"

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

First do one thing unconditionally: **write the full wiki protocol to `wiki/_protocols.md`**, using everything from the template `CLAUDE.md` starting at `## Protocol 1 — Ingest`.

**Case A: user has no `CLAUDE.md`** — copy the template `CLAUDE.md` to the project root; also write `wiki/_protocols.md`.

**Case B: user has an existing `CLAUDE.md`** — **do not append the full wiki protocol into the user's main `CLAUDE.md`**. Use lightweight integration instead:

1. Write the full wiki protocol to `wiki/_protocols.md`
2. Append this short section to the user's existing `CLAUDE.md`:

```markdown
## Wiki Protocols (karpathy-claude-wiki)

When working with `wiki/`, first read:
- `wiki/_schema.md`
- `wiki/_protocols.md`

Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.
If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.
```

Why this is better:
- it keeps the user's main `CLAUDE.md` compact
- it keeps the full wiki protocol inside `wiki/`, only read when needed
- it preserves the user's own workflow, domain background, and command system

When done, tell the user explicitly:
- whether you copied the full `CLAUDE.md`
- whether you wrote `wiki/_protocols.md`
- if the user already had `CLAUDE.md`, that you added only a lightweight entry instead of the full protocol

## Phase 5 — Scaffold the first entity

Use the example entity name from Phase 1 Q4. **The path depends on whether Phase 3 renamed anything**:

- If `investing` (default): use `wiki/entities/<NAME>/profile.md` and template `wiki/entities/_template/profile.md`
- If renamed: use `wiki/<new-folder>/<NAME>/profile.md` and template `wiki/<new-folder>/_template/profile.md`

Copy the template to the new location and fill in basic frontmatter (title, created date, domain). Leave the body sections empty. **Don't invent thesis content** — that's the user's job.

## Phase 6 — Verify and hand off

1. **Generate the index**: `python scripts/wiki_index.py` (no args). This produces `wiki/_index.json` and `wiki/overview.md` for navigation. If python isn't available, tell the user the wiki still works and they can run this command later.
2. **Cleanup**: `rm -rf .karpathy-tmp` (PowerShell: `Remove-Item .\.karpathy-tmp -Recurse -Force`).
3. Show the user a tree of the new `wiki/` directory.
4. Confirm `CLAUDE.md` copy/lightweight integration worked, and show that `wiki/_protocols.md` was written.
5. **Tell the user generated files are optional**:
   > "This template now ships as a clean slate. `_index.json`, `overview.md`, and `_attention.md` are generated files, not starter content. Generate them when you want navigation or structural reports; leaving them absent is fine."


6. Tell the user, verbatim:
   > "Wiki installed. To do your first ingest: drop a file into `wiki/raw/<category>/` where `<category>` is one of `articles`, `papers`, `books`, `podcasts`, `conversations`. Then say 'ingest this following the protocol'. Before the first ingest, make sure the agent has read `wiki/_schema.md`, `wiki/_protocols.md`, and `CLAUDE.md`."

Stop after Phase 6. **Do not pre-populate content.** The user fills the wiki by living with it.
