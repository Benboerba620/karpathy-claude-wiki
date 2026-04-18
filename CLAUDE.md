# CLAUDE.md - Wiki Protocols

> 这个文件定义了让个人 wiki “活起来”的四个核心协议。把它放在项目根目录，或把其中内容合并进你现有的 `CLAUDE.md`。Claude Code 会自动读取它。

如果你是第一次读到它的人类：把它看作 Claude 与 `wiki/` 交互时遵守的契约。理解一次就够了，后续由 Claude 执行。

如果你是 AI agent：**这些协议不可协商**。每次处理 wiki 时都要遵守。如果协议与用户指令冲突，先指出冲突，再行动。

---

## 语言 / Language

**默认语言：中文（简体）。**

- 与用户的对话、进度更新、报错说明默认使用中文。
- 所有新建或修改的 wiki 文件正文、标题、字段说明默认使用中文。
- 公司名、ticker、产品名、技术术语等专有名词保留原文。
- 原始引文保留原语言，不强制翻译。
- 如果用户明确要求英文输出或安装英文模板，以用户指令为准。

---

## Protocol 1 - Ingest

**Trigger**: 用户把文件放进 `wiki/raw/` 并说“ingest this”，或粘贴内容并要求“ingest this into the wiki”，或明确要求扫描可选外部 inbox（如 Obsidian `Clippings`）。

**辅助 skill**: 如果运行环境支持 repo-local skills，优先使用 `skills/wiki-ingest/SKILL.md` 作为执行指南。

**Steps**:

1. **归档原始材料**。把 `wiki/raw/` 视为默认的不可变 inbox。用户如果已经把文件放在这里，就不要再移动；如果来源是粘贴内容或外部 inbox，先复制到 `wiki/raw/`。一旦进入 `raw/`，**永不修改**。

2. **可选外部扫描**。如果用户明确要求，可运行 `python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings` 扫描 Obsidian `Clippings`。如果未安装 Obsidian 或未找到 `Clippings`，静默跳过，继续处理 `wiki/raw/`。

3. **编译为 source-summary**。创建 `wiki/sources/<YYYY-MM-DD>-<slug>.md`，结构如下：

   ```markdown
   ---
   title: <一行标题>
   type: source-summary
   domain: <用户领域，例如 investing/research/reading>
   sources: [raw/<filename>]
   related: [[entity1]], [[concept1]]
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   confidence: high | medium | low
   ---

   ## TL;DR / 一句话摘要
   一句话。

   ## Key Data / 关键数据
   记录硬数据的表格。

   ## Direct Quotes / 原始引文
   保留原文并标明出处。

   ## Implications / 启示
   这份材料对现有实体/概念意味着什么。

   ## Verifiable Predictions / 可验证预测
   仅当材料中出现具体、带日期、可证伪的判断时填写。
   ```

4. **提取实体与概念**。识别材料中提到的所有实体和概念：
   - 如果它已存在于 `wiki/entities/` 或 `wiki/concepts/`：更新对应页面（通常是 `profile.md`，以及用户确实在使用的可选子页面），并用 `[[wikilinks]]` 回链到新来源。
   - 如果它不存在：先问用户，**不要自动创建**。知识库的策展权属于用户。

5. **追加到日志**。在 `wiki/_log.md` 新增一行：

   ```
   | YYYY-MM-DD HH:MM | ingest | raw/<file> | sources/<file> + N updates | <一句话备注> |
   ```

6. **更新 inbox digest**。在 `wiki/inbox-digest.md` 当前周的表格里新增一行：

   ```
   | <来源/作者> | <标题> | <主要归档对象> | <一句话收获> |
   ```

   如果当周区块不存在，就创建它。如果文件累计超过约 60 天内容，把更老的周区块移到 `wiki/inbox-archive.md`。

7. **向用户汇报**。格式为：`已摄入到 sources/<file>。更新了 <entity1>、<concept1>。新增 N 个交叉引用。发现 N 处潜在矛盾。`

---

## Protocol 2 - Cross-Reference

**Trigger**: 任何时候更新 `entity` 或 `concept` 页面。

**Steps**:

1. **扫描相关页面**。读取当前页面 frontmatter 里的 `related:`。对每个关联项，打开对应页面，检查是否需要 reciprocal update。

