[中文](#中文) ｜ [English](#english)

# 中文

> 一个个人 LLM 知识库模板，**灵感来自 [Andrej Karpathy 的推文](https://x.com/karpathy/status/2039805659525644595)** —— 用 LLM 来构建和维护个人 wiki。本模板针对 [Claude Code](https://claude.com/claude-code) 优化，但任何能读写文件的 AI agent 都可以使用。
>
> **状态**：空模板。你负责放资料、提问题；LLM 负责整理、交叉引用、回写和持续维护。

**Last updated**：`2026-04-08`

**直接按你的情况选一条路：**

| 你是谁 | 走哪条路 |
|---|---|
| 🪟 **Windows 用户 + 编程小白**（投资者 / 研究员） | [一键安装（PowerShell 脚本）](#-windows-小白一键安装推荐) |
| 🍎 **macOS / Linux 用户 + 编程小白** | [一键安装（bash 脚本）](#-macos--linux-小白一键安装) |
| 🧑‍💻 **会用 Git / 命令行** | [手动安装（5 分钟）](#手动安装5-分钟) |
| 🤖 **想让 AI agent 帮你装** | 把 [`INSTALL-FOR-AI.md`](./INSTALL-FOR-AI.md) 的链接发给 Claude Code，说"帮我装这个" |

## 最近更新

- `2026-04-08`：新增 `python scripts/wiki_index.py --report`，生成 `wiki/_attention.md` 注意力 / 链接结构报告
- `2026-04-08`：新增 GitHub Actions `Wiki Lint`，提交和 PR 会自动检查 wiki 健康状态
- `2026-04-08`：新增 `scripts/install_wiki.ps1`，Windows 小白用户可一键安装
- `2026-04-08`：优化 `README` 首页导流，第一次来的用户更容易知道该怎么开始
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

## 🪟 Windows 小白：一键安装（推荐）

如果你 **第一次接触这类项目** + **不会 Git / Markdown / 命令行**，按这 4 步来。

**开始前你只需要知道**：
- 你**不需要**先懂 schema、protocol、frontmatter 这些词
- 你**不需要**会 Markdown；你的工作是"丢文件 + 提问题"
- 推荐环境：**Windows + PowerShell + Claude Code**

### 1. 下载这个项目

二选一：
- 会用 git：`git clone https://github.com/Benboerba620/karpathy-claude-wiki.git`
- 不会用 git：在 GitHub 页面点 **Code → Download ZIP**，解压

### 2. 打开 PowerShell，进入项目文件夹

```powershell
cd 你的项目路径\karpathy-claude-wiki
```

### 3. 一键安装到你的项目目录

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"
```

这一条命令会自动帮你：复制 `wiki/`、复制 `scripts/wiki_index.py`、处理 `CLAUDE.md`、创建第一个可跟踪的 entity（这里是 `AAPL`，你可以换成任意股票代码 / 书名 / 人名）、生成索引并跑 lint。

如果你还没有自己的项目目录，把 `-TargetDir` 指到一个全新的空文件夹即可：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-wiki-project" -EntityName "AAPL"
```

### 4. 打开 Claude Code，对它说

> 读一下 `wiki/_schema.md` 和 `CLAUDE.md`，然后按 ingest 协议把我放进 `wiki/raw/` 的文件摄入到 wiki 里。

### 小白常见问题

- **不懂 Git，能用吗？** 可以，下载 ZIP 解压也行。
- **不懂 Markdown，能用吗？** 可以，你的工作是"丢文件 + 提问题"，整理交给 AI。
- **必须先懂 schema / protocol 吗？** 不必。先装起来、跑起来，后面再慢慢看。
- **没装 Python，会失败吗？** 不一定。安装脚本会尽量继续执行；只是会跳过索引生成，之后装好 Python 再运行 `python scripts/wiki_index.py` 即可。
- **只想先试试，不想污染现有项目？** 把 `-TargetDir` 指到一个全新的空文件夹。

---

## 🍎 macOS / Linux 小白：一键安装

和 Windows 版完全等价的 bash 脚本，行为一样。

### 1. 下载

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

不会用 git：从 GitHub 页面 **Code → Download ZIP**，解压，`cd` 进去。

### 2. 一键安装

```bash
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL
```

参数说明：
- `--target-dir`：你的项目目录（不存在会自动创建）
- `--entity-name`：第一个想追踪的 entity 名称（股票代码 / 书名 / 人名都行）
- `--force`：如果目标目录已经有 wiki，覆盖
- `--skip-index`：跳过最后的索引 + lint

macOS 默认装了 Python 3，如果你之前删过，脚本会优雅跳过索引那一步，提醒你之后手动跑。

### 3. 打开 Claude Code，对它说

> 读一下 `wiki/_schema.md` 和 `CLAUDE.md`，然后按 ingest 协议把我放进 `wiki/raw/` 的文件摄入到 wiki 里。

---

## 手动安装（5 分钟）

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

如果项目**已经有**`CLAUDE.md`，不要覆盖。把本仓库里的协议内容手动合并进去（或者用上面的一键安装脚本，它会自动 append）。

### 3. 把第一份原始材料丢进 `raw/`

```bash
# 🍎 macOS / Linux
cp ~/Downloads/some-research-paper.md wiki/raw/papers/
```

```powershell
# 🪟 Windows PowerShell
Copy-Item "$HOME\Downloads\some-research-paper.md" .\wiki\raw\papers\
```

### 4. 打开 Claude Code，对它说

> "读一下 `wiki/_schema.md` 和 `CLAUDE.md`，然后按 ingest 协议把 `wiki/raw/papers/some-research-paper.md` 摄入到 wiki 里。"

Claude 接下来会：
- 创建 `wiki/sources/<日期>-<slug>.md`，写一份结构化总结
- 识别其中提到的 entities 和 concepts，创建或更新对应页面
- 用 `[[wikilinks]]` 添加交叉引用
- 追加一行到 `_log.md`

完成第一次 ingest 之后，根据效果调整 schema，然后继续摄入更多内容。

---

## 让 AI agent 帮你装

打开 Claude Code（或 Cursor / Cline 等任何能读取 URL + 文件的 agent），把这条消息发给它：

> 帮我装这个：https://github.com/Benboerba620/karpathy-claude-wiki/blob/main/INSTALL-FOR-AI.md

Agent 会按 `INSTALL-FOR-AI.md` 里的 6 阶段协议走完整个流程：澄清你的领域、克隆模板、（如果需要）按你的领域定制、合并 `CLAUDE.md`、创建第一个 entity、生成索引、交付。

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

**Last updated**: `2026-04-08`

**Pick the path that matches you:**

| Who you are | Where to go |
|---|---|
| 🪟 **Windows + coding beginner** (investor / analyst) | [One-shot install (PowerShell)](#-windows-beginner-one-shot-install-recommended) |
| 🍎 **macOS / Linux + coding beginner** | [One-shot install (bash)](#-macos--linux-beginner-one-shot-install) |
| 🧑‍💻 **Comfortable with git / CLI** | [Manual install (5 minutes)](#manual-install-5-minutes) |
| 🤖 **Want an AI agent to install it for you** | Send [`INSTALL-FOR-AI.md`](./INSTALL-FOR-AI.md) to Claude Code and say "install this for me" |

## Recent Updates

- `2026-04-08`: Added `python scripts/wiki_index.py --report` to generate the attention / link-graph report in `wiki/_attention.md`
- `2026-04-08`: Added GitHub Actions `Wiki Lint` for automatic wiki health checks on pushes and PRs
- `2026-04-08`: Added `scripts/install_wiki.ps1` for beginner-friendly Windows setup
- `2026-04-08`: Improved README routing so first-time visitors can pick the right install path faster
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

## 🪟 Windows beginner: one-shot install (recommended)

If you're **new to projects like this** + **don't know git / Markdown / CLI**, follow these 4 steps.

**Before you start, you only need to know**:
- You **don't** need to understand schema, protocol, or frontmatter
- You **don't** need to know Markdown — your job is "drop files, ask questions"
- Recommended environment: **Windows + PowerShell + Claude Code**

### 1. Download the project

Either:
- With git: `git clone https://github.com/Benboerba620/karpathy-claude-wiki.git`
- Without git: on GitHub, click **Code → Download ZIP**, then unzip it

### 2. Open PowerShell and `cd` into the project folder

```powershell
cd path\to\karpathy-claude-wiki
```

### 3. One-shot install into your project directory

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"
```

This single command copies `wiki/`, copies `scripts/wiki_index.py`, sets up `CLAUDE.md`, scaffolds your first trackable entity (here `AAPL` — replace with any ticker / book / person), and generates the index + lint report.

No project directory yet? Point `-TargetDir` at a new empty folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-wiki-project" -EntityName "AAPL"
```

### 4. Open Claude Code and say:

> Read `wiki/_schema.md` and `CLAUDE.md`, then ingest the file I dropped in `wiki/raw/` following the ingest protocol.

### Beginner FAQ

- **No git? Can I still use it?** Yes — the ZIP download works.
- **No Markdown experience?** Fine. Your job is "drop files, ask questions"; the AI does the formatting.
- **Do I need to understand schema / protocol first?** No. Install it, run it, learn as you go.
- **No Python?** The installer will gracefully skip the index step. Install Python later, then run `python scripts/wiki_index.py`.
- **I just want to try it without polluting an existing project.** Point `-TargetDir` at a new empty folder.

---

## 🍎 macOS / Linux beginner: one-shot install

Behaviour-equivalent bash version of the PowerShell installer.

### 1. Download

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

No git? Use **Code → Download ZIP** on GitHub, unzip, `cd` in.

### 2. One-shot install

```bash
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL
```

Flags:
- `--target-dir` — your project directory (auto-created if missing)
- `--entity-name` — first entity to scaffold (a ticker / book / person)
- `--force` — overwrite an existing wiki at the target
- `--skip-index` — skip the final index + lint step

macOS ships Python 3 by default; if you've removed it the script will skip the index step gracefully and tell you to run it later.

### 3. Open Claude Code and say:

> Read `wiki/_schema.md` and `CLAUDE.md`, then ingest the file I dropped in `wiki/raw/` following the ingest protocol.

---

## Manual install (5 minutes)

For people already comfortable with git / CLI / Markdown.

### 1. Clone

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

### 2. Copy `CLAUDE.md` to your project root

```bash
# 🍎 macOS / Linux
cp CLAUDE.md ../my-project/CLAUDE.md
```

```powershell
# 🪟 Windows PowerShell
Copy-Item .\CLAUDE.md ..\my-project\CLAUDE.md
```

If your project **already has** a `CLAUDE.md`, don't overwrite it. Merge the wiki protocols in manually (or use one of the one-shot installers above — they auto-append).

### 3. Drop a first source into `raw/`

```bash
# 🍎 macOS / Linux
cp ~/Downloads/some-research-paper.md wiki/raw/papers/
```

```powershell
# 🪟 Windows PowerShell
Copy-Item "$HOME\Downloads\some-research-paper.md" .\wiki\raw\papers\
```

### 4. Open Claude Code and say:

> "Read `wiki/_schema.md` and `CLAUDE.md`, then ingest `wiki/raw/papers/some-research-paper.md` following the ingest protocol."

That's it. Claude will:
- Create `wiki/sources/<date>-<slug>.md` with a structured summary
- Detect the entities and concepts mentioned, create or update those pages
- Add cross-references using `[[wikilinks]]`
- Append to `_log.md`

After your first ingest, refine the schema based on what worked, then ingest more.

---

## Let an AI agent install it for you

Open Claude Code (or Cursor / Cline / any agent that can fetch URLs and write files) and paste:

> Install this for me: https://github.com/Benboerba620/karpathy-claude-wiki/blob/main/INSTALL-FOR-AI.md

The agent will follow the 6-phase protocol in `INSTALL-FOR-AI.md`: clarify your domain, clone the template, customize for your domain (if needed), merge `CLAUDE.md`, scaffold your first entity, generate the index, and hand off.

---

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
