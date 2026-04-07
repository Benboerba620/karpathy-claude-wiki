[中文](#中文) | [English](#karpathy-claude-wiki)

# 中文

> 一个个人 LLM 知识库模板,**灵感来自 [Andrej Karpathy 的推文](https://x.com/karpathy/status/2039805659525644595)**——用 LLM 来构建和维护个人 wiki。本模板针对 [Claude Code](https://claude.com/claude-code) 优化,但任何能读写文件的 AI agent 都可以使用。

**状态**: 空模板。你负责放资料、提问题; LLM 负责整理、交叉引用、回写和持续维护。

**如果你是第一次来这个项目,直接按下面分流:**
- **中文 Windows 小白用户** → 看 `给中文小白用户:最简单安装方法`
- **已经会 Git / Markdown / 命令行** → 看 `快速上手(进阶/手动安装,5 分钟)`
- **想让 AI agent 自动帮你装** → 看 `AI 自动安装协议`

**你会得到什么:**
- 一个放在本地、纯 Markdown 的个人 wiki
- 一套让 Claude / Cursor / Cline 按协议维护 wiki 的规则
- 一个可以自动生成索引并检查健康状态的脚本
- 一个对 Windows / PowerShell 更友好的安装入口

**它适合谁:**
- 想把研究、阅读、投资、写作资料长期积累下来的人
- 希望“自己负责判断什么值得收录,AI 负责整理”的人
- 不想先搭数据库、前端、RAG 系统,想先把东西用起来的人

**它不太适合谁:**
- 想立刻得到一个现成内容库的人
- 完全不打算使用 AI agent,只想手工记笔记的人
- 需要多人实时协作、权限管理、在线服务端的团队场景

---

## 给中文小白用户:最简单安装方法(Windows,推荐)

如果你主要是 **中文用户 + Windows 用户 + 第一次接触这类项目**,推荐你先不要看后面的完整协议,直接按这 4 步来。

**开始前你只需要知道三件事:**
- 你**不需要**先懂 schema、protocol、frontmatter 这些词
- 你**不需要**会 Markdown; 你主要做的是“放文件 + 提问题”
- 最推荐的环境是 **Windows + PowerShell + Claude Code**

### 1. 下载项目

你可以二选一:
- 会用 git: `git clone https://github.com/Benboerba620/karpathy-claude-wiki.git`
- 不会用 git: 直接在 GitHub 页面点 **Code → Download ZIP** 下载后解压

### 2. 打开 PowerShell,进入这个项目文件夹

```powershell
cd 你的项目路径\karpathy-claude-wiki
```

### 3. 一键安装到你的项目目录

下面这个命令会自动帮你完成这几件事:
- 复制 `wiki/`
- 复制 `scripts/wiki_index.py`
- 处理 `CLAUDE.md`
- 创建第一个可跟踪的 entity
- 自动生成索引并跑一次 lint

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"
```

如果你还没有自己的项目目录,也可以先这样试:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-wiki-project" -EntityName "AAPL"
```

### 4. 打开 Claude Code,然后直接说

> 读一下 `wiki/_schema.md` 和 `CLAUDE.md`,然后按 ingest 协议把我放进 `wiki/raw/` 的文件摄入到 wiki 里。

### 小白常见问题

- **我不懂 Git,能用吗?** 可以,下载 ZIP 解压也能用。
- **我不懂 Markdown,能用吗?** 可以,你主要是“丢文件 + 提问题”,整理工作交给 AI。
- **我必须先懂 schema / protocol 吗?** 不必。第一次先装起来、跑起来,后面再慢慢看。
- **我是 Windows 用户,会不会麻烦?** 现在已经提供 PowerShell 安装脚本,比手动复制文件简单很多。
- **我没装 Python,会失败吗?** 不一定。安装脚本会尽量继续执行; 只是会跳过索引生成,你之后装好 Python 再运行 `python scripts/wiki_index.py` 即可。
- **我只想先试试,不想污染现有项目?** 可以,直接把 `-TargetDir` 指到一个全新的空文件夹。

---

## 这是什么?

一个基于 markdown 的个人 wiki,**用户负责策展,LLM 负责维护**。把一份研究笔记丢进 `wiki/raw/`,LLM 会自动把它编译成结构化的 `sources/` 页面、更新 `concepts/` 和 `entities/`、建立交叉引用,并标记任何与你已有信念相冲突的地方。

整个架构如下:

```
wiki/
├── _schema.md          # 宪法。AI 在每次操作前都会先读它
├── _log.md             # 操作日志(谁在什么时候为什么改了什么)
├── raw/                # 不可变的原始材料(PDF、文章、文字稿)
├── sources/            # 编译后的总结,每个来源一页,必须有 frontmatter
├── entities/           # 公司、人、书、项目——任何想追踪的对象
├── concepts/           # 主题、框架、把 entities 联系起来的想法
├── explorations/       # 研究问题的固化答案(回写)
├── decisions/          # 决策日志,含理由 + 取舍
├── rules.md            # 被 3 次以上验证过的规律
├── false-beliefs.md    # 被数据推翻的常识
└── comparisons/        # 并排对比(A vs B)
```

这五层按 **变化速率** 组织:

| 层 | 速度 | 例子 |
|---|---|---|
| `raw/` | 永远不变 | PDF、全文文章 |
| `sources/` | 很少变 | 结构化总结 |
| `entities/` + `concepts/` | 周/月级 | profile、主题 |
| `explorations/` + `decisions/` | 随查询而变 | 固化的答案 |
| `rules.md` + `false-beliefs.md` | 季度级 | 来之不易的教训 |

---

## 为什么和 Notion / Obsidian / RAG 不一样

| 维度 | 传统知识库 | 本模板 |
|---|---|---|
| **读者** | 你(某天) | LLM(每次查询) |
| **维护者** | 你(所以它会死) | LLM(所以它能活) |
| **组织方式** | 文件夹 + 标签 | 按变化速率分层 + 显式交叉引用 |
| **输出** | 你打开文件读 | 你提问,AI 在整个 wiki 上推理 |

关键的转变是:**维护成本趋近于零**,因为 LLM 替你做所有的整理工作。用户的角色从"清洁工"变成"策展人"。

---

## 快速上手(进阶/手动安装,5 分钟)

> 下面默认给出 bash 命令; 如果你在 Windows PowerShell 里操作,对应命令也一起写在下面。

### 1. 克隆

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

### 2. 阅读 schema

```bash
cat wiki/_schema.md
```

```powershell
Get-Content .\wiki\_schema.md
```

这是 wiki 的"宪法"。AI 在每次操作前都会先读它。

### 3. 把 CLAUDE.md 移到你的项目根目录

```bash
# 如果目标项目还没有 CLAUDE.md,直接复制
cp CLAUDE.md ../my-project/CLAUDE.md
```

```powershell
# 如果目标项目还没有 CLAUDE.md,直接复制
Copy-Item .\CLAUDE.md ..\my-project\CLAUDE.md
```

如果目标项目**已经有** `CLAUDE.md`,不要直接覆盖。把本仓库里的协议内容手动合并进去,或者交给 AI agent 按下面的“AI 自动安装协议”处理。

### 4. 把第一份原始材料丢进 raw/

```bash
cp ~/Downloads/some-research-paper.md wiki/raw/papers/
```

```powershell
Copy-Item "$HOME\Downloads\some-research-paper.md" .\wiki\raw\papers\
```

### 5. 打开 Claude Code,然后对它说:

> "读一下 `wiki/_schema.md` 和 `CLAUDE.md`,然后按 ingest 协议把 `wiki/raw/papers/some-research-paper.md` 摄入到 wiki 里。"

就这些。Claude 接下来会:
- 创建一个带结构化总结的 `wiki/sources/<日期>-<slug>.md`
- 识别其中提到的 entities 和 concepts,创建或更新对应页面
- 用 `[[wikilinks]]` 语法添加交叉引用
- 追加一行到 `_log.md`

完成第一次 ingest 之后,根据效果调整 schema,然后继续摄入更多内容。

---

## AI 自动安装协议

> **给 AI agent(Claude Code、Cursor、Cline 等)**:如果用户把这份 README 的 URL 贴给你并说"帮我装这个",请**按顺序**执行下面的步骤,不要跳过澄清阶段。

### 阶段 1 — 澄清(向用户提问,一次一个问题)

1. **"wiki 应该放在哪?"** 默认:当前项目下的 `./wiki/`。
2. **"你的主要领域是什么?"** 选项:`investing`(投资)、`research`(研究)、`reading`(阅读)、`writing`(写作)、`mixed`(混合)。这决定了 AI 如何为用户定制模板。
3. **"你的项目根目录是否已经有 `CLAUDE.md`?"**(yes / no)
4. **"举一个你想开始追踪的 entity 例子"**(比如一个股票代码、一本书的标题、一个人的名字、一个项目代号)。把这个答案记下来,阶段 5 会用。

### 阶段 2 — 克隆与提取

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
```

移动:
- `.karpathy-tmp/wiki/` → 用户选择的路径(默认 `./wiki/`)
- `.karpathy-tmp/scripts/wiki_index.py` → `./scripts/wiki_index.py`(如果 `scripts/` 不存在则创建)

⚠️ **此时不要删 `.karpathy-tmp/`**——阶段 4 还需要从 `.karpathy-tmp/CLAUDE.md` 读取协议内容。清理放到阶段 6 最后做。

### 阶段 3 — 根据用户领域定制

> ⚠️ **如果用户选了 `investing`,跳过整个阶段 3**——模板默认就是 investing 领域,不需要任何修改。

如果是其他领域,按以下三步走:

**3.1 — 重命名 entity 文件夹**

```bash
mv wiki/entities wiki/<新名称>
```

```powershell
Move-Item .\wiki\entities .\wiki\<新名称>
```

| 领域 | 新文件夹名 | 配套术语 |
|---|---|---|
| `research` | `subjects/` | `entity` → `subject` |
| `reading` | `authors/` | `entity` → `author`(可选删 `decisions/`) |
| `writing` | `references/` | `entity` → `reference`(可选删 `rules.md`) |
| `mixed` | (保留 `entities/`,按需添加 sibling 目录) | — |

**3.2 — 用词边界 find-replace 修正引用**

在两个文件里替换:
- `wiki/_schema.md`
- `.karpathy-tmp/CLAUDE.md`(注意:是模板的 CLAUDE.md,**不是**用户项目根目录的 CLAUDE.md)

⚠️ **必须用词边界正则**(例如 `\bentities\b` → `\bsubjects\b`),否则单数 `entity` 和复数 `entities` 会被同时改坏,造成"`entity` 页面应该列出它的 `subjects`"这种语义裂开的句子。

**3.3 — 同步更新模板的 frontmatter**

打开 `wiki/<新名称>/_template/profile.md`,替换以下硬编码字段:
- `type: entity` → `type: <新单数>`(例如 `subject`)
- `domain: [investing]` → `domain: [<用户领域>]`
- `judgment: watching/bullish/bearish/neutral` 是投资字段,不合适就改成更通用的词,或保留 `watching` 当占位

> 💡 `rules.md` 和 `false-beliefs.md` 里的示例(P/E ratio、supply chain)是 investing 风格的占位内容。本协议不自动重写它们——告诉用户这些是示例,首次 ingest 后自行替换即可。

### 阶段 4 — 整合 `CLAUDE.md`

**情况 A:用户没有 `CLAUDE.md`** —— 直接 `cp .karpathy-tmp/CLAUDE.md ./CLAUDE.md`。PowerShell:`Copy-Item .\.karpathy-tmp\CLAUDE.md .\CLAUDE.md`。完成。

**情况 B:用户已经有 `CLAUDE.md`** —— 追加,但必须做两件事:

1. **裁掉模板的 standalone 引言**。`.karpathy-tmp/CLAUDE.md` 开头有 "If you're a human reading this for the first time..." 这种适合独立文件的导言。append 时只从 `## Protocol 1 — Ingest` 开始,前面的所有行全部跳过,否则用户文件里会出现尴尬的内嵌旁白。

2. **把所有标题级别下移一级**,让追加的内容嵌套在新的父章节下:`# CLAUDE.md — Wiki Protocols` 整行删除,`## Protocol N` → `### Protocol N`,`### Phase N` → `#### Phase N`,以此类推。否则用户文件会出现两个 H1 + 同级混乱的层级。

追加格式:
```markdown
[用户原本的 CLAUDE.md 内容]

## Wiki Protocols (from karpathy-claude-wiki)

### Protocol 1 — Ingest
[已下移层级的内容...]

### Protocol 2 — Cross-Reference
...
```

操作完明确告诉用户:你裁掉了什么、追加了什么、改了哪些标题层级。

### 阶段 5 — 创建第一个 entity

使用阶段 1 第 4 题的示例 entity 名称。**路径取决于阶段 3 是否做了 rename**:

- 如果 `investing`(默认):用 `wiki/entities/<NAME>/profile.md` 和模板 `wiki/entities/_template/profile.md`
- 如果做了 rename:用 `wiki/<新文件夹>/<NAME>/profile.md` 和模板 `wiki/<新文件夹>/_template/profile.md`

复制模板到新位置,填好基础 frontmatter(title、created 日期、domain),正文部分留空。**不要替用户编造 thesis 内容**——那是用户的工作。

### 阶段 6 — 验证并交付

1. **生成索引**:`python scripts/wiki_index.py`(无参数)。这一步会生成 `wiki/_index.json` 和 `wiki/overview.md`。**没有这两个文件,wiki 没有索引,后续的 lint/search 全都没法跑**。如果用户没装 python,告诉他们装好后再手动跑一次。

2. **清理临时目录**:`rm -rf .karpathy-tmp`(阶段 2 推迟到现在做)。PowerShell 对应命令:`Remove-Item .\.karpathy-tmp -Recurse -Force`。

3. 给用户展示新建的 `wiki/` 目录树。

4. 确认 `CLAUDE.md` 整合成功(打印出相关章节)。

5. **告知用户 EXAMPLE 占位文件的处理方式**(不要自作主张删,让用户自己决定):
   > "模板里有几个 `EXAMPLE-*.md` 和 `EXAMPLE/` 文件,用来展示页面结构长什么样。它们对 ingest 无害(Claude 会识别为占位并跳过),但如果你想要完全干净的起点,运行下面这条命令清掉:
   > ```bash
   > rm wiki/*/EXAMPLE-*.md 2>/dev/null; rm -rf wiki/*/EXAMPLE/ 2>/dev/null
   > ```
   > PowerShell:
   > ```powershell
   > Get-ChildItem .\wiki -Recurse -File -Filter 'EXAMPLE-*.md' | Remove-Item -Force
   > Get-ChildItem .\wiki -Recurse -Directory -Filter 'EXAMPLE' | Remove-Item -Recurse -Force
   > ```
   > 不清也没事,看个人偏好。"

6. 对用户说,原文如下:
   > "Wiki 安装完成。要做第一次 ingest:把一个文件放进 `wiki/raw/<category>/`(`<category>` 可选 `articles` / `papers` / `books` / `podcasts` / `conversations`),然后说"按协议摄入这个"。第一次 ingest 会根据你的具体领域优化 schema。"

阶段 6 之后停止。不要预填内容。用户通过日常使用来填充 wiki。

---

## LLM 充当记账员的实际原理

核心洞察(来自 Karpathy,被多个实现验证):**杀死传统知识库的是记账工作**。不是思考,不是策展,而是记账。打标签、建链接、去重、总结、重新组织。

LLM 极其擅长记账。它们做这件事的方式跟人类一样,但它们不会像人类那样厌倦。

所以设计原则是:

1. **由人决定什么进入 wiki**(策展)
2. **由人决定问它什么**(查询)
3. **LLM 做剩下的所有事**(编译、交叉引用、矛盾扫描、回写)

`CLAUDE.md` 里的四个协议把这种分工固化下来:

- **摄入协议**(Ingest):用户给一份新来源时,LLM 把它总结到 `sources/`,提取 entities/concepts,更新对应页面。
- **交叉引用协议**(Cross-reference):更新一个 entity 时,LLM 检查相关的 concepts 和其他 entities 是否需要同步。
- **矛盾扫描协议**(Contradiction-scan):写下新判断时,LLM 检查 `false-beliefs.md` 和 `rules.md` 是否有冲突并标记。
- **固化协议**(Crystallization):某次查询产生了特别有用的答案时,LLM 主动提议把它存为一个 `exploration` 页面。

这四个协议是让 wiki "活"起来的关键。具体措辞参见 `CLAUDE.md`。

---

## 这个模板**不**包含什么

- **没有向量数据库**。Markdown + frontmatter + LLM 上下文窗口已经够用。Karpathy 的洞察是:个人 wiki 的体量足够小,根本不需要 RAG。
- **没有 GUI**。可以用 Obsidian、VSCode 或任意 markdown 编辑器。也可以一个都不用——直接和 LLM 对话即可。
- **没有领域内容**。这里故意是空的。Yibo 的投资 wiki 用了 2 个月之后有 34 个 entities 和 111 个 sources;你的会长成完全不同的样子。

---

## 致谢与灵感来源

- [Andrej Karpathy](https://x.com/karpathy/status/2039805659525644595) — 原始想法与框架
- [Karpathy 的 gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — "想法文件"
- [Stewart Brand《How Buildings Learn》](https://en.wikipedia.org/wiki/How_Buildings_Learn) — shearing layers(剪切层)原则
- [Claude Code](https://claude.com/claude-code) — 本模板针对其设计的 agent 框架

---

## 协议

MIT。Fork 它、改它、发布它。做出有意思的东西欢迎告诉作者。

---

## 关于作者

更多投资思考、研究方法与系统化协作的文章,欢迎关注微信公众号 **奔波儿r**:

<p align="center">
  <img src="assets/wechat-qr.jpg" alt="奔波儿r 公众号二维码" width="240"/>
</p>

---

[中文](#中文) | [English](#karpathy-claude-wiki)

# karpathy-claude-wiki

> A personal LLM Knowledge Base template, **inspired by [Andrej Karpathy's tweet](https://x.com/karpathy/status/2039805659525644595)** on building personal wikis with LLMs. Optimized for [Claude Code](https://claude.com/claude-code) but works with any AI agent that can read & write files.

**Status**: Empty template. You decide what goes in; the LLM handles the bookkeeping.

**If this is your first visit, use this route:**
- **Chinese + Windows beginner** → jump to `给中文小白用户:最简单安装方法`
- **Comfortable with Git / CLI** → jump to `Quick Start (Manual / advanced, 5 minutes)`
- **Want an AI agent to install it for you** → jump to `AI Auto-Install Protocol`

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

## Quick Start (Manual / advanced, 5 minutes)

> The examples below use bash by default. If you're on Windows PowerShell, equivalent commands are included too.

### 1. Clone

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

### 2. Read the schema

```bash
cat wiki/_schema.md
```

```powershell
Get-Content .\wiki\_schema.md
```

This is your wiki's "constitution". The AI will read it before every operation.

### 3. Move CLAUDE.md to your project root

```bash
# If the target project does not already have a CLAUDE.md, just copy it
cp CLAUDE.md ../my-project/CLAUDE.md
```

```powershell
# If the target project does not already have a CLAUDE.md, just copy it
Copy-Item .\CLAUDE.md ..\my-project\CLAUDE.md
```

If the target project **already has** a `CLAUDE.md`, don't overwrite it. Merge the wiki protocols in manually, or let an AI agent follow the "AI installation protocol" below.

### 4. Drop your first source into raw/

```bash
cp ~/Downloads/some-research-paper.md wiki/raw/papers/
```

```powershell
Copy-Item "$HOME\Downloads\some-research-paper.md" .\wiki\raw\papers\
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
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
```

Move:
- `.karpathy-tmp/wiki/` → user's chosen path (default `./wiki/`)
- `.karpathy-tmp/scripts/wiki_index.py` → `./scripts/wiki_index.py` (create `scripts/` if needed)

⚠️ **Do NOT delete `.karpathy-tmp/` yet** — Phase 4 still needs `.karpathy-tmp/CLAUDE.md`. Cleanup happens in Phase 6.

### Phase 3 — Customize for the user's domain

> ⚠️ **If the user picked `investing`, skip Phase 3 entirely** — the template ships with investing as the default and no customization is needed.

For non-investing domains, do these three steps:

**3.1 — Rename the entity folder**

```bash
mv wiki/entities wiki/<new-name>
```

```powershell
Move-Item .\wiki\entities .\wiki\<new-name>
```

| Domain | New folder | Term hint |
|---|---|---|
| `research` | `subjects/` | `entity` → `subject` |
| `reading` | `authors/` | `entity` → `author` (optionally drop `decisions/`) |
| `writing` | `references/` | `entity` → `reference` (optionally drop `rules.md`) |
| `mixed` | (keep `entities/`, add sibling dirs as needed) | — |

**3.2 — Word-boundary find-replace**

Apply to two files:
- `wiki/_schema.md`
- `.karpathy-tmp/CLAUDE.md` (the template's CLAUDE.md, **not** the user's project CLAUDE.md)

⚠️ **You must use word-boundary regex** (e.g. `\bentities\b` → `\bsubjects\b`). A naive `s/entities/subjects/g` will leave the singular `entity` unchanged and produce broken sentences like "the `entity` page should list its connected `subjects`".

**3.3 — Update the template's frontmatter**

Open `wiki/<new-name>/_template/profile.md` and replace the hard-coded fields:
- `type: entity` → `type: <new-singular>` (e.g. `subject`)
- `domain: [investing]` → `domain: [<chosen-domain>]`
- `judgment: watching/bullish/bearish/neutral` is investing-specific — replace with domain-appropriate values, or keep `watching` as a generic placeholder

> 💡 `rules.md` and `false-beliefs.md` ship with investing-flavored examples (P/E ratios, supply chains). This protocol does **not** auto-rewrite them — tell the user they're placeholders and to replace them after the first real ingest.

### Phase 4 — Integrate `CLAUDE.md`

**Case A: user has no `CLAUDE.md`** — just `cp .karpathy-tmp/CLAUDE.md ./CLAUDE.md`. PowerShell: `Copy-Item .\.karpathy-tmp\CLAUDE.md .\CLAUDE.md`. Done.

**Case B: user has an existing `CLAUDE.md`** — append, but with two transformations to avoid breaking the user's file:

1. **Trim the template's standalone intro.** `.karpathy-tmp/CLAUDE.md` starts with a "If you're a human reading this for the first time..." preamble that makes sense for a standalone file but becomes awkward in-file narration when merged. Skip everything before `## Protocol 1 — Ingest` and only append from there.

2. **Shift all heading levels down by one** so the appended content nests under the new parent section. Drop the `# CLAUDE.md — Wiki Protocols` H1 line entirely; turn `## Protocol N` → `### Protocol N`, `### Phase N` → `#### Phase N`, etc. Otherwise the user's file ends up with conflicting H1s and a broken hierarchy.

Append result format:
```markdown
[user's existing CLAUDE.md content]

## Wiki Protocols (from karpathy-claude-wiki)

### Protocol 1 — Ingest
[shifted content...]

### Protocol 2 — Cross-Reference
...
```

When done, tell the user explicitly: what you trimmed, what you appended, and which heading levels you shifted.

### Phase 5 — Scaffold the first entity

Use the example entity name from Phase 1 Q4. **The path depends on whether Phase 3 renamed anything**:

- If `investing` (default): use `wiki/entities/<NAME>/profile.md` and template `wiki/entities/_template/profile.md`
- If renamed: use `wiki/<new-folder>/<NAME>/profile.md` and template `wiki/<new-folder>/_template/profile.md`

Copy the template to the new location and fill in basic frontmatter (title, created date, domain). Leave the body sections empty. **Don't invent thesis content** — that's the user's job.

### Phase 6 — Verify and hand off

1. **Generate the index**: `python scripts/wiki_index.py` (no args). This produces `wiki/_index.json` and `wiki/overview.md`. **Without these, the wiki has no index and downstream lint/search commands won't work.** If python isn't available, tell the user to install it and run this command later.

2. **Cleanup**: `rm -rf .karpathy-tmp` (Phase 2 postponed this). PowerShell: `Remove-Item .\.karpathy-tmp -Recurse -Force`.

3. Show the user a tree of the new `wiki/` directory.

4. Confirm `CLAUDE.md` integration worked (cat the relevant section).

5. **Tell the user about the EXAMPLE placeholder files** (do NOT auto-delete — let them decide):
   > "The template ships with a few `EXAMPLE-*.md` and `EXAMPLE/` files that show what a real entry looks like. They're harmless (Claude recognizes them as placeholders and skips them on ingest), but if you want a fully clean slate, run:
   > ```bash
   > rm wiki/*/EXAMPLE-*.md 2>/dev/null; rm -rf wiki/*/EXAMPLE/ 2>/dev/null
   > ```
   > PowerShell:
   > ```powershell
   > Get-ChildItem .\wiki -Recurse -File -Filter 'EXAMPLE-*.md' | Remove-Item -Force
   > Get-ChildItem .\wiki -Recurse -Directory -Filter 'EXAMPLE' | Remove-Item -Recurse -Force
   > ```
   > Leaving them is also fine — purely personal preference."

6. Tell the user, verbatim:
   > "Wiki installed. To do your first ingest: drop a file into `wiki/raw/<category>/` where `<category>` is one of `articles`, `papers`, `books`, `podcasts`, `conversations`. Then say 'ingest this following the protocol'. The first ingest will refine the schema for your specific domain."

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