2. **维护双向链接**。如果你在页面 A 的 `related:` 里加入 `[[B]]`，确保页面 B 的 `related:` 里也包含 `[[A]]`。

3. **识别孤儿页**。如果更新后某页既没有入链也没有出链，要提醒用户。通常这意味着一个尚未长成的半成品想法。

4. **更新“关联网络 / Network”章节**。每个实体页都应该有连接到其他实体与概念的网络区块，链接变化时同步更新。

---

## Protocol 3 - Contradiction Scan

**Trigger**: 任何时候准备把新的判断、主张或证据写进 wiki。

**Steps**:

1. **检查 `false-beliefs.md`**。新判断是否与其中条目冲突？如果是，暂停并先提示用户。

2. **检查 `rules.md`**。新判断是否违反现行规则？如果是，同样先提示再写入。

3. **检查相关页面**。如果新判断与实体 X 有关，扫描 X 的现有页面（至少 `profile.md`，以及用户在用的其他子页），查找历史判断是否矛盾。

4. **按固定模板提示**：

   ```
   ⚠️ Possible contradiction:
   - New evidence: <你准备写入的新证据>
   - Existing belief: <wiki 里的既有观点，附文件路径>
   - Suggested resolution: <update old | qualify new | mark as exception>
   ```

目的不是阻止矛盾出现，而是让矛盾显性化，方便用户有意识地决定如何处理。

---

## Protocol 4 - Crystallization

**Trigger**: 你刚刚用 2 个以上来源回答了一个研究问题，而且答案具有可复用价值，不只是一次性查找。

**Steps**:

1. **先询问是否保存**。对用户说：`这个答案综合了 [[source1]]、[[source2]]、[[source3]]。要不要我把它保存成 exploration 页面，方便以后引用？`

2. **如果用户同意**，使用 `wiki/explorations/_template.md` 创建 `wiki/explorations/<YYYY-MM>-<slug>.md`。模板包含触发事件、假设分支、不确定性、数据缺口、行动节点和开放问题。按问题复杂度取舍，不必机械填满。

3. **控制频率**。每次对话最多主动提出两次 crystallization 建议。

4. **后续复用**。用户以后问到类似问题时，优先检查 `explorations/`，命中就直接引用，不必重新综合。

---

## 定期维护（按周或按需执行）

### Lint

运行 `python scripts/wiki_index.py --lint`，检查：

- 失效的 `[[wikilinks]]`
- 没有入链或出链的孤儿页
- 缺失必要 frontmatter 的页面
- 超过 90 天仍标记为 `confidence: high` 的陈旧页面

### 重新编译 concepts

当某个 `concept` 页面自上次编译后新增了 3 个以上来源时，重写其 `## Synthesis / 综述` 区块。

### 提升 rules

扫描实体页中被重复验证 3 次以上的模式，建议提升到 `rules.md`。遵守 `rules.md` 中的 Rule Lifecycle：提升、复核、退役、更新都需要写入 Promotion Log。

### 验证 predictions

扫描 `sources/*.md` 中 `## Verifiable Predictions / 可验证预测` 表格里已到期的预测：

- 如果确认成立：增加证据计数，必要时建议提升到 `rules.md`
- 如果被证伪：如果它暴露了认知偏差，建议写入 `false-beliefs.md`

---

## 风格约束

- **保持简洁**。wiki 主要是给 LLM 读的，冗长会浪费上下文。
- **严格使用 frontmatter**。缺 frontmatter 的页面等于不可发现。
- **优先 wikilinks**。尽量写 `[[entity]]`，不要只写纯文本名称。
- **实体页和概念页不要加 emoji**。风格不统一，也不利于检索。
- **所有内容都要带日期**。`created:` 与 `updated:` 是强制字段。

---

## 冲突处理

如果用户指令与这些协议冲突：

1. 先明确指出冲突：`你的指令要求我做 X，但 Protocol N 要求我做 Y。`
2. 再问用户以哪条规则为准。
3. 如果用户覆盖了协议，再问一次是否要顺手更新本文件，让新规则永久化。

---

*这是一个通用协议文件。你可以按自己的领域改写、删减或扩展。建议把变更提交到 git，方便追踪知识架构如何演化。*
