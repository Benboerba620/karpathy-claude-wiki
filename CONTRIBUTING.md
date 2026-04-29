# 贡献指南

感谢你愿意贡献 —— 这个项目很小，几乎任何边界清楚的 PR 都欢迎。

## 简单规则

- **一个 PR 只做一件事**，方便 review，方便回滚。
- **面向用户的文档用中文**。README、INSTALL-FOR-AI 等用户会读到的文档请用中文；代码注释和内部脚本英文即可。
- **不要加向量数据库 / RAG 层**。这个模板就是要"只用 markdown"。如果你觉得某个查询场景真的需要 embedding，先开一个 Discussion 聊。
- **push 前先跑 lint**：
  ```bash
  python scripts/wiki_index.py
  python scripts/wiki_index.py --report   # 可选，重新生成 wiki/_attention.md
  python scripts/preflight_public_repo.py
  ```
  CI 会在 `.github/workflows/wiki-lint.yml` 跑同一套 lint 和公开前安全检查。`preflight_public_repo.py` 会拦截 API key、本机路径、同步盘冲突文件和 `wiki/raw/` 原始材料误提交。

## 测试安装脚本

如果你动了 `scripts/install_wiki.ps1` 或 `scripts/install_wiki.sh`，**提 PR 前先在一个全新的空文件夹里端到端 dry-run 一次**。安装脚本以前出过的所有 bug 都是"本地看着没事，干净机器上炸"。

## 在范围内

- 脚本 / lint / 安装的 bug 修复
- 新的 AI agent 安装路径（Cursor、Cline、Aider 等）
- 让 `wiki/_schema.md` 的默认值更通用、不绑死某个领域
- 文档、示例、翻译

## 不在范围内

- 领域特定的 entity 类型（金融、生物等）—— 留在你自己的 fork 里
- 需要跑 server 或外部服务的东西
- 向量数据库、embedding、RAG pipeline

## 报 bug / 提问题

- **bug** → 开 Issue，用 bug report 模板
- **"我能不能…" / "怎么…"** → 开 [Discussion](https://github.com/Benboerba620/karpathy-claude-wiki/discussions)，不要开 Issue
