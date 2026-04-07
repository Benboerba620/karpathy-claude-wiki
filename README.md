[中文](#中文) | [English](#karpathy-claude-wiki)

# 中文

> 一个个人 LLM 知识库模板,**灵感来自 [Andrej Karpathy 的推文](https://x.com/karpathy/status/2039805659525644595)**——用 LLM 来构建和维护个人 wiki。本模板针对 [Claude Code](https://claude.com/claude-code) 优化,但任何能读写文件的 AI agent 都可以使用。

**状态**:空模板。装上之后由用户填充内容。从那一刻起,LLM 替你完成所有的整理工作。

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

## 快速上手(人类版,5 分钟)

### 1. 克隆

```bash
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
cd karpathy-claude-wiki
```

### 2. 阅读 schema

```bash
cat wiki/_schema.md
```

这是 wiki 的"宪法"。AI 在每次操作前都会先读它。

### 3. 把 CLAUDE.md 移到你的项目根目录

```bash
# 如果已经有 CLAUDE.md,把内容追加进去,不要覆盖
cp CLAUDE.md ../my-project/CLAUDE.md
```

### 4. 把第一份原始材料丢进 raw/

```bash
cp ~/Downloads/some-research-paper.md wiki/raw/papers/
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

完成后删除 `.karpathy-tmp/`。

### 阶段 3 — 根据用户领域定制

打开 `wiki/_schema.md`,根据领域应用对应的修改:

| 领域 | 修改 |
|---|---|
| `investing` | 保持原样。`entities/` = 公司,`concepts/` = 主题/框架。 |
| `research` | 把 `entities/` 改名为 `subjects/`。简化 `rules.md`,只保留"已验证的模式"。 |
| `reading` | 把 `entities/` 改名为 `authors/`,`concepts/` 改名为 `themes/`。删掉 `decisions/`。 |
| `writing` | 把 `entities/` 改名为 `references/`,`concepts/` 改名为 `topics/`。删掉 `rules.md`。 |
| `mixed` | 保留 `entities/`,根据需要并列添加其他目录。 |

改名后,在 `_schema.md` 和 `CLAUDE.md` 里做一次全局搜索替换,修正所有引用。

### 阶段 4 — 整合 `CLAUDE.md`

- **如果用户已经有 `CLAUDE.md`**:把 `.karpathy-tmp/CLAUDE.md` 的内容追加到一个新章节 `## Wiki Protocols (from karpathy-claude-wiki)` 下面。告诉用户你追加了哪些内容。
- **如果用户没有 `CLAUDE.md`**:把 `.karpathy-tmp/CLAUDE.md` 复制到用户项目的根目录。

### 阶段 5 — 创建第一个 entity

使用阶段 1 第 4 题的示例 entity 名称,创建:

```
wiki/entities/<NAME>/profile.md
```

用 `wiki/entities/_template/profile.md` 作为模板。填好基础 frontmatter(title、type、created 日期),正文部分留空,等用户填。

### 阶段 6 — 验证并交付

1. 给用户展示新建的 `wiki/` 目录树。
2. 确认 `CLAUDE.md` 整合成功(打印出相关章节)。
3. 对用户说,原文如下:
   > "Wiki 安装完成。要做第一次 ingest:把一个文件放进 `wiki/raw/<category>/`,然后说"按协议摄入这个"。第一次 ingest 会根据你的具体领域优化 schema。"

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
---

[中文](#中文) | [English](#karpathy-claude-wiki)

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
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git
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
git clone https://github.com/Benboerba620/karpathy-claude-wiki.git .karpathy-tmp
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
