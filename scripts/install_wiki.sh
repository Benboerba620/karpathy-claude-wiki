#!/usr/bin/env bash
# install_wiki.sh - karpathy-claude-wiki one-shot installer (macOS / Linux)
#
# Equivalent to scripts/install_wiki.ps1 (Windows PowerShell). Behaviour parity:
#  - copies wiki/ and scripts/wiki_index.py into the target project
#  - writes wiki/_protocols.md and lightly merges CLAUDE.md if one already exists
#  - optionally scaffolds a first entity from the template
#  - generates wiki index + lint (gracefully skips if Python is unavailable or fails)
#
# Usage:
#   bash scripts/install_wiki.sh --target-dir ~/my-project --entity-name AAPL
#
# Run with --help for the full option list.

set -euo pipefail

print_step() { printf '\033[36m[karpathy-claude-wiki] %s\033[0m\n' "$1"; }
print_warn() { printf '\033[33m[karpathy-claude-wiki] %s\033[0m\n' "$1" >&2; }
print_done() { printf '\033[32m%s\033[0m\n' "$1"; }
die()        { printf '\033[31m[karpathy-claude-wiki] ERROR: %s\033[0m\n' "$1" >&2; exit 1; }

TARGET_DIR=""
WIKI_DIR_NAME="wiki"
ENTITY_NAME=""
FORCE=0
SKIP_INDEX=0

usage() {
  cat <<'EOF'
Usage: bash install_wiki.sh --target-dir PATH [--entity-name NAME]
                            [--wiki-dir-name wiki] [--force] [--skip-index]

Required:
  --target-dir PATH     Project directory where the wiki will be installed.

Optional:
  --entity-name NAME    Scaffold a first entity (e.g. AAPL) under wiki/entities/.
  --wiki-dir-name NAME  Wiki directory name (default: wiki).
  --force               Overwrite an existing wiki directory.
  --skip-index          Skip running wiki_index.py at the end.
  -h, --help            Show this message.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-dir)     TARGET_DIR="${2:-}";    shift 2 ;;
    --wiki-dir-name)  WIKI_DIR_NAME="${2:-}"; shift 2 ;;
    --entity-name)    ENTITY_NAME="${2:-}";   shift 2 ;;
    --force)          FORCE=1;                 shift ;;
    --skip-index)     SKIP_INDEX=1;            shift ;;
    -h|--help)        usage; exit 0 ;;
    *) die "Unknown argument: $1 (run with --help)" ;;
  esac
done

[[ -z "$TARGET_DIR" ]] && { usage; echo; die "--target-dir is required"; }

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

mkdir -p "$TARGET_DIR"
target_dir_abs="$(cd "$TARGET_DIR" && pwd)"

if [[ "$target_dir_abs" == "$repo_root" ]]; then
  die "--target-dir cannot be the template repo itself. Pass your own project directory."
fi

source_wiki="$repo_root/wiki"
source_claude="$repo_root/CLAUDE.md"
source_index_script="$repo_root/scripts/wiki_index.py"
target_wiki="$target_dir_abs/$WIKI_DIR_NAME"
target_scripts_dir="$target_dir_abs/scripts"
target_index_script="$target_scripts_dir/wiki_index.py"
target_claude="$target_dir_abs/CLAUDE.md"

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

mkdir -p "$target_scripts_dir"
cp "$source_index_script" "$target_index_script"
print_step "Copied scripts/wiki_index.py"

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
title: Wiki Protocols
type: meta
created: $today
updated: $today
---

# Wiki Protocols

> Installed from karpathy-claude-wiki. Read this together with $wiki_dir_name/_schema.md whenever working with the wiki.

$body
EOF

  print_step "Wrote wiki protocol file: $out"
}

merge_claude_md() {
  local template="$1" target="$2" wiki_dir_name="$3"

  if [[ ! -f "$target" ]]; then
    cp "$template" "$target"
    print_step "Copied CLAUDE.md to project root"
    return
  fi

  if grep -qF '## Wiki Protocols (karpathy-claude-wiki)' "$target"; then
    print_step "Target CLAUDE.md already contains karpathy-claude-wiki protocols, skipping append"
    return
  fi

  cat >>"$target" <<EOF

## Wiki Protocols (karpathy-claude-wiki)

When working with `$wiki_dir_name/`, first read:
- `$wiki_dir_name/_schema.md`
- `$wiki_dir_name/_protocols.md`

Use those files for ingest, cross-reference, contradiction scan, crystallization, and periodic wiki maintenance.
If the wiki protocol conflicts with project-specific instructions above, surface the conflict and ask the user which rule should win.
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
    $c =~ s/\QYYYY-MM-DD\E/$today/g;
    $c =~ s/\Q- Related entities: [[entity1]], [[entity2]]\E/- Related entities:/g;
    $c =~ s/\Q- Related concepts: [[concept1]], [[concept2]]\E/- Related concepts:/g;
    $c =~ s|\Q- Related sources: [[sources/source1]], [[sources/source2]]\E|- Related sources:|g;
    $c =~ s/\Q- Variable 1 — why it matters, how to measure\E/- /g;
    $c =~ s/\Q- Variable 2 — why it matters, how to measure\E/- /g;
    $c =~ s/\Q- Variable 3 — why it matters, how to measure\E/- /g;
    $c =~ s/\Q- (questions you haven\x{27}t answered yet)\E/- /g;

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
print_done "Installation complete. Next steps:"
print_done "1. Drop a source file into $WIKI_DIR_NAME/raw/articles/ (or papers/, books/, podcasts/, conversations/)"
print_done "2. Open Claude Code in $target_dir_abs"
print_done "3. Tell it: \"Read $WIKI_DIR_NAME/_schema.md, $WIKI_DIR_NAME/_protocols.md, and CLAUDE.md, then ingest the file I just dropped following the ingest protocol.\""
