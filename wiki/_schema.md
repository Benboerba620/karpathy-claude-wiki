---
title: Wiki Schema
type: meta
updated: 2026-04-18
---

# Wiki Schema

> 这是这套 wiki 的“宪法”。LLM 每次操作前都应先读它。你可以自由修改，最好交给 git 记录演化过程。

## 架构

```text
wiki/
├── _schema.md          # 本文件
├── _log.md             # 操作日志
├── _index.json         # 由 scripts/wiki_index.py 生成
├── overview.md         # 人类可读索引（同样为生成文件）
├── rules.md            # 已验证规则
├── false-beliefs.md    # 被证伪的常见认知
├── inbox-digest.md     # 最近摄入摘要
├── inbox-archive.md    # 较早的周摘要归档
├── raw/                # 不可变的原始材料；默认平铺 inbox
├── sources/            # 编译后的结构化摘要（每个来源一个文件）
├── entities/           # 你持续跟踪的对象（公司、人、书、项目等）
│   └── {NAME}/
│       ├── profile.md  # 主页面（判断、网络关系）
│       └── ...         # 当一个文件不够时再扩展子页面
├── concepts/           # 主题、框架、横向连接多个实体的想法
│   └── {THEME}.md      # 或 {THEME}/{THEME}.md
├── explorations/       # 固化后的研究问题答案（见 _template.md）
├── decisions/          # 决策日志（见 _template.md）
└── comparisons/        # 并排比较分析
```

## 页面类型

| type | 位置 | 适用场景 |
|---|---|---|
| `entity` | `entities/{NAME}/` | 需要长期跟踪的离散对象 |
| `tracker` | `entities/{NAME}/tracker.md` | 某个实体的追加式证据/催化跟踪 |
| `notes` | `entities/{NAME}/notes.md` | 某个实体的日期化研究笔记 |
| `concept` | `concepts/{NAME}.md` | 连接多个实体的主题或框架 |
| `source-summary` | `sources/` | 对单个外部来源的结构化摘要 |
| `exploration` | `explorations/` | 某个研究问题的固化答案 |
| `decision` | `decisions/` | 一次明确决策及其理由 |
| `comparison` | `comparisons/` | A vs B 并排比较 |
| `meta` | 根目录 | `_schema.md`、`rules.md`、`false-beliefs.md` 等 |

## Frontmatter 规范

除 `raw/` 外，每个 `.md` 页面都必须带 YAML frontmatter：

```yaml
---
title: <human-readable title>
type: entity | tracker | notes | concept | source-summary | exploration | decision | comparison | meta
domain: [investing | research | reading | writing | tech | life]
sources: [raw/filename]            # 仅 source-summary 使用
related: [[entity1]], [[concept1]]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: high | medium | low
---
```

`entity` 页面额外包含：

```yaml
aliases: [alt-name-1, alt-name-2]
tags: [tag1, tag2]
judgment: bullish | bearish | neutral | watching
```

## Wikilinks

使用双中括号：`[[entity-name]]`、`[[concept-name]]`。LLM 会利用它们做导航。**双向链接是强制的**：A 链到 B，B 也应回链到 A。

如果名称有歧义，可以写显式路径：`[[entities/AAPL/profile|Apple]]`。

## 五层结构：按变化速度组织

这套 wiki 最重要的设计原则是：

> **变化速度不同的东西，必须分层存放。**

| 层 | 变化频率 | 示例 |
|---|---|---|
| `raw/` | **几乎不变** | PDF、全文、转录稿 |
| `sources/` | **很少变** | 结构化来源摘要 |
| `entities/`、`concepts/` | **周到月级** | 档案页、主题页 |
| `explorations/`、`decisions/` | **按问题变化** | 固化答案、一次决策 |
| `rules.md`、`false-beliefs.md` | **季度级** | 长期经验总结 |

如果把这些层混在一起，快变量会淹没慢变量，最终失去可维护性。

## Ingest 规则

当用户给出一个新来源时：

1. 把原文放进 `raw/`（不可变归档；允许平铺）
2. 创建 `sources/<date>-<slug>.md`
3. 识别其中提到的实体与概念，更新对应页面；如果要新建，先征得用户同意
4. 维护双向 `[[wikilinks]]`
5. 追加一行到 `_log.md`
6. 更新 `inbox-digest.md` 当前周内容，需要时把旧周归档到 `inbox-archive.md`
7. 运行 `python scripts/wiki_index.py --lint`

完整细节见 `CLAUDE.md`。

## 可选外部 inbox

- Obsidian `Clippings` 可以作为用户显式开启的外部 inbox。
- 自动扫描命令：`python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings`
- 如果本机没有 Obsidian 或没有 `Clippings` 目录，直接忽略，不算错误。

## 可验证预测（可选但很有用）

当来源里出现具体、带日期、可证伪的预测时，在 source-summary 里加入：

```markdown
## Verifiable Predictions / 可验证预测

| Prediction | Target date | Status | Verified date | Result |
|---|---|---|---|---|
| <claim> | YYYY-MM | pending | | |
```

状态流转：`pending` → `confirmed` / `partially` / `denied`

- `confirmed` 累积 3 次以上：建议提升到 `rules.md`
- `denied` 且暴露偏差：建议加入 `false-beliefs.md`

## Concept synthesis（重编译）

每个 `concept` 页面应包含 `## Synthesis / 综述` 区块，总结它引用的所有来源：

```markdown
## Synthesis / 综述

> Compiled from N sources, last updated YYYY-MM-DD

(3-5 句当前最佳理解，并注明来源之间是否存在分歧)

**Key data points / 关键数据**:
| Metric | Latest value | Source |
|---|---|---|

**Sources cited / 引用来源**:
- [[sources/<file>]] - relevance
```

**触发重编译条件**：自上次编译以来，新增 3 个以上来源引用了该 concept。

## 领域定制

模板默认以 `investing` 为示例领域。如果你要改成其他领域，可以按下表做项目级 find-replace：

| Investing term | Research term | Reading term | Writing term |
|---|---|---|---|
| company | subject | author | reference |
| ticker | ID | ISBN | citekey |
| portfolio | reading list | shelf | bibliography |
| earnings | results | publication | release |
| catalyst | trigger | sequel | edition |

## 索引生成

运行 `python scripts/wiki_index.py` 以重建 `_index.json` 与 `overview.md`。常用附加参数：

- `--lint`：结构健康检查
- `--search "query"`：临时检索
- `--stats`：统计信息
- `--report`：重建 `_attention.md`

---

*这份 schema 是你与 LLM 之间的契约。可以自由修改，但建议提交到 git，以便你以后回看自己的知识结构如何演化。*
