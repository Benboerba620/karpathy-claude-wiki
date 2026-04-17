#!/usr/bin/env python3
"""ingest_helper.py —— 可选的 PDF / 长文本压缩助手（karpathy-claude-wiki 配套）

背景
----
`CLAUDE.md` 里的 ingest 协议假设 AI agent 能直接读一份原始资料、把它压缩成
`sources/<日期>-<slug>.md` 摘要页面。对小文件（一篇文章、一条笔记）来说，
Claude / Cursor / Cline 直接读就行，不需要这个脚本。

但遇到**大文件**（几十页的卖方研报、长播客文稿、几百页的书）时，把整个
文件塞进主对话会狂烧 context。这个 helper 把"压缩"这一步外包给你选的一个
OpenAI 兼容 LLM，返回结构化 JSON，再由 agent 快速生成 `sources/` 页面。

支持的 provider（都用 OpenAI 兼容 /v1/chat/completions 接口）：
    kimi       月之暗面 Kimi —— 长文本友好，国内注册方便
    glm        智谱 GLM —— glm-4-flash 一般有免费额度
    deepseek   DeepSeek —— 新用户送免费 credits
    qwen       阿里通义千问 (DashScope 兼容模式) —— 国内大厂方案
    openai     OpenAI 官方 / 或者任何 OpenAI 兼容端点（改 base_url 即可）

配置方式：把 API key 写到项目根目录的 `.env` 文件里（或者直接 export 到
环境变量）。具体变量名见 `.env.example`。

使用方式
--------

    # CLI —— 读一个 PDF，把 JSON 摘要打到 stdout
    python scripts/ingest_helper.py --pdf wiki/raw/articles/my-report.pdf

    # CLI —— 明确指定 provider
    python scripts/ingest_helper.py --pdf my.pdf --provider glm

    # CLI —— 读普通 md / txt 文件
    python scripts/ingest_helper.py --text wiki/raw/articles/my-article.md

    # Python API —— AI agent 直接调
    from scripts.ingest_helper import summarize_file
    data = summarize_file("wiki/raw/articles/my-report.pdf", provider="kimi")
    # data 是 dict，包含 title / date / tldr / key_data / quotes / ...

依赖
----
    - Python 3.8+
    - requests（通常已预装；没装的话：pip install requests）
    - pypdf（仅读 PDF 时需要；pip install pypdf）

如果一个 API key 都没配，脚本会优雅退出并提示去看 .env.example。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Windows 控制台默认 cp936 会把中文输出显示成乱码；Python 3.7+ 可以强制 UTF-8。
# 新终端（Windows Terminal / VS Code / Git Bash）能正确渲染；老 cmd.exe 仍可能
# 有问题，但写入文件 (--out) 永远是 UTF-8 干净的。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

try:
    import requests
except ImportError:  # pragma: no cover
    sys.stderr.write("错误：未安装 requests 库。请运行：pip install requests\n")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Provider 配置表
# ─────────────────────────────────────────────────────────────────────────────
# 每家 provider 都暴露 OpenAI 兼容的 /v1/chat/completions 接口。
# 端点和模型名称可能会随 provider 官方政策调整，部署前请核对一次官网文档。
PROVIDERS = {
    "kimi": {
        "env_key": "KIMI_API_KEY",
        "env_key_alt": "MOONSHOT_API_KEY",  # 兼容官方变量名
        "base_url_env": "KIMI_BASE_URL",
        "base_url_default": "https://api.moonshot.cn/v1",
        "model_env": "KIMI_MODEL",
        "model_default": "moonshot-v1-32k",  # 长文本专用变体
        "docs": "https://platform.moonshot.cn/docs",
    },
    "glm": {
        "env_key": "GLM_API_KEY",
        "env_key_alt": "ZHIPUAI_API_KEY",
        "base_url_env": "GLM_BASE_URL",
        "base_url_default": "https://open.bigmodel.cn/api/paas/v4",
        "model_env": "GLM_MODEL",
        "model_default": "glm-4-flash",  # 截至 2026-01 免费
        "docs": "https://bigmodel.cn/dev/api",
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "env_key_alt": None,
        "base_url_env": "DEEPSEEK_BASE_URL",
        "base_url_default": "https://api.deepseek.com/v1",
        "model_env": "DEEPSEEK_MODEL",
        "model_default": "deepseek-chat",
        "docs": "https://api-docs.deepseek.com",
    },
    "qwen": {
        "env_key": "DASHSCOPE_API_KEY",
        "env_key_alt": "QWEN_API_KEY",
        "base_url_env": "QWEN_BASE_URL",
        "base_url_default": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_env": "QWEN_MODEL",
        "model_default": "qwen-plus",
        "docs": "https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "env_key_alt": None,
        "base_url_env": "OPENAI_BASE_URL",
        "base_url_default": "https://api.openai.com/v1",
        "model_env": "OPENAI_MODEL",
        "model_default": "gpt-4o-mini",
        "docs": "https://platform.openai.com/docs",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# .env 加载器（不依赖 python-dotenv）
# ─────────────────────────────────────────────────────────────────────────────
def _load_dotenv(path: Path) -> None:
    """把一个 .env 文件读进环境变量。不覆盖已有变量。"""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def _autoload_env() -> None:
    """在 CWD 和脚本所在项目根目录查找 .env，依次加载。"""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for c in candidates:
        _load_dotenv(c)


# ─────────────────────────────────────────────────────────────────────────────
# Provider 选择逻辑
# ─────────────────────────────────────────────────────────────────────────────
def _resolve_provider(explicit: Optional[str] = None) -> tuple[str, dict, str]:
    """挑一个可用的 provider，返回 (名称, 配置, API key)。

    - 如果 explicit 有值：用这个，如果没 key 就直接报错
    - 否则按优先级自动探测（kimi → glm → deepseek → qwen → openai）
    """
    order = ["kimi", "glm", "deepseek", "qwen", "openai"]
    tried = [explicit] if explicit else order
    for name in tried:
        if name not in PROVIDERS:
            raise ValueError(f"未知 provider：{name}。可选：{list(PROVIDERS)}")
        cfg = PROVIDERS[name]
        key = os.environ.get(cfg["env_key"])
        if not key and cfg.get("env_key_alt"):
            key = os.environ.get(cfg["env_key_alt"])
        if key:
            return name, cfg, key
    raise RuntimeError(
        "没找到任何 provider 的 API key。"
        "请在 .env 或环境变量里至少配一个。参考 .env.example。"
        f"尝试过：{', '.join(tried)}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 文件读取
# ─────────────────────────────────────────────────────────────────────────────
def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        sys.stderr.write(
            "错误：读取 PDF 需要 pypdf 库。请运行：pip install pypdf\n"
            "（或者先把 PDF 转成 .md/.txt 再传进来。）\n"
        )
        sys.exit(1)
    reader = PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages, 1):
        try:
            parts.append(f"\n\n--- 第 {i} 页 ---\n{page.extract_text() or ''}")
        except Exception as e:  # pragma: no cover
            parts.append(f"\n\n--- 第 {i} 页（提取失败：{e}）---\n")
    return "".join(parts)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_input(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return _read_text(path)


# ─────────────────────────────────────────────────────────────────────────────
# Prompt 模板
# ─────────────────────────────────────────────────────────────────────────────
SUMMARY_SYSTEM = (
    "你是一位资深研究分析师，负责把研报、文章、长文档压缩成结构化 JSON。"
    "只输出 JSON —— 不要加任何解释文字，不要包 markdown 代码块。"
    "不确定的字段用 null，不要编造数字。关键数据和金句必须来自原文。"
)

SUMMARY_USER_TEMPLATE = """请从下方文档中提取结构化 JSON 摘要。
严格按以下 schema 返回（字段名保留、未知值用 null）：

