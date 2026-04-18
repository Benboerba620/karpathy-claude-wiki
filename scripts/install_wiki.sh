#!/usr/bin/env bash
# install_wiki.sh - karpathy-claude-wiki one-shot installer (macOS / Linux)

set -euo pipefail

print_step() { printf '\033[36m[karpathy-claude-wiki] %s\033[0m\n' "$1"; }
print_warn() { printf '\033[33m[karpathy-claude-wiki] %s\033[0m\n' "$1" >&2; }
print_done() { printf '\033[32m%s\033[0m\n' "$1"; }
die()        { printf '\033[31m[karpathy-claude-wiki] ERROR: %s\033[0m\n' "$1" >&2; exit 1; }

TARGET_DIR=""
WIKI_DIR_NAME="wiki"
LANGUAGE="zh-CN"
ENTITY_NAME=""
FORCE=0
SKIP_INDEX=0
WITH_INGEST_HELPER=0

usage() {
  cat <<'EOF'
Usage: bash install_wiki.sh --target-dir PATH [--entity-name NAME]
                            [--wiki-dir-name wiki] [--language zh-CN|en]
                            [--force] [--skip-index]
                            [--with-ingest-helper]

Required:
  --target-dir PATH     Project directory where the wiki will be installed.

Optional:
  --entity-name NAME    Scaffold a first entity (e.g. AAPL) under wiki/entities/.
  --wiki-dir-name NAME  Wiki directory name (default: wiki).
  --language LANG       Generated wiki language: zh-CN (default) or en.
  --force               Overwrite an existing wiki directory.
  --skip-index          Skip running wiki_index.py at the end.
  --with-ingest-helper  Also copy scripts/ingest_helper.py and .env.example.
  -h, --help            Show this message.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-dir)     TARGET_DIR="${2:-}";    shift 2 ;;
    --wiki-dir-name)  WIKI_DIR_NAME="${2:-}"; shift 2 ;;
    --language)       LANGUAGE="${2:-}";      shift 2 ;;
    --entity-name)    ENTITY_NAME="${2:-}";   shift 2 ;;
    --force)          FORCE=1;                 shift ;;
    --skip-index)     SKIP_INDEX=1;            shift ;;
    --with-ingest-helper) WITH_INGEST_HELPER=1; shift ;;
    -h|--help)        usage; exit 0 ;;
    *) die "Unknown argument: $1 (run with --help)" ;;
  esac
done

[[ -z "$TARGET_DIR" ]] && { usage; echo; die "--target-dir is required"; }

normalize_language() {
  case "${1,,}" in
    zh|zh-cn|zh-hans|cn) echo "zh-CN" ;;
    en|en-us|en-gb) echo "en" ;;
    *) die "Unsupported language '$1'. Use zh-CN or en." ;;
  esac
}

LANGUAGE="$(normalize_language "$LANGUAGE")"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

mkdir -p "$TARGET_DIR"
target_dir_abs="$(cd "$TARGET_DIR" && pwd)"

if [[ "$target_dir_abs" == "$repo_root" ]]; then
  die "--target-dir cannot be the template repo itself. Pass your own project directory."
fi

localized_source_path() {
  local relative_path="$1"
  local override_path="$repo_root/locales/$LANGUAGE/$relative_path"
  if [[ "$LANGUAGE" != "zh-CN" && -e "$override_path" ]]; then
    printf '%s\n' "$override_path"
  else
    printf '%s\n' "$repo_root/$relative_path"
  fi
}

source_wiki="$repo_root/wiki"
source_claude="$(localized_source_path "CLAUDE.md")"
source_index_script="$repo_root/scripts/wiki_index.py"
source_ingest_helper="$repo_root/scripts/ingest_helper.py"
source_ingest_skill_dir="$repo_root/skills/wiki-ingest"
source_env_example="$repo_root/.env.example"
target_wiki="$target_dir_abs/$WIKI_DIR_NAME"
target_scripts_dir="$target_dir_abs/scripts"
target_skills_dir="$target_dir_abs/skills"
target_index_script="$target_scripts_dir/wiki_index.py"
target_ingest_helper="$target_scripts_dir/ingest_helper.py"
target_ingest_skill_dir="$target_skills_dir/wiki-ingest"
target_claude="$target_dir_abs/CLAUDE.md"
target_env_example="$target_dir_abs/.env.example"

[[ -d "$source_wiki" ]]         || die "Template wiki/ not found at $source_wiki"
[[ -f "$source_claude" ]]       || die "Template CLAUDE.md not found at $source_claude"
[[ -f "$source_index_script" ]] || die "Template scripts/wiki_index.py not found"

if [[ -d "$target_wiki" ]]; then
  if [[ $FORCE -eq 0 ]]; then
    die "Target wiki directory already exists at $target_wiki. Pass --force to overwrite."
  fi
  rm -rf "$target_wiki"
fi

print_step "Copying wiki template to $target_wiki"
cp -R "$source_wiki" "$target_wiki"

