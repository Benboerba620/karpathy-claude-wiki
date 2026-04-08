# 更新日志

这里记录 `karpathy-claude-wiki` 的重要更新。

## 2026-04-08

- 修复已有 `CLAUDE.md` 项目在安装后被整段 wiki 协议撑长的问题
- 安装器现在会把完整协议写入 `wiki/_protocols.md`，已有项目只追加轻量入口
- `scripts/wiki_index.py --lint` 现在默认忽略 `wiki/_protocols.md`，避免协议示例造成误报
- 新增适合 Windows 小白用户的一键安装脚本 `scripts/install_wiki.ps1`
- 优化 `README` 首页导流，更适合中文新用户和第一次访问者
- 新增 GitHub Actions 工作流，自动运行 `Wiki Lint`
- 加强 `scripts/wiki_index.py`：支持 BOM frontmatter、更稳的链接解析、以及新建页面的 orphan 缓冲逻辑
- 新增 `python scripts/wiki_index.py --report`，支持注意力 / 链接结构报告
- 新增生成文件 `wiki/_attention.md`

## 2026-04-07

- 新增中文 README 和中英文切换入口
- 改进 AI 安装协议，补充 EXAMPLE 占位文件清理说明
- 发布 Karpathy 风格的空 wiki 模板结构

