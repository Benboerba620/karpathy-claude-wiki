# 更新日志

这里记录 `karpathy-claude-wiki` 的重要更新。

## 2026-04-09

- 清理模板默认内容：移除 `EXAMPLE` 页面、`tracker.md` / `notes.md` 模板、`decisions/README.md` 以及默认提交的生成文件
- 对齐 Windows / macOS / Linux 安装器：两者都会写入 `wiki/_protocols.md`，已有 `CLAUDE.md` 时只追加轻量入口
- 修复安装器在检测到 Python 但不可运行时直接中断的问题，改为提示后继续安装
- 修复 bash 安装器的两个实际 bug：`wiki_root` 未绑定变量，以及协议提取对破折号字符过于脆弱
- 收紧 `scripts/wiki_index.py` 的排除规则，避免把 `_template.md` 和 `decisions/README.md` 当成真实内容；同时修复 `--report` 标题阈值显示
- 同步 README 与 AI 安装协议，明确生成文件是按需生成、没有 Python 时安装仍会完成

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