{{
  "title": "简短标题",
  "date": "YYYY-MM-DD 或 null",
  "author": "作者 / 机构 或 null",
  "tldr": "一句话核心结论",
  "key_data": [
    {{"metric": "指标名", "value": "值", "period": "期间", "note": "可选备注"}}
  ],
  "quotes": ["原文金句 1", "原文金句 2"],
  "implications": "这份资料对跟踪该话题的人意味着什么（2-3 句）",
  "entities_mentioned": ["实体 1（公司/人物/产品）", "实体 2"],
  "concepts_mentioned": ["概念 1（主题/框架）", "概念 2"],
  "verifiable_predictions": [
    {{"claim": "具体可证伪的预测", "target_date": "YYYY-MM", "status": "pending"}}
  ],
  "open_questions": ["未解决问题 1", "未解决问题 2"]
}}

文档全文：
----
{content}
----
"""


# ─────────────────────────────────────────────────────────────────────────────
# LLM 调用
# ─────────────────────────────────────────────────────────────────────────────
def _call_llm(
    provider: str,
    cfg: dict,
    api_key: str,
    system: str,
    user: str,
    max_tokens: int = 4000,
    timeout: int = 300,
) -> str:
    base_url = os.environ.get(cfg["base_url_env"], cfg["base_url_default"]).rstrip("/")
    model = os.environ.get(cfg["model_env"], cfg["model_default"])
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    sys.stderr.write(f"[ingest_helper] 调用 {provider}（{model}）→ {base_url}\n")
    r = requests.post(url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _parse_json_loose(text: str) -> dict:
    """有些 LLM 会把 JSON 包在 ```json ... ``` 里，剥一下壳。"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[: -len("```")]
        text = text.strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


# ─────────────────────────────────────────────────────────────────────────────
# 对外 API
# ─────────────────────────────────────────────────────────────────────────────
def summarize_file(
    path: str | Path,
    provider: Optional[str] = None,
    max_chars: int = 200_000,
    max_tokens: int = 4000,
) -> dict:
    """读一个文件，调 LLM 压缩，返回结构化 dict。

    参数：
        path       —— 要压缩的文件路径（.pdf / .md / .txt）
        provider   —— kimi/glm/deepseek/qwen/openai 之一；None 时自动探测
        max_chars  —— 超过这个长度就截尾（粗暴截断，重要内容请先分片）
        max_tokens —— LLM 输出上限

    返回：
        dict，包含 title / date / author / tldr / key_data / quotes /
        implications / entities_mentioned / concepts_mentioned /
        verifiable_predictions / open_questions
    """
    _autoload_env()
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    name, cfg, key = _resolve_provider(provider)
    content = _read_input(path)
    if len(content) > max_chars:
        sys.stderr.write(
            f"[ingest_helper] 内容长度 {len(content)} 超过 {max_chars}，尾部已截断。"
            "如果关键信息在结尾，请先手动分片。\n"
        )
        content = content[:max_chars]

    user_prompt = SUMMARY_USER_TEMPLATE.format(content=content)
    raw = _call_llm(name, cfg, key, SUMMARY_SYSTEM, user_prompt, max_tokens=max_tokens)
    try:
        return _parse_json_loose(raw)
    except json.JSONDecodeError as e:
        sys.stderr.write(
            f"[ingest_helper] LLM 返回的不是合法 JSON。前 500 字：\n{raw[:500]}\n"
        )
        raise RuntimeError(f"LLM 输出非 JSON：{e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="用 OpenAI 兼容 LLM 把长文档压缩成结构化 JSON 摘要。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="支持的 provider：" + ", ".join(PROVIDERS),
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pdf", help="PDF 文件路径")
    g.add_argument("--text", help="md / txt 文件路径")
    ap.add_argument(
        "--provider",
        choices=list(PROVIDERS),
        help="显式指定 provider（默认按环境变量自动探测）",
    )
    ap.add_argument(
        "--max-chars",
        type=int,
        default=200_000,
        help="输入截断长度（超过则尾部丢弃）",
    )
    ap.add_argument("--max-tokens", type=int, default=4000, help="LLM 输出 token 上限")
    ap.add_argument(
        "--out",
        help="JSON 写到这个路径（默认打 stdout；传 '-' 也打 stdout）",
    )
    args = ap.parse_args()

    src = args.pdf or args.text
    try:
        data = summarize_file(
            src,
            provider=args.provider,
            max_chars=args.max_chars,
            max_tokens=args.max_tokens,
        )
    except Exception as e:
        sys.stderr.write(f"错误：{e}\n")
        return 1

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out and args.out != "-":
        Path(args.out).write_text(payload, encoding="utf-8")
        sys.stderr.write(f"[ingest_helper] 已写入 {args.out}\n")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
