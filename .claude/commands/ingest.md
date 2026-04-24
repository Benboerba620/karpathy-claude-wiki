---
description: 按 wiki 协议摄入来源。可用 `/ingest` 自动处理 `wiki/raw/` 候选，或 `/ingest <path>` 指定文件。
argument-hint: [path-or-note]
disable-model-invocation: true
---

执行这个仓库的 wiki ingest 流程。

先做这些准备：

1. 先读 `wiki/_schema.md`、`wiki/_protocols.md` 和 `CLAUDE.md`，不要跳过。
2. 把 `wiki/raw/` 视为不可变 inbox。用户已经放进去的文件不要修改原文。
3. 如果用户明确要求扫描外部 inbox（例如 Obsidian `Clippings`），先运行：
   `python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings`

处理输入参数时按这个规则：

1. 如果传了参数 `$ARGUMENTS`：
   把它当成“要 ingest 的文件路径”或“要 ingest 的候选说明”来解析。
2. 如果没有传参数：
   检查 `wiki/raw/` 下的待处理文件，忽略 `.gitkeep`。
3. 如果待处理文件是 0 个：
   明确告诉用户当前没有可 ingest 的来源。
4. 如果待处理文件是 1 个：
   直接 ingest 它。
5. 如果待处理文件大于 1 个：
   先简短列出候选，让用户确认要 ingest 哪个，不要擅自批量处理。

执行 ingest 时：

1. 如果仓库里有 `scripts/wiki_cli.py`，优先用它完成归档、`sources/` 页面、`_log.md`、`inbox-digest.md` 和 index/lint 的样板流程。
2. 如果来源是大 PDF / 长文档，且仓库里有 `scripts/ingest_helper.py`，可以在合适时先用 helper 生成结构化 JSON，再继续 ingest。
3. 无论是否用了脚本，最终结果都要对齐 `wiki/_protocols.md` 的协议格式，而不是只停留在脚本默认输出。
4. 更新已存在的 entity / concept 页面；如果需要新建 entity / concept，先征得用户同意。
5. 维护双向 `[[wikilinks]]`。
6. 完成后确认 `wiki/_log.md` 和 `wiki/inbox-digest.md` 已更新。
7. 如果你没有通过 `scripts/wiki_cli.py` 自动跑 lint，就手动运行：
   `python scripts/wiki_index.py --lint`

最后给用户一个简短结果：

- ingest 了哪个 raw 文件
- 生成了哪个 `wiki/sources/...md`
- 更新了哪些 entity / concept 页面
- 如果还有待确认项，明确指出
