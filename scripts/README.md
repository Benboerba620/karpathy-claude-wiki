# Scripts

维护这套 wiki 的辅助脚本说明。

## `install_wiki.ps1`

面向 Windows PowerShell 的一键安装器，适合新手用户。

它会：

- 复制 `wiki/`
- 清理模板中的生成文件和残留 raw 材料
- 复制 `scripts/wiki_index.py`
- 复制 `skills/wiki-ingest/`
- 可选复制 `scripts/ingest_helper.py` 和 `.env.example`
- 复制 `CLAUDE.md`，或在已有 `CLAUDE.md` 中追加轻量入口
- 写入 `wiki/_protocols.md`
- 创建第一个 entity 页面
- 生成 `_index.json` 与 `overview.md`
- 运行 `--lint`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_wiki.ps1 -TargetDir "D:\my-project" -EntityName "AAPL"
```

常用参数：

- `-Language zh-CN|en`：生成的 wiki 语言，默认 `zh-CN`
- `-Force`：目标目录已有 wiki 时强制覆盖
- `-WithIngestHelper`：额外复制 `scripts/ingest_helper.py` 和 `.env.example`

默认安装出的 wiki 使用平铺的 `wiki/raw/` inbox。

## `install_wiki.sh`

面向 macOS / Linux 的对应安装器，行为与 PowerShell 版本尽量保持一致。

```bash
bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL
```

常用参数：

- `--language zh-CN|en`
- `--force`
- `--skip-index`
- `--with-ingest-helper`

## `wiki_index.py`

索引生成、检索和 lint 检查三合一脚本。

```bash
# 默认：重建 _index.json + overview.md
python scripts/wiki_index.py

# 关键词搜索
python scripts/wiki_index.py --search "concept name"

# 结构健康检查
python scripts/wiki_index.py --lint

# 统计信息
python scripts/wiki_index.py --stats

# 生成 attention / link-graph 报告
python scripts/wiki_index.py --report
```

`--report` 会写出 `wiki/_attention.md`，突出显示：

- 高链接节点
- top-5 注意力集中度
- 扇出较高的 hub sources
- 零入链的新页面
- 被引用来源最多的 concepts

## `ingest_helper.py`（可选）

把 PDF / 长文本压缩成结构化 JSON，交给较便宜的 OpenAI 兼容 LLM 处理，节省主对话上下文。

适用场景：

- 长研报
- 长播客转录
- 几百页书稿或大文档

短文章、笔记、对话通常不需要这一层。

```bash
cp .env.example .env
pip install requests pypdf

python scripts/ingest_helper.py --pdf wiki/raw/my-report.pdf
python scripts/ingest_helper.py --pdf my.pdf --provider glm
python scripts/ingest_helper.py --text wiki/raw/notes.md
python scripts/ingest_helper.py --pdf my.pdf --out /tmp/summary.json
```

也可以作为 Python API：

```python
from scripts.ingest_helper import summarize_file
data = summarize_file("wiki/raw/my-report.pdf", provider="kimi")
```

## 后续可能补的脚本

1. `fix_broken_links.py`
2. `split_sources.py`
3. `promote_rules.py`
4. `verify_predictions.py`

这些都不是必需品，等真实痛点出现再加。