apply_wiki_locale_overrides() {
  [[ "$LANGUAGE" == "zh-CN" ]] && return

  local locale_wiki_root="$repo_root/locales/$LANGUAGE/wiki"
  [[ -d "$locale_wiki_root" ]] || die "Locale wiki overrides not found for language '$LANGUAGE'"
  cp -R "$locale_wiki_root"/. "$target_wiki"
  print_step "Applied wiki locale overrides: $LANGUAGE"
}

apply_wiki_locale_overrides

normalize_copied_wiki() {
  local wiki_root="$1"
  rm -f "$wiki_root/_index.json" "$wiki_root/overview.md" "$wiki_root/_attention.md"

  local raw_root="$wiki_root/raw"
  [[ -d "$raw_root" ]] || return

  shopt -s dotglob nullglob
  for path in "$raw_root"/*; do
    rm -rf "$path"
  done

  : > "$raw_root/.gitkeep"
  shopt -u dotglob nullglob

  print_step "Removed generated files and non-template raw materials from copied wiki/"
}

normalize_copied_wiki "$target_wiki"

mkdir -p "$target_scripts_dir"
cp "$source_index_script" "$target_index_script"
print_step "Copied scripts/wiki_index.py"

if [[ -d "$source_ingest_skill_dir" ]]; then
  mkdir -p "$target_skills_dir"
  rm -rf "$target_ingest_skill_dir"
  cp -R "$source_ingest_skill_dir" "$target_ingest_skill_dir"
  print_step "Copied skills/wiki-ingest"
fi

if [[ $WITH_INGEST_HELPER -eq 1 ]]; then
  [[ -f "$source_ingest_helper" ]] || die "Template scripts/ingest_helper.py not found"
  [[ -f "$source_env_example" ]] || die "Template .env.example not found"
  cp "$source_ingest_helper" "$target_ingest_helper"
  cp "$source_env_example" "$target_env_example"
  print_step "Copied scripts/ingest_helper.py and .env.example"
fi

protocol_title() {
  if [[ "$LANGUAGE" == "en" ]]; then
    printf '%s\n' "Wiki Protocols"
  else
    printf '%s\n' "Wiki 协议"
  fi
}

protocol_heading() {
  if [[ "$LANGUAGE" == "en" ]]; then
    printf '%s\n' "# Wiki Protocols"
  else
    printf '%s\n' "# Wiki 协议"
  fi
}

protocol_intro() {
  if [[ "$LANGUAGE" == "en" ]]; then
    printf '%s\n' "> Installed from karpathy-claude-wiki. Read this together with $WIKI_DIR_NAME/_schema.md whenever working with the wiki."
  else
    printf '%s\n' "> 由 karpathy-claude-wiki 安装。处理 wiki 时请与 $WIKI_DIR_NAME/_schema.md 一起阅读。"
  fi
}

write_protocol_file() {
  local template="$1" wiki_root="$2" wiki_dir_name="$3"
  local out="$wiki_root/_protocols.md"
  local today body
  today="$(date +%Y-%m-%d)"

  body="$({
    perl -0ne '
      use strict; use warnings; use utf8;
      if (/^## Protocol 1 .*$/ms) {
        my $body = $&;
        $body =~ s/\s+\z//;
        print $body;
      } else {
        die "marker not found in template CLAUDE.md\n";
      }
    ' "$template"
  })" || die "Failed to extract protocol body from template CLAUDE.md"

  cat >"$out" <<EOF
---
title: $(protocol_title)
type: meta
created: $today
updated: $today
---

$(protocol_heading)

$(protocol_intro)

$body
EOF

  print_step "Wrote wiki protocol file: $out"
}

merge_claude_md() {
  local template="$1" target="$2" wiki_dir_name="$3"
  local section_header
  local section_body

  if [[ "$LANGUAGE" == "en" ]]; then
    section_header='## Wiki Protocols (karpathy-claude-wiki)'
    section_body=$(cat <<EOF
When working with \`$wiki_dir_name/\`, first read:
- \`$wiki_dir_name/_schema.md\`
- \`$wiki_dir_name/_protocols.md\`

Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.
If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.
EOF
)
  else
    section_header='## Wiki 协议（karpathy-claude-wiki）'
    section_body=$(cat <<EOF
处理 \`$wiki_dir_name/\` 时，请先阅读：
- \`$wiki_dir_name/_schema.md\`
- \`$wiki_dir_name/_protocols.md\`

使用这两个文件来执行摄入、交叉引用、矛盾扫描、结晶化与周期性维护。
如果 wiki 协议与上方项目级指令冲突，请先明确指出冲突，再询问用户以哪条规则为准。
EOF
)
  fi

  if [[ ! -f "$target" ]]; then
    cp "$template" "$target"
    print_step "Copied CLAUDE.md to project root"
    return
  fi

  if grep -qF "$section_header" "$target"; then
    print_step "Target CLAUDE.md already contains karpathy-claude-wiki protocols, skipping append"
    return
  fi

  cat >>"$target" <<EOF

$section_header

$section_body
EOF

  print_step "Appended lightweight wiki entry to existing CLAUDE.md"
}

create_first_entity() {
  local wiki_root="$1" name="$2"
  [[ -z "$name" ]] && return

  local tpl="$wiki_root/entities/_template/profile.md"
  [[ -f "$tpl" ]] || die "Entity template not found at $tpl"

  local entity_dir="$wiki_root/entities/$name"
  local entity_profile="$entity_dir/profile.md"
  local today
  today="$(date +%Y-%m-%d)"

  mkdir -p "$entity_dir"

  perl -e '
    use strict; use warnings;
    use utf8;
    my ($src, $dst, $name, $today) = @ARGV;

    open(my $f, "<:utf8", $src) or die "open: $!";
    local $/; my $c = <$f>; close $f;

    $c =~ s/\Q<Entity name>\E/$name/g;
    $c =~ s/\Q<实体名称>\E/$name/g;
    $c =~ s/\QYYYY-MM-DD\E/$today/g;
    $c =~ s/\Q| Started tracking | YYYY-MM-DD |\E/| Started tracking | $today |/g;
    $c =~ s/\Q| 开始跟踪 | YYYY-MM-DD |\E/| 开始跟踪 | $today |/g;
    $c =~ s/\Q- Related entities: [[entity1]], [[entity2]]\E/- Related entities:/g;
    $c =~ s/\Q- Related concepts: [[concept1]], [[concept2]]\E/- Related concepts:/g;
    $c =~ s|\Q- Related sources: [[sources/source1]], [[sources/source2]]\E|- Related sources:|g;
    $c =~ s/\Q- 相关实体：[[实体1]], [[实体2]]\E/- 相关实体：/g;
    $c =~ s/\Q- 相关概念：[[概念1]], [[概念2]]\E/- 相关概念：/g;
    $c =~ s|\Q- 相关来源：[[sources/source1]], [[sources/source2]]\E|- 相关来源：|g;
    $c =~ s/\Q- Variable 1 — why it matters, how to measure\E/- /g;
    $c =~ s/\Q- Variable 2 — why it matters, how to measure\E/- /g;
    $c =~ s/\Q- Variable 3 — why it matters, how to measure\E/- /g;
    $c =~ s/\Q- 变量 1：为什么重要，如何衡量\E/- /g;
    $c =~ s/\Q- 变量 2：为什么重要，如何衡量\E/- /g;
    $c =~ s/\Q- 变量 3：为什么重要，如何衡量\E/- /g;
    $c =~ s/\Q- (questions you haven\x{27}t answered yet)\E/- /g;
    $c =~ s/\Q- （你还没有回答的问题）\E/- /g;

    open(my $o, ">:utf8", $dst) or die "write: $!";
    print $o $c; close $o;
  ' "$tpl" "$entity_profile" "$name" "$today"

  print_step "Created first entity: $entity_profile"
}

write_protocol_file "$source_claude" "$target_wiki" "$WIKI_DIR_NAME"
merge_claude_md "$source_claude" "$target_claude" "$WIKI_DIR_NAME"
create_first_entity "$target_wiki" "$ENTITY_NAME"

if [[ $SKIP_INDEX -eq 0 ]]; then
  python_bin=""
  if command -v python3 >/dev/null 2>&1; then
    python_bin="python3"
  elif command -v python >/dev/null 2>&1; then
    python_bin="python"
  fi

  if [[ -n "$python_bin" ]]; then
    print_step "Generating wiki index"
    if ! (cd "$target_dir_abs" && "$python_bin" ./scripts/wiki_index.py); then
      print_warn "python was detected, but index generation failed. The wiki was still installed; run '$python_bin scripts/wiki_index.py' later."
    elif ! (cd "$target_dir_abs" && "$python_bin" ./scripts/wiki_index.py --lint); then
      print_warn "python was detected, but wiki lint failed. The wiki was still installed; run '$python_bin scripts/wiki_index.py --lint' after reviewing the files."
    fi
  else
    print_warn "python not detected; skipped index generation. The wiki was still installed; install Python 3 then run: python3 scripts/wiki_index.py"
  fi
fi

echo
if [[ "$LANGUAGE" == "en" ]]; then
  print_done "Installation complete. Next steps:"
  print_done "1. Drop a source file into $WIKI_DIR_NAME/raw/"
  print_done "2. Open Claude Code in $target_dir_abs"
  print_done "3. Tell it: \"Read $WIKI_DIR_NAME/_schema.md, $WIKI_DIR_NAME/_protocols.md, and CLAUDE.md, then ingest the file I just dropped following the ingest protocol.\""
  print_done "4. Optional: if you use Obsidian Clippings, ask the agent to scan it with: python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings"
else
  print_done "安装完成，下一步："
  print_done "1. 把一个源文件放进 $WIKI_DIR_NAME/raw/"
  print_done "2. 在 $target_dir_abs 打开 Claude Code"
  print_done "3. 对它说：\"先读 $WIKI_DIR_NAME/_schema.md、$WIKI_DIR_NAME/_protocols.md 和 CLAUDE.md，再按协议摄入我刚放进去的文件。\""
  print_done "4. 可选：如果你使用 Obsidian Clippings，可以先让 agent 运行：python skills/wiki-ingest/scripts/scan_pending_sources.py --include-obsidian-clippings"
fi
