# INSTALL-FOR-AI.md - Auto-install protocol

> [中文](#中文---给-ai-agent-的安装协议) | [English](#english---ai-agent-install-protocol)
>
> **Audience**: AI agents such as Claude Code, Cursor, Cline, and Windsurf.
> If a human user pastes the URL of this file and says "install this for me", follow the steps below **in order**.

---

# 中文 - 给 AI agent 的安装协议

## 阶段 1 - 澄清（一次只问一个问题）

1. **“wiki 放在哪里？”** 默认：当前项目下的 `./wiki/`
2. **“你的主要领域是什么？”** 选项：`investing` / `research` / `reading` / `writing` / `mixed`
3. **“项目根目录里已经有 `CLAUDE.md` 吗？”** `yes` / `no`
4. **“先举一个你想开始跟踪的 entity。”** 例如股票代码、书名、人名、项目代号

## 阶段 2 - 克隆并提取

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
```

复制：

- `.karpathy-tmp/wiki/` -> 用户选择的 wiki 路径
- `.karpathy-tmp/.claude/commands/ingest.md` -> `./.claude/commands/ingest.md`（如果目标项目还没有同名命令）
- `.karpathy-tmp/scripts/wiki_index.py` -> `./scripts/wiki_index.py`
- `.karpathy-tmp/scripts/wiki_cli.py` -> `./scripts/wiki_cli.py`
- `.karpathy-tmp/skills/wiki-ingest/` -> `./skills/wiki-ingest/`（如果项目保留 repo-local skills）

默认生成简体中文 wiki。只有当用户**明确要求英文模板**时，才额外覆盖：

- `.karpathy-tmp/locales/en/CLAUDE.md` -> 目标项目根目录的 `CLAUDE.md` 模板来源
- `.karpathy-tmp/locales/en/wiki/` -> 覆盖刚复制好的 `wiki/`

只有当用户明确说要 ingest 大 PDF、长播客转录或几百页文档时，才额外复制：

- `.karpathy-tmp/scripts/ingest_helper.py` -> `./scripts/ingest_helper.py`
- `.karpathy-tmp/.env.example` -> `./.env.example`

然后告诉用户：

> 如果你想把 PDF 压缩这一步外包给便宜的外接 LLM，请任选 Kimi / 智谱 GLM / DeepSeek / Qwen / OpenAI 之一，复制 `.env.example` 为 `.env`，填入一个 API key，然后运行 `pip install requests pypdf`。如果只 ingest 短文，不需要安装这一层。

⚠️ 此时不要删除 `.karpathy-tmp/`，阶段 4 还要用到里面的模板文件。

## 阶段 3 - 按用户领域定制

> 如果用户选的是 `investing`，整个阶段 3 可以跳过。

### 3.1 重命名实体目录

| 领域 | 新目录 | 术语映射 |
|---|---|---|
| `research` | `subjects/` | `entity` -> `subject` |
| `reading` | `authors/` | `entity` -> `author` |
| `writing` | `references/` | `entity` -> `reference` |
| `mixed` | 保留 `entities/` | 按需扩展 |

### 3.2 用词替换

仅修改：

- `wiki/_schema.md`
- 默认修改 `.karpathy-tmp/CLAUDE.md`
- 如果用户明确要求英文模板，则改 `.karpathy-tmp/locales/en/CLAUDE.md`

必须使用词边界正则，避免把单复数一起改坏。

### 3.3 同步模板 frontmatter

打开 `wiki/<new-folder>/_template/profile.md`，至少同步：

- `type: entity` -> `type: <new-singular>`
- `domain: [investing]` -> `domain: [<chosen-domain>]`
- `judgment: ...` 如不合适，改成领域内更自然的词

## 阶段 4 - 整合 `CLAUDE.md`

无论用户是否已有 `CLAUDE.md`，都必须把完整 wiki 协议写入 `wiki/_protocols.md`。协议正文取自模板 `CLAUDE.md` 中 `## Protocol 1 - Ingest` 开始的全部内容。

### 情况 A：用户没有 `CLAUDE.md`

- 直接复制模板 `CLAUDE.md` 到项目根目录
- 同时写入 `wiki/_protocols.md`

### 情况 B：用户已经有 `CLAUDE.md`

不要把整套 wiki 协议直接 append 进去。改成轻量接入：

如果用户语言是 `zh-CN`，追加：

```markdown
## Wiki 协议（karpathy-claude-wiki）

处理 `wiki/` 时，请先阅读：
- `wiki/_schema.md`
- `wiki/_protocols.md`

使用这两个文件来执行摄入、交叉引用、矛盾扫描、结晶化与周期性维护。
如果 wiki 协议与上方项目级指令冲突，请先明确指出冲突，再询问用户以哪条规则为准。
```

如果用户语言是 `en`，追加：

```markdown
## Wiki Protocols (karpathy-claude-wiki)

When working with `wiki/`, first read:
- `wiki/_schema.md`
- `wiki/_protocols.md`

Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.
If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.
```

## 阶段 5 - 创建第一个 entity

使用阶段 1 第 4 个问题里收集到的 entity 名称。

- 默认路径：`wiki/entities/<NAME>/profile.md`
- 如果阶段 3 做了 rename：`wiki/<new-folder>/<NAME>/profile.md`

复制对应模板，补齐基本 frontmatter（标题、日期、领域）。正文保持空白，不要帮用户虚构 thesis。

## 阶段 6 - 验证并交付

1. 运行 `python scripts/wiki_index.py`
2. 运行 `python scripts/wiki_index.py --lint`
3. 删除 `.karpathy-tmp/`
4. 给用户展示新的 `wiki/` 目录树
5. 明确说明是否复制了完整 `CLAUDE.md`，以及 `wiki/_protocols.md` 已写入
6. 告诉用户 `_index.json`、`overview.md`、`_attention.md` 都是生成文件，不是初始内容

默认最后对用户说：

> "Wiki 安装完成。第一次 ingest：把一个文件放进 `wiki/raw/`，然后说‘按协议摄入这个’。如果你用 Obsidian Clippings，也可以先让我扫描。开始前请确保 agent 已经读过 `wiki/_schema.md`、`wiki/_protocols.md` 和 `CLAUDE.md`。"

只有当用户明确要求英文模板时，才改为：

> "Wiki installed. To do your first ingest: drop a file into `wiki/raw/`, then say 'ingest this following the protocol'. If you use Obsidian Clippings, you can ask me to scan that too. Before the first ingest, make sure the agent has read `wiki/_schema.md`, `wiki/_protocols.md`, and `CLAUDE.md`."

阶段 6 完成后停止。**不要预填任何真实内容。**

---

# English - AI agent install protocol

## Phase 1 - Clarify (one question at a time)

1. **"Where should the wiki live?"** Default: `./wiki/`
2. **"What's your primary domain?"** Options: `investing`, `research`, `reading`, `writing`, `mixed`
3. **"Do you already have a `CLAUDE.md` at your project root?"** `yes` / `no`
4. **"What's one example entity you want to start tracking?"** A ticker, book title, person, or project codename

## Phase 2 - Clone and extract

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
```

Copy:

- `.karpathy-tmp/wiki/` -> the user's chosen wiki path
- `.karpathy-tmp/.claude/commands/ingest.md` -> `./.claude/commands/ingest.md` if the target project does not already have the same command
- `.karpathy-tmp/scripts/wiki_index.py` -> `./scripts/wiki_index.py`
- `.karpathy-tmp/scripts/wiki_cli.py` -> `./scripts/wiki_cli.py`
- `.karpathy-tmp/skills/wiki-ingest/` -> `./skills/wiki-ingest/` if the project keeps repo-local skills

By default, generate a Simplified Chinese wiki. Only if the user explicitly asks for an English template, also overlay:

- `.karpathy-tmp/locales/en/CLAUDE.md`
- `.karpathy-tmp/locales/en/wiki/`

Only if the user explicitly plans large ingests, also copy:

- `.karpathy-tmp/scripts/ingest_helper.py`
- `.karpathy-tmp/.env.example`

Then tell the user:

> If you want to offload PDF compression to a cheaper external LLM, register for any one of Kimi / Zhipu GLM / DeepSeek / Qwen / OpenAI, copy `.env.example` to `.env`, fill in one API key, and run `pip install requests pypdf`. Skip this if you'll mostly ingest short articles.

⚠️ Do not delete `.karpathy-tmp/` yet. Phase 4 still needs the template files inside it.

## Phase 3 - Customize for the user's domain

> If the user picked `investing`, skip Phase 3.

### 3.1 Rename the entity folder

| Domain | New folder | Term hint |
|---|---|---|
| `research` | `subjects/` | `entity` -> `subject` |
| `reading` | `authors/` | `entity` -> `author` |
| `writing` | `references/` | `entity` -> `reference` |
| `mixed` | keep `entities/` | extend as needed |

### 3.2 Apply word-boundary replacements

Modify only:

- `wiki/_schema.md`
- `.karpathy-tmp/CLAUDE.md` by default
- `.karpathy-tmp/locales/en/CLAUDE.md` only if the user explicitly asked for English

Use word-boundary regex so you do not break singular/plural phrasing.

### 3.3 Update template frontmatter

In `wiki/<new-folder>/_template/profile.md`, at minimum update:

- `type: entity` -> `type: <new-singular>`
- `domain: [investing]` -> `domain: [<chosen-domain>]`
- `judgment: ...` -> a domain-appropriate equivalent if needed

## Phase 4 - Integrate `CLAUDE.md`

Always write the full wiki protocol into `wiki/_protocols.md`, using everything from the selected template `CLAUDE.md` starting at `## Protocol 1 - Ingest`.

### Case A: user has no `CLAUDE.md`

- Copy the selected template `CLAUDE.md` into the project root
- Write `wiki/_protocols.md`

### Case B: user already has `CLAUDE.md`

Do not append the full wiki protocol into the user's main file. Use a lightweight bridge section instead. Default to the Chinese bridge; switch to the English one only if the user explicitly asked for English.

## Phase 5 - Scaffold the first entity

Use the entity name from Phase 1 Q4.

- Default path: `wiki/entities/<NAME>/profile.md`
- If Phase 3 renamed things: `wiki/<new-folder>/<NAME>/profile.md`

Copy the template, fill in title/date/domain, and leave the body empty. Do not invent thesis content.

## Phase 6 - Verify and hand off

1. Run `python scripts/wiki_index.py`
2. Run `python scripts/wiki_index.py --lint`
3. Delete `.karpathy-tmp/`
4. Show the user the resulting `wiki/` tree
5. Confirm whether you copied the full `CLAUDE.md`, and that `wiki/_protocols.md` exists
6. Tell the user that `_index.json`, `overview.md`, and `_attention.md` are generated files, not starter content

Final hand-off message:

- For `zh-CN`:
  `"Wiki 安装完成。第一次 ingest：把一个文件放进 \`wiki/raw/\`，然后说‘按协议摄入这个’。如果你用 Obsidian Clippings，也可以先让我扫描。开始前请确保 agent 已经读过 \`wiki/_schema.md\`、\`wiki/_protocols.md\` 和 \`CLAUDE.md\`。"`
- For `en`:
  `"Wiki installed. To do your first ingest: drop a file into \`wiki/raw/\`, then say 'ingest this following the protocol'. If you use Obsidian Clippings, you can ask me to scan that too. Before the first ingest, make sure the agent has read \`wiki/_schema.md\`, \`wiki/_protocols.md\`, and \`CLAUDE.md\`."`

Stop after Phase 6. **Do not pre-populate real content.**
