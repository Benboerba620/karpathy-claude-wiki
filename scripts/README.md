# Scripts

Helper scripts for maintaining the wiki. Currently:
## `install_wiki.ps1`

A beginner-friendly Windows PowerShell installer for Chinese / non-technical users.

It can:
- copy `wiki/` into a target project
- strip generated files / raw-material leftovers from the copied template
- copy `scripts/wiki_index.py`
- optionally copy `scripts/ingest_helper.py` + `.env.example`
- copy `CLAUDE.md` or add a lightweight entry when one already exists
- write `wiki/_protocols.md` and scaffold the first entity page
- generate `_index.json` + `overview.md`
- run `--lint`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"
```

Use `-Force` if the target `wiki/` already exists and you explicitly want to overwrite it.
Use `-WithIngestHelper` if you also want `scripts/ingest_helper.py` and `.env.example`.
On Windows, the installer ignores the Microsoft Store `python.exe` alias and only runs index/lint when a real Python 3 interpreter is available.

## `wiki_index.py`

A combined index generator, search tool, and lint checker.

```bash
# Default: regenerate _index.json + overview.md
python scripts/wiki_index.py

# Search by keyword across all pages
python scripts/wiki_index.py --search "concept name"

# Run health check (broken links, orphans, stale pages, missing frontmatter)
python scripts/wiki_index.py --lint

# Quick stats by type and domain
python scripts/wiki_index.py --stats

# Generate attention / link-graph report
python scripts/wiki_index.py --report
```

`--report` generates a structural attention summary and writes `wiki/_attention.md`.
It highlights:
- god nodes (most-linked pages)
- top-5 attention concentration
- hub sources with high fan-out
- lonely recent pages with zero inbound links
- concepts ranked by source-reference count

This is a minimal version (~200 lines). The original it was distilled from is ~700 lines and has domain-specific extensions for larger wiki structures. Customize freely.

## `ingest_helper.py`（可选 —— 大文件 ingest 外接 LLM 助手）

把 PDF / 长文本压缩这一步外包给一个便宜的 OpenAI 兼容 LLM，省主对话 context。只在 ingest 大研报、长播客、几百页的书时才需要；短文章让主 agent 直接读即可，不要装这个。

支持的 provider（任选一家，前四家在国内有免费额度）：

- **Kimi / 月之暗面**（`https://platform.moonshot.cn/`）—— 长文本友好
- **智谱 GLM**（`https://bigmodel.cn/`）—— `glm-4-flash` 免费
- **DeepSeek**（`https://platform.deepseek.com/`）—— 送免费 credits
- **通义 Qwen**（`https://dashscope.console.aliyun.com/`）—— 阿里 DashScope
- **OpenAI**（或任何 OpenAI 兼容端点）

三步配好：

```bash
# 1. 复制 .env 模板
cp .env.example .env
# 2. 编辑 .env，在其中一家 provider 下取消注释并填 key
# 3. 装依赖
pip install requests pypdf
```

用法：

```bash
# 读 PDF，JSON 打 stdout
python scripts/ingest_helper.py --pdf wiki/raw/articles/my-report.pdf

# 显式指定 provider
python scripts/ingest_helper.py --pdf my.pdf --provider glm

# 读 md / txt
python scripts/ingest_helper.py --text wiki/raw/articles/notes.md

# 写 JSON 到文件
python scripts/ingest_helper.py --pdf my.pdf --out /tmp/summary.json
```

JSON 字段：`title / date / author / tldr / key_data / quotes / implications / entities_mentioned / concepts_mentioned / verifiable_predictions / open_questions` —— 正好对齐 ingest 协议里 `sources/<日期>-<slug>.md` 的字段结构。

也可以作为 Python API 被 AI agent 直接调用：

```python
from scripts.ingest_helper import summarize_file
data = summarize_file("wiki/raw/articles/my-report.pdf", provider="kimi")
```

**边界**：
- ✅ 适合：结构化压缩已知文档（研报、文章、播客稿）
- ❌ 不适合：跨多个文档的综合判断、投资决策依赖的精确数字归属（主 agent 亲自读）
- 国产 LLM 在数字密集 / infographic 提取上偶有硬幻觉，关键财务数据出 JSON 后主 agent 建议再核一遍原文

## What you might add later

Common additions, in order of usefulness:

1. **`fix_broken_links.py`** — auto-repair common wikilink format issues (display text vs path)
2. **`split_sources.py`** — split a long accumulated source file into individual `sources/*.md` pages
3. **`promote_rules.py`** — scan entity pages for repeated confirmation patterns, suggest rule promotions
4. **`verify_predictions.py`** — for predictions whose target date has passed, ask the LLM to verify and update

None of these are essential. Build them when the pain shows up.

## Dependencies

The minimal script uses only the Python standard library. No `pip install` required.

If you want fancier YAML parsing (multi-line values, nested dicts), add `pyyaml` and replace `parse_frontmatter()`.
