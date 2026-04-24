[中文](#中文) ｜ [English](#english)

[![Latest Release](https://img.shields.io/github/v/release/Benboerba620/karpathy-claude-wiki?display_name=tag)](https://github.com/Benboerba620/karpathy-claude-wiki/releases/latest)
[![Wiki Lint](https://github.com/Benboerba620/karpathy-claude-wiki/actions/workflows/wiki-lint.yml/badge.svg)](https://github.com/Benboerba620/karpathy-claude-wiki/actions/workflows/wiki-lint.yml)

> 🔗 **"零代码 AI 投研三件套" 之一** ｜ Part of the zero-code AI investment research toolkit
> 知识库底座 karpathy-claude-wiki · [日常盯盘 daily-watchlist](https://github.com/Benboerba620/daily-watchlist) · [假设追踪 hypothesis-tracker](https://github.com/Benboerba620/hypothesis-tracker)

# 中文

> 一个个人 LLM 知识库模板，**灵感来自 [Andrej Karpathy 的推文](https://x.com/karpathy/status/2039805659525644595)** —— 用 LLM 来构建和维护个人 wiki。本模板针对 [Claude Code](https://claude.com/claude-code) 优化，但任何能读写文件的 AI agent 都可以使用。
>
> **状态**：空模板。你负责放资料、提问题；LLM 负责整理、交叉引用、回写和持续维护。

**Last updated**：`2026-04-18`

**直接按你的情况选一条路：**

| 你是谁 | 走哪条路 |
|---|---|
| 🤖 **任何人，尤其编程小白** | [**让 Claude Code / AI agent 帮你装（推荐）**](#-推荐让-claude-code--ai-agent-帮你装) |
| 📄 **要 ingest 研报 / 长文档** | [可选：大文件 ingest 外接 LLM 助手](#-可选大文件-ingest-外接-llm-助手) |
| 🧑‍💻 **偏好本地脚本 / 不想让 agent 动电脑** | [进阶：本地脚本安装](#进阶本地脚本安装-windows--macos--linux)（折叠） |
| 🛠️ **想完全手动拆解每一步** | [进阶：手动安装（5 分钟）](#进阶手动安装5-分钟)（折叠） |

## 最近更新

- `2026-04-18`：发布 `v0.2.0`——整个 wiki 默认输出中文，英文改为可选 locale；安装器、安装协议、模板、CI smoke test 全部对齐到这一行为
- `2026-04-18`：新增 Claude Code 的 `.claude/commands/ingest.md`，现在可以直接用 `/ingest` 触发协议
- `2026-04-18`：新增 `scripts/wiki_cli.py`：提供 `ingest` / `scan` 命令，支持命令式 ingest，而不只依赖 agent 对话触发
- `2026-04-17`：README 结构重排——让 Claude Code / AI agent 帮你装成为首推路径，本地脚本和手动安装折叠为进阶选项
- `2026-04-17`：新增 `scripts/ingest_helper.py` + `.env.example`：可选的大文件 ingest 外接 LLM 助手，支持 Kimi / 智谱 GLM / DeepSeek / 通义 Qwen / OpenAI 五家 OpenAI 兼容 provider（前四家在国内有免费额度）
- `2026-04-12`：新增 `explorations/_template.md` 和 `decisions/_template.md`，包含假设分支、备选方案、行动触发条件、Lessons → Rules 闭环
- `2026-04-12`：`rules.md` 新增 Rule Lifecycle（`observation → pattern → RULE → under review → retired`），Promotion Log 记录所有生命周期事件
- `2026-04-12`：`inbox-digest.md` 从平铺表格改为按周分组，60 天滚动归档到 `inbox-archive.md`
- `2026-04-12`：扩展所有 EXAMPLE 文件为完整带注释的示例；新增 source-summary 示例；安装脚本 Python 检测加强；CI 升级到 v6
- `2026-04-09`：模板默认改为干净起点；修复 bash 安装器 bug；统一三端安装器行为
- 完整历史见 [`CHANGELOG.md`](./CHANGELOG.md)

---

## 这是什么？

一个基于 markdown 的个人 wiki，**用户负责策展，LLM 负责维护**。把一份研究笔记丢进 `wiki/raw/`，LLM 会自动把它编译成结构化的 `sources/` 页面、更新 `concepts/` 和 `entities/`、建立交叉引用，并标记任何与你已有信念相冲突的地方。

```
wiki/
├── _schema.md          # 宪法。AI 在每次操作前先读它
├── _log.md             # 操作日志
├── raw/                # 不可变的原始材料（PDF、文章、文字稿）
├── sources/            # 编译后的结构化总结，每个来源一页
├── entities/           # 公司、人、书、项目——任何想追踪的对象
├── concepts/           # 主题、框架、把 entities 联系起来的想法
├── explorations/       # 研究问题的固化答案（回写）
├── decisions/          # 决策日志，含理由 + 取舍
├── rules.md            # 被 3 次以上验证过的规律
├── false-beliefs.md    # 被数据推翻的常识
└── comparisons/        # 并排对比
```

五层按 **变化速率** 组织：`raw/` 永不变 → `sources/` 很少变 → `entities/` + `concepts/` 周/月级 → `explorations/` 随查询而变 → `rules.md` + `false-beliefs.md` 季度级。

**和 Notion / Obsidian / RAG 的关键区别**：传统知识库是写给"某天会回头读"的你的，所以维护成本最终会杀死它；这个模板是写给 **每次查询都读一遍** 的 LLM 的，维护成本由 LLM 承担——你只负责策展。**没有向量数据库**，markdown + frontmatter + LLM 上下文窗口已经够用（Karpathy 的洞察：个人 wiki 的体量根本不需要 RAG）。

---

## 🤖 推荐：让 Claude Code / AI agent 帮你装

**最简单的方式**。不用下载项目、不用开终端、不用敲命令——整个流程就是打开 AI agent 发一句话。

### 1. 打开 Claude Code（或 Cursor / Cline / Windsurf 等任何能读 URL + 写文件的 agent）

### 2. 把下面这句话发给它：

> 帮我装这个：https://github.com/Benboerba620/karpathy-claude-wiki/blob/main/INSTALL-FOR-AI.md

### 3. Agent 会按 `INSTALL-FOR-AI.md` 里的 6 阶段协议和你互动

它会问你 4 个问题（一次一个）：

1. **wiki 放哪**？（默认 `./wiki/`）
2. **你的主要领域**？（`investing` / `research` / `reading` / `writing` / `mixed`）
3. **项目根目录已经有 `CLAUDE.md` 了吗**？
4. **举一个你想开始追踪的 entity**（股票代码 / 书名 / 人名 / 项目代号都行）

回答完之后，agent 会自动克隆模板、按你领域定制（如果不是默认的 `investing`）、写入 `wiki/_protocols.md`、轻量接入或复制 `CLAUDE.md`、创建你指定的第一个 entity、生成索引、清理临时文件。**整个过程无需你再操作任何命令**。

### 小白常见问题

- **不懂 Git / Markdown / 命令行，能用吗？** 能，这条路就是为这种情况设计的。Agent 会帮你干所有技术活。
- **必须先懂 schema / protocol 吗？** 不必。装起来先用，需要时再看。
- **没装 Python 会失败吗？** 装起来不会失败；只是 `_index.json` 和 `overview.md` 两个导航文件生成不了，等装了 Python 再手动跑一次 `python scripts/wiki_index.py` 就好。
- **只想先试试，不想污染现有项目？** 告诉 agent 把 wiki 放到一个全新空目录就行。
- **Claude Code 没订阅 / 用不了怎么办？** 用 [Cursor](https://cursor.com/) / [Cline](https://cline.bot/) / [Windsurf](https://codeium.com/windsurf) 任何一个能读 URL 的 agent 都行。或者走下面「进阶：本地脚本安装」折叠段里的本地脚本。

---

## 📄 可选：大文件 ingest 外接 LLM 助手

> **什么时候值得装这个**：你计划的主要用法是 ingest 研报（几十页）、长播客文稿、或整本书。
> **什么时候可以跳过**：你主要喂短文章 / 笔记 / 对话。主 agent 直接读就够了。

**为什么需要**：几十页的 PDF 直接塞给 Claude / Cursor 主对话会狂烧 context。`scripts/ingest_helper.py` 把"压缩 PDF 成结构化 JSON"这一步外包给一个便宜的 OpenAI 兼容 LLM，主 agent 拿到 JSON 再快速生成 `sources/` 页面。

**支持五家 provider**（任选一家即可，前四家在国内都有免费额度）：

| Provider | 注册地址 | 免费额度 / 特点 |
|---|---|---|
| **Kimi / 月之暗面** | [platform.moonshot.cn](https://platform.moonshot.cn/) | 长文本友好，新用户有免费额度 |
| **智谱 GLM** | [bigmodel.cn](https://bigmodel.cn/) | `glm-4-flash` 截至 2026-01 免费 |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com/) | 新用户送免费 credits |
| **通义 Qwen** | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/) | 阿里 DashScope，OpenAI 兼容模式 |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | 或任何 OpenAI 兼容端点（改 `base_url` 即可） |

**三步配好**：

```bash
# 1. 拷贝配置模板
cp .env.example .env

# 2. 编辑 .env，在你选的那家 provider 下取消注释并填 key
#    （只需填一家，脚本会自动探测）

# 3. 装依赖
pip install requests pypdf
```

**用法示例**：

```bash
# 读 PDF，结构化 JSON 打到 stdout
python scripts/ingest_helper.py --pdf wiki/raw/my-report.pdf

# 显式指定 provider
python scripts/ingest_helper.py --pdf my.pdf --provider glm

# 写 JSON 到文件（主 agent 随后读这个 JSON 去生成 sources/ 页面）
python scripts/ingest_helper.py --pdf my.pdf --out /tmp/summary.json
```

JSON 输出包含 `title / date / tldr / key_data / quotes / implications / verifiable_predictions / open_questions / entities_mentioned / concepts_mentioned`——正好对齐 ingest 协议里 `sources/<日期>-<slug>.md` 的字段。

> 📝 **提示**：用 AI agent 安装路径的用户，只要在**阶段 2 克隆**时**额外**告诉 agent 把 `scripts/ingest_helper.py`、`.env.example` 和 `skills/wiki-ingest/` 也复制到项目，就能一起装好。agent 会自动处理。`wiki/raw/` 现在默认就是平铺 inbox；如果你用 Obsidian Clippings，也可以让 agent 先扫描它。

---

## ⌨️ 可选：命令式 ingest

如果你不想每次都对 agent 说“ingest this”，现在也可以直接走命令：

```bash
# 最简单：归档原文件、生成 sources 页面、更新 _log / inbox-digest、跑 index + lint
python scripts/wiki_cli.py ingest path/to/source.md

# 大 PDF / 长文先用 helper 压成 JSON，再交给命令式 ingest
python scripts/ingest_helper.py --pdf my.pdf --out /tmp/my.json
python scripts/wiki_cli.py ingest my.pdf --summary-json /tmp/my.json

# 扫描 wiki/raw/ 和可选 Obsidian Clippings
python scripts/wiki_cli.py scan --include-obsidian-clippings --json
```

`wiki_cli.py ingest` 默认会做这几件事：

- 必要时把原文件复制进 `wiki/raw/`
- 创建 `wiki/sources/YYYY-MM-DD-slug.md`
- 更新 `wiki/_log.md`
- 更新 `wiki/inbox-digest.md`
- 尝试回链已存在的 entity / concept 页面
- 最后运行 `python scripts/wiki_index.py` 和 `python scripts/wiki_index.py --lint`

如果你已经在项目里安装了可选的 `scripts/ingest_helper.py`，命令式 ingest 就能和大文件预处理无缝拼起来。

---

## `/ingest`：Claude Code 里的 slash command

如果你用的是 Claude Code，现在仓库也自带了真正的 slash command：

```text
/ingest
/ingest wiki/raw/some-research-paper.md
```

这个命令文件在 `.claude/commands/ingest.md`。它会先让 Claude 读取 `wiki/_schema.md`、`wiki/_protocols.md` 和 `CLAUDE.md`，然后按协议执行 ingest；如果仓库里有 `scripts/wiki_cli.py`，它也会优先利用脚本处理样板步骤。

本地安装脚本会把这个命令一起复制到目标项目；如果目标项目已经有自己的 `.claude/commands/ingest.md`，安装器会跳过，避免覆盖你的现有命令。

---

<details>
<summary><b>进阶：本地脚本安装 (Windows / macOS / Linux)</b></summary>

适合：不想让 AI agent 接触本地文件、或者没有 Claude Code / Cursor 订阅的用户。

### 🪟 Windows PowerShell 一键安装

```powershell
# 1. 下载项目
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki

# 2. 一键安装到目标目录（换成你自己的路径和 entity 名称）
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"
```

不会用 git：在 GitHub 页面点 **Code → Download ZIP**，解压，`cd` 进去。

脚本会：复制 `wiki/`、复制 `.claude/commands/ingest.md`、复制 `scripts/wiki_index.py`、复制 `scripts/wiki_cli.py`、处理 `CLAUDE.md`（已有则只追加轻量入口 + 把完整协议写入 `wiki/_protocols.md`）、创建第一个可跟踪 entity、在 Python 可用时生成索引并跑 lint。

### 🍎 macOS / Linux bash 一键安装

```bash
# 1. 下载
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki

# 2. 一键安装
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL
```

参数说明：
- `--target-dir`：你的项目目录（不存在会自动创建）
- `--entity-name`：第一个想追踪的 entity 名称（股票代码 / 书名 / 人名都行）
- `--force`：如果目标目录已经有 wiki，覆盖
- `--skip-index`：跳过最后的索引 + lint

### 安装完打开 Claude Code 对它说

> 读一下 `wiki/_schema.md`、`wiki/_protocols.md` 和 `CLAUDE.md`，然后按 ingest 协议把我放进 `wiki/raw/` 的文件摄入到 wiki 里。

</details>

<details>
<summary><b>进阶：手动安装（5 分钟）</b></summary>

适合已经会用 git / 命令行 / Markdown 的人。

### 1. 克隆

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

### 2. 把 `CLAUDE.md` 复制到你的项目根目录

```bash
# 🍎 macOS / Linux
cp CLAUDE.md ../my-project/CLAUDE.md
```

```powershell
# 🪟 Windows PowerShell
Copy-Item .\CLAUDE.md ..\my-project\CLAUDE.md
```

如果项目**已经有**`CLAUDE.md`，不要覆盖——推荐用上面「本地脚本安装」折叠段里的脚本：它会把完整协议写入 `wiki/_protocols.md`，并只在现有 `CLAUDE.md` 里追加一小段轻量入口。

### 3. 把第一份原始材料丢进 `raw/`

```bash
# 🍎 macOS / Linux
cp ~/Downloads/some-research-paper.md wiki/raw/
```

```powershell
# 🪟 Windows PowerShell
Copy-Item "$HOME\Downloads\some-research-paper.md" .\wiki\raw\
```

### 4. 打开 Claude Code，对它说

> 读一下 `wiki/_schema.md` 和 `CLAUDE.md`，然后按 ingest 协议把 `wiki/raw/some-research-paper.md` 摄入到 wiki 里。如果你用 Obsidian Clippings，也可以先让 agent 扫描。

Claude 会：创建 `wiki/sources/<日期>-<slug>.md` 写结构化总结、识别实体/概念并创建或更新页面、用 `[[wikilinks]]` 加交叉引用、追加一行到 `_log.md`。

完成第一次 ingest 后，根据效果调整 schema，继续喂更多内容。

</details>

---

## 这个模板**不**包含什么

- **没有向量数据库**。Markdown + frontmatter + LLM 上下文窗口已经够用。
- **没有 GUI**。Obsidian、VSCode 或任意 markdown 编辑器都行。也可以一个都不用——直接和 LLM 对话。
- **没有领域内容**。这里故意是空的。Yibo 的投资 wiki 用了 2 个月之后有 34 个 entities 和 111 个 sources；你的会长成完全不同的样子。

---

## 致谢

- [Andrej Karpathy](https://x.com/karpathy/status/2039805659525644595) — 原始想法与框架
- [Karpathy 的 gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — "想法文件"
- [Stewart Brand《How Buildings Learn》](https://en.wikipedia.org/wiki/How_Buildings_Learn) — shearing layers 原则
- [Claude Code](https://claude.com/claude-code) — 本模板针对其设计的 agent 框架

## 协议

MIT。Fork 它、改它、发布它。做出有意思的东西欢迎告诉作者。

## 关于作者

更多投资思考、研究方法与系统化协作的文章，欢迎关注微信公众号 **奔波儿r**：

<p align="center">
  <img src="assets/wechat-qr.jpg" alt="奔波儿r 公众号二维码" width="240"/>
</p>

---

# English

> A personal LLM knowledge-base template, **inspired by [Andrej Karpathy's tweet](https://x.com/karpathy/status/2039805659525644595)** on building personal wikis with LLMs. Optimized for [Claude Code](https://claude.com/claude-code) but works with any AI agent that can read & write files.
>
> **Status**: Empty template. You decide what goes in; the LLM handles the bookkeeping.

**Last updated**: `2026-04-18`

**Pick the path that matches you:**

| Who you are | Where to go |
|---|---|
| 🤖 **Anyone, especially non-technical users** | [**Let Claude Code / an AI agent install it (recommended)**](#-recommended-let-claude-code--an-ai-agent-install-it) |
| 📄 **Plan to ingest research reports / long docs** | [Optional: external-LLM helper for large ingests](#-optional-external-llm-helper-for-large-ingests) |
| 🧑‍💻 **Prefer local scripts / don't want an agent touching your disk** | [Advanced: local script install](#advanced-local-script-install-windows--macos--linux) (collapsible) |

## Recent Updates

- `2026-04-18`: Released `v0.2.0` — the generated wiki now defaults to Simplified Chinese, with English kept as an optional locale; installers, install protocol, templates, and CI smoke tests are now aligned to that behavior
- `2026-04-18`: Added `.claude/commands/ingest.md`, so Claude Code can trigger the ingest workflow via `/ingest` or `/ingest <path>`
- `2026-04-18`: Added `scripts/wiki_cli.py`: a command-based ingest entrypoint with `ingest` / `scan`, so the workflow no longer has to be purely agent-prompt driven
- `2026-04-17`: README restructured — "Let Claude Code / an AI agent install it" is now the top-recommended path; local scripts and manual install collapsed under "Advanced"
- `2026-04-17`: Added `scripts/ingest_helper.py` + `.env.example`: optional external-LLM helper for large ingests, supporting 5 OpenAI-compatible providers — Kimi / Zhipu GLM / DeepSeek / Alibaba Qwen / OpenAI (the first four have free tiers in mainland China)
- `2026-04-18`: Generated wiki now defaults to Simplified Chinese, with an optional English locale via `--language en` or an explicit English-template request
- `2026-04-12`: Added `explorations/_template.md` and `decisions/_template.md` with hypothesis branches, alternatives, action triggers, and Lessons → Rules feedback loop
- `2026-04-12`: `rules.md` now has a Rule Lifecycle (`observation → pattern → RULE → under review → retired`) with Promotion Log tracking all lifecycle events
- `2026-04-12`: `inbox-digest.md` upgraded to weekly grouping with 60-day rolling archive to `inbox-archive.md`
- `2026-04-12`: Expanded all EXAMPLE files into fully annotated examples; added source-summary example; hardened Python detection in installers; CI upgraded to v6
- `2026-04-09`: Clean-slate default template; bash installer bugfixes; unified installer behaviour
- Full history: [`CHANGELOG.md`](./CHANGELOG.md)

---

## What is this?

A markdown-based personal wiki where **you curate, the LLM maintains**. Drop a research note into `wiki/raw/` and the LLM compiles it into structured `sources/`, updates `concepts/` and `entities/`, builds cross-references, and flags contradictions with what you already believe.

```
wiki/
├── _schema.md          # The constitution. AI reads this before every action.
├── _log.md             # Operation log.
├── raw/                # Immutable original materials (PDFs, articles, transcripts).
├── sources/            # Compiled summaries, one page per source.
├── entities/           # Companies, people, books, projects — anything you track.
├── concepts/           # Themes, frameworks, ideas that connect entities.
├── explorations/       # Crystallized answers to research questions.
├── decisions/          # Decision log with reasoning + trade-offs.
├── rules.md            # Rules confirmed by 3+ instances.
├── false-beliefs.md    # Conventional wisdom that data has refuted.
└── comparisons/        # Side-by-side comparisons.
```

The five layers are organized by **rate of change**: `raw/` never changes → `sources/` rarely → `entities/` + `concepts/` weekly–monthly → `explorations/` per-query → `rules.md` + `false-beliefs.md` quarterly.

**Why this is different from Notion / Obsidian / RAG**: traditional KBs are written for the *future you* who'll come back and read them — the maintenance cost eventually kills them. This template is written for the **LLM that re-reads it on every query**. Maintenance is the LLM's job; yours is curation. **No vector database** — markdown + frontmatter + the LLM's context window is enough. (Karpathy's insight: a personal wiki is small enough to not need RAG.)

---

## 🤖 Recommended: Let Claude Code / an AI agent install it

**The simplest path.** No downloading the project, no opening a terminal, no typing commands — the whole flow is: open your AI agent, send one message.

### 1. Open Claude Code (or Cursor / Cline / Windsurf / any agent that can fetch URLs and write files)

### 2. Send this message:

> Install this for me: https://github.com/Benboerba620/karpathy-claude-wiki/blob/main/INSTALL-FOR-AI.md

### 3. The agent will walk you through the 6-phase protocol in `INSTALL-FOR-AI.md`

It will ask you 4 questions (one at a time):

1. **Where should the wiki live?** (default: `./wiki/`)
2. **What's your primary domain?** (`investing` / `research` / `reading` / `writing` / `mixed`)
3. **Do you already have a `CLAUDE.md` at your project root?**
4. **What's one example entity you want to start tracking?** (a stock ticker, book title, person's name, project codename)

By default the generated wiki is in Simplified Chinese. If you explicitly want an English template, tell the agent that directly.

Once you've answered, the agent clones the template, customizes for your domain (if not the default `investing`), writes `wiki/_protocols.md`, lightly integrates or copies `CLAUDE.md`, scaffolds the entity you named, generates the index, and cleans up. **No further commands from you.**

### Beginner FAQ

- **No git / Markdown / CLI experience? Can I still use it?** Yes — this path is designed for exactly that. The agent handles all the technical work.
- **Do I need to understand schema / protocol first?** No. Install it, use it, read docs when you need.
- **No Python installed?** The install won't fail; only `_index.json` and `overview.md` navigation files get skipped. Install Python later and run `python scripts/wiki_index.py` once.
- **I just want to try it without polluting an existing project.** Tell the agent to put the wiki in a brand-new empty folder.
- **I don't have Claude Code. Alternatives?** [Cursor](https://cursor.com/), [Cline](https://cline.bot/), [Windsurf](https://codeium.com/windsurf), or any AI agent that can fetch URLs. Or see the collapsed "Advanced: local script install" section below.

---

## 📄 Optional: external-LLM helper for large ingests

> **When this is worth installing**: your primary use case is ingesting multi-page research reports, long podcast transcripts, or full books.
> **When you can skip it**: you'll mostly feed short articles / notes / conversations. The main agent reads those directly.

**Why you'd want it**: multi-hundred-page PDFs fed into the main Claude / Cursor conversation burn a ton of context. `scripts/ingest_helper.py` offloads the "compress PDF → structured JSON" step to a cheaper OpenAI-compatible LLM, and the main agent uses that JSON to generate the `sources/` page quickly.

**Five supported providers** (any one works; the first four have free tiers in mainland China):

| Provider | Sign up | Free tier / note |
|---|---|---|
| **Kimi / Moonshot** | [platform.moonshot.cn](https://platform.moonshot.cn/) | Strong on long text, free credits for new users |
| **Zhipu GLM** | [bigmodel.cn](https://bigmodel.cn/) | `glm-4-flash` is free as of 2026-01 |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com/) | Trial credits for new users |
| **Alibaba Qwen** | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/) | DashScope OpenAI-compatible mode |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) | Or any OpenAI-compatible endpoint (override `base_url`) |

**Three-step setup**:

```bash
# 1. Copy the config template
cp .env.example .env

# 2. Edit .env, uncomment ONE provider block, paste the API key
#    (the script auto-detects whichever one you configured)

# 3. Install dependencies
pip install requests pypdf
```

**Usage examples**:

```bash
# Read a PDF, print structured JSON to stdout
python scripts/ingest_helper.py --pdf wiki/raw/my-report.pdf

# Explicitly pick a provider
python scripts/ingest_helper.py --pdf my.pdf --provider glm

# Write JSON to a file (the main agent then reads it to generate the sources/ page)
python scripts/ingest_helper.py --pdf my.pdf --out /tmp/summary.json
```

The JSON output contains `title / date / tldr / key_data / quotes / implications / verifiable_predictions / open_questions / entities_mentioned / concepts_mentioned` — mapping cleanly onto the `sources/<date>-<slug>.md` page fields.

> 📝 **Tip**: if you're going via the AI-agent install path above, during Phase 2 just tell the agent to **also** copy `scripts/ingest_helper.py`, `.env.example`, and `skills/wiki-ingest/` into your project. If you're using the local installers below instead, the installer now copies `skills/wiki-ingest/` by default. `wiki/raw/` is now a flat inbox by default, and Obsidian Clippings can be scanned optionally.

---

## ⌨️ Optional: command-based ingest

If you do not want ingest to rely purely on an agent prompt, the repo now ships a CLI entrypoint:

```bash
# Archive the raw file, generate a sources page, update _log / inbox-digest, then run index + lint
python scripts/wiki_cli.py ingest path/to/source.md

# Pair it with the optional helper for large PDFs / long docs
python scripts/ingest_helper.py --pdf my.pdf --out /tmp/my.json
python scripts/wiki_cli.py ingest my.pdf --summary-json /tmp/my.json

# Scan wiki/raw/ and optional Obsidian Clippings
python scripts/wiki_cli.py scan --include-obsidian-clippings --json
```

By default, `wiki_cli.py ingest` will:

- copy the original file into `wiki/raw/` when needed
- create `wiki/sources/YYYY-MM-DD-slug.md`
- update `wiki/_log.md`
- update `wiki/inbox-digest.md`
- try to back-link existing entity / concept pages
- run `python scripts/wiki_index.py` and `python scripts/wiki_index.py --lint`

If you also installed `scripts/ingest_helper.py`, command-based ingest composes cleanly with the large-file helper workflow.

---

## `/ingest`: slash command for Claude Code

If you are using Claude Code, the repo now also ships a real slash command:

```text
/ingest
/ingest wiki/raw/some-research-paper.md
```

The command file lives at `.claude/commands/ingest.md`. It tells Claude to read `wiki/_schema.md`, `wiki/_protocols.md`, and `CLAUDE.md` first, then run the ingest workflow. If `scripts/wiki_cli.py` exists, the command can use it for the boilerplate parts of the ingest.

The local installers copy this slash command into the target project as well. If the target project already has its own `.claude/commands/ingest.md`, the installer skips it instead of overwriting it silently.

---

<details>
<summary><b>Advanced: local script install (Windows / macOS / Linux)</b></summary>

For users who'd rather not let an AI agent touch their disk, or who don't have Claude Code / Cursor access.

### 🪟 Windows PowerShell one-shot install

```powershell
# 1. Download the project
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki

# 2. One-shot install into a target directory (replace with your own path and entity name)
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"

# Optional: generate an English wiki instead of the default Simplified Chinese one
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL" -Language en

# Optional: also copy scripts/ingest_helper.py + .env.example for large ingests
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL" -WithIngestHelper
```

No git? Use **Code → Download ZIP** on GitHub, unzip, `cd` in.

The script: copies `wiki/`, strips local generated files / raw materials from the template copy, copies `.claude/commands/ingest.md`, copies `scripts/wiki_index.py`, copies `scripts/wiki_cli.py`, copies `skills/wiki-ingest/`, optionally copies `scripts/ingest_helper.py` + `.env.example`, handles `CLAUDE.md` (if one exists, adds only a lightweight entry + writes the full protocol to `wiki/_protocols.md`), scaffolds your first trackable entity, and generates the index + runs lint when Python is available. The installed wiki defaults to Simplified Chinese; pass `-Language en` for English.

### 🍎 macOS / Linux bash one-shot install

```bash
# 1. Download
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki

# 2. One-shot install
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL

# Optional: generate an English wiki instead of the default Simplified Chinese one
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL --language en

# Optional: also copy scripts/ingest_helper.py + .env.example for large ingests
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL --with-ingest-helper
```

Flags:
- `--target-dir` — your project directory (auto-created if missing)
- `--entity-name` — first entity to scaffold (a ticker / book / person)
- `--language` — `zh-CN` (default) or `en`
- `--force` — overwrite an existing wiki at the target
- `--skip-index` — skip the final index + lint step
- `--with-ingest-helper` — also copy `scripts/ingest_helper.py` and `.env.example`

### After installation, open Claude Code and say:

> Read `wiki/_schema.md`, `wiki/_protocols.md`, and `CLAUDE.md`, then ingest the file I dropped in `wiki/raw/` following the ingest protocol. If I use Obsidian Clippings, scan that optional inbox first.

</details>

## What's NOT in this template

- **No vector database.** Markdown + frontmatter + LLM context window is enough.
- **No GUI.** Use Obsidian, VSCode, or any markdown editor. Or none at all — talk to the LLM.
- **No domain content.** Intentionally empty. Yibo's investing wiki has 34 entities and 111 sources after 2 months; yours will look different.

---

## Credit & inspiration

- [Andrej Karpathy](https://x.com/karpathy/status/2039805659525644595) — original idea & framing
- [Karpathy's gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the "idea file"
- [Stewart Brand's *How Buildings Learn*](https://en.wikipedia.org/wiki/How_Buildings_Learn) — shearing layers principle
- [Claude Code](https://claude.com/claude-code) — the agent harness this was designed for

## License

MIT. Fork it, change it, ship it. Tell me what you build.

---

*If you build something interesting on top of this, open an issue or PR.*
