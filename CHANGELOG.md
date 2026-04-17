# 更新日志

这里记录 `karpathy-claude-wiki` 的重要更新。

## 2026-04-17

### README 结构重排：AI agent 路径升为首推

- 路由表改为：🤖 Claude Code / AI agent 帮你装（推荐）→ 📄 大文件 ingest helper（可选但强推）→ 🧑‍💻 本地脚本（折叠进阶）→ 🛠️ 手动安装（折叠进阶）
- 之所以这样改：对真小白来说，"打开终端 + 翻文档找命令 + 复制粘贴 + 改路径参数"的门槛比"给 Claude Code 发一句 URL"高得多；AI agent 路径又是近乎零操作
- 「让 AI agent 帮你装」章节扩写为 3 步流程 + 明确列出 agent 会问的 4 个澄清问题，小白能提前预期
- 「大文件 ingest helper」章节提前到 AI agent 安装之后，并加强提示（研报/长文稿/书的场景必读）
- Windows PowerShell 一键安装、macOS/Linux bash 一键安装两节合并为一个可折叠的「进阶：本地脚本安装」
- 手动安装改为可折叠的「进阶：手动安装（5 分钟）」
- 中英双语同步
- 路由表第 1 行补 Cursor / Cline / Windsurf 的替代选项链接，避免"没有 Claude Code 就用不了"的错觉

### 新增 scripts/ingest_helper.py + .env.example

- 新增可选脚本 `scripts/ingest_helper.py`（~280 行，中文 docstring）：把 PDF / 长文本压缩这一步外包给便宜的 OpenAI 兼容 LLM，返回结构化 JSON，主 Claude / Cursor agent 再快速生成 `sources/` 页面
- 支持 5 家 OpenAI 兼容 provider：**Kimi / 月之暗面**、**智谱 GLM**（`glm-4-flash` 截至 2026-01 免费）、**DeepSeek**、**通义 Qwen**、**OpenAI**（或任何 OpenAI 兼容端点）—— 前四家在国内都有免费额度
- 自动探测环境变量里配了哪家就用哪家，不用改代码切 provider
- 内置轻量 `.env` 加载器，不依赖 `python-dotenv`
- Windows 控制台 UTF-8 自动重配置，中文 help / JSON 输出不乱码
- 支持 `.pdf` / `.md` / `.txt` 输入；PDF 需要 `pypdf`，其他零外部依赖（除 `requests`）
- CLI + Python API 双入口；JSON 输出字段正好对齐 ingest 协议里 `sources/<日期>-<slug>.md` 的 schema
- `.env.example` 包含五家 provider 的配置模板和注册入口，中文注释
- `INSTALL-FOR-AI.md` 阶段 2 尾部新增可选步骤：只在用户明确表示要 ingest 大 PDF 时才复制这两个文件
- `scripts/README.md` 新增 `ingest_helper.py` 章节（中文）
- 不装也不影响默认 ingest 流程，纯粹是给大文件场景兜底

## 2026-04-12

- 新增 `wiki/explorations/_template.md`：完整的 exploration 模板，包含假设分支、不确定性、数据缺口、行动触发条件
- 新增 `wiki/decisions/_template.md`：完整的 decision 模板，包含备选方案对比、反转条件、Outcome 回顾区、Lessons → Rules 闭环
- 增强 `wiki/rules.md`：新增 Rule Lifecycle 段落，写清 `observation → pattern → RULE → under review → retired` 完整路径，Promotion Log 记录所有生命周期事件
- 升级 `wiki/inbox-digest.md`：从平铺表格改为按周分组，60 天滚动归档到 `inbox-archive.md`
- 新增 `wiki/inbox-archive.md`：digest 归档文件
- 新增 `wiki/sources/EXAMPLE-source-summary.md`：source-summary 示例页面
- 扩展所有 EXAMPLE 文件（entity/concept/exploration）为完整带注释的示例
- `CLAUDE.md` Protocol 1 新增 Step 5（更新 inbox digest），Protocol 4 改为引用模板文件
- `wiki/_schema.md` 补充 `tracker` 和 `notes` 为独立 page type，exploration/decision 指向模板
- `scripts/wiki_index.py` 重构排除逻辑：`SCAFFOLD_SKIP_PATTERNS` 统一处理模板和示例文件
- 安装脚本 Python 检测加强：`py -3` → `python` → `python3` 顺序尝试
- CI: GitHub Actions 升级到 v6

## 2026-04-09

- 修复 PowerShell 安装器：Windows Store 的 `python.exe` 别名现在被识别为"Python 不可用"，而非真正的解释器
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
