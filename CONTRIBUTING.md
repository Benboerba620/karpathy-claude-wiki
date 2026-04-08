# Contributing / 贡献指南

[English](#english) ｜ [中文](#中文)

## English

Thanks for thinking about contributing — this project is small enough that almost any well-scoped PR is welcome.

### Quick rules

- **One PR = one concern.** Easier to review, easier to revert.
- **Keep it bilingual where it matters.** README, INSTALL-FOR-AI, and any doc on the user-facing path should have both Chinese and English. Code comments and internal scripts can be English only.
- **Don't add a vector DB / RAG layer.** This template is intentionally markdown-only. If you think a query case really needs embeddings, open a Discussion first.
- **Run wiki lint before pushing:**
  ```bash
  python scripts/wiki_index.py
  python scripts/wiki_index.py --report   # optional, regenerates wiki/_attention.md
  ```
  CI will run the same lint via `.github/workflows/wiki-lint.yml`.

### Testing the install scripts

If you change `scripts/install_wiki.ps1` or `scripts/install_wiki.sh`, **dry-run end-to-end into a brand-new empty folder** before opening the PR. Past bugs in the install scripts have all been "looked fine, broke on a clean machine".

### What's in scope

- Bug fixes in scripts / lint / install
- New AI-agent install paths (Cursor, Cline, Aider, etc.)
- Better defaults for `wiki/_schema.md` that don't lock users into a domain
- Documentation, examples, translations

### What's out of scope

- Domain-specific entity types (finance, biology, etc.) — keep those in your own fork
- Anything that requires running a server or external service
- Vector databases, embeddings, RAG pipelines

### Reporting bugs / asking questions

- **Bug** → open an Issue with the bug report template
- **"How do I..." / "Is it possible to..."** → open a [Discussion](https://github.com/Benboerba620/karpathy-claude-wiki/discussions), not an Issue

---

## 中文

感谢你愿意贡献 —— 这个项目很小，几乎任何边界清楚的 PR 都欢迎。

### 简单规则

- **一个 PR 只做一件事**，方便 review，方便回滚。
- **用户路径上的文档保持中英双语**。README、INSTALL-FOR-AI 这些必须双语；代码注释和内部脚本英文即可。
- **不要加向量数据库 / RAG 层**。这个模板就是要"只用 markdown"。如果你觉得某个查询场景真的需要 embedding，先开一个 Discussion 聊。
- **push 前先跑 lint**：
  ```bash
  python scripts/wiki_index.py
  python scripts/wiki_index.py --report   # 可选，重新生成 wiki/_attention.md
  ```
  CI 会在 `.github/workflows/wiki-lint.yml` 跑同一套 lint。

### 测试安装脚本

如果你动了 `scripts/install_wiki.ps1` 或 `scripts/install_wiki.sh`，**提 PR 前先在一个全新的空文件夹里端到端 dry-run 一次**。安装脚本以前出过的所有 bug 都是"本地看着没事，干净机器上炸"。

### 在范围内

- 脚本 / lint / 安装的 bug 修复
- 新的 AI agent 安装路径（Cursor、Cline、Aider 等）
- 让 `wiki/_schema.md` 的默认值更通用、不绑死某个领域
- 文档、示例、翻译

### 不在范围内

- 领域特定的 entity 类型（金融、生物等）—— 留在你自己的 fork 里
- 需要跑 server 或外部服务的东西
- 向量数据库、embedding、RAG pipeline

### 报 bug / 提问题

- **bug** → 开 Issue，用 bug report 模板
- **"我能不能…" / "怎么…"** → 开 [Discussion](https://github.com/Benboerba620/karpathy-claude-wiki/discussions)，不要开 Issue
