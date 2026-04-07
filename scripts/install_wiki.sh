#!/usr/bin/env bash
# install_wiki.sh — karpathy-claude-wiki one-shot installer (macOS / Linux)
#
# Equivalent to scripts/install_wiki.ps1 (Windows PowerShell). Behaviour parity:
#  - copies wiki/ and scripts/wiki_index.py into the target project
#  - merges CLAUDE.md (or appends protocols if one already exists)
#  - optionally scaffolds a first entity from the template
#  - generates wiki index + lint (gracefully skips if no python)
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
    --target-dir)     TARGET_DIR="${2:-}";    shift 2;;
    --wiki-dir-name)  WIKI_DIR_NAME="${2:-}"; shift 2;;
    --entity-name)    ENTITY_NAME="${2:-}";   shift 2;;
    --force)          FORCE=1;                shift;;
    --skip-index)     SKIP_INDEX=1;           shift;;
    -h|--help)        usage; exit 0;;
    *) die "Unknown argument: $1 (run with --help)";;
  esac
done

[[ -z "$TARGET_DIR" ]] && { usage; echo; die "--target-dir is required"; }

# resolve paths
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

# ----- merge CLAUDE.md -----
merge_claude_md() {
  local template="$1" target="$2"

  if [[ ! -f "$target" ]]; then
    cp "$template" "$target"
    print_step "Copied CLAUDE.md to project root"
    return
  fi

  if grep -qF '## Wiki Protocols (from karpathy-claude-wiki)' "$target"; then
    print_step "Target CLAUDE.md already contains karpathy-claude-wiki protocols, skipping append"
    return
  fi

  perl -e '
    use strict; use warnings;
    use utf8;
    binmode STDOUT, ":utf8";
    my ($tpl_path, $tgt_path) = @ARGV;

    open(my $tf, "<:utf8", $tpl_path) or die "open template: $!";
    local $/; my $tpl = <$tf>; close $tf;

    my $marker = "## Protocol 1 \x{2014} Ingest";  # em-dash
    my $idx = index($tpl, $marker);
    die "marker not found in template CLAUDE.md\n" if $idx < 0;

    my $trimmed = substr($tpl, $idx);
    $trimmed =~ s/\s+\z//;

    # shift H2..H5 down by one level; leave H6 / H1 alone
    my @out;
    for my $line (split /\r?\n/, $trimmed) {
      if ($line =~ /^(#{2,5})\s+/) { push @out, "#" . $line; }
      else { push @out, $line; }
    }
    my $shifted = join("\n", @out);

    open(my $gf, "<:utf8", $tgt_path) or die "open target: $!";
    my $existing = <$gf>; close $gf;
    $existing =~ s/\s+\z//;

    my $merged = $existing
               . "\n\n## Wiki Protocols (from karpathy-claude-wiki)\n\n"
               . $shifted . "\n";

    open(my $of, ">:utf8", $tgt_path) or die "write target: $!";
    print $of $merged; close $of;
  ' "$template" "$target"

  print_step "Appended wiki protocols to existing CLAUDE.md"
}

merge_claude_md "$source_claude" "$target_claude"

# ----- scaffold first entity -----
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

    # NOTE: \Q...\E does NOT interpret \x{} or \x escapes inside the literal —
    # we have to interpolate the special characters via Perl variables.
    my $em  = "\x{2014}";  # em-dash
    my $apo = "\x{27}";    # apostrophe

    $c =~ s/\Q<Entity name>\E/$name/g;
    $c =~ s/\QYYYY-MM-DD\E/$today/g;
    $c =~ s/\Q- Related entities: [[entity1]], [[entity2]]\E/- Related entities:/g;
    $c =~ s/\Q- Related concepts: [[concept1]], [[concept2]]\E/- Related concepts:/g;
    $c =~ s|\Q- Related sources: [[sources/source1]], [[sources/source2]]\E|- Related sources:|g;
    $c =~ s/\Q- Variable 1 ${em} why it matters, how to measure\E/- /g;
    $c =~ s/\Q- Variable 2 ${em} why it matters, how to measure\E/- /g;
    $c =~ s/\Q- Variable 3 ${em} why it matters, how to measure\E/- /g;
    $c =~ s/\Q- (questions you haven${apo}t answered yet)\E/- /g;

    open(my $o, ">:utf8", $dst) or die "write: $!";
    print $o $c; close $o;
  ' "$tpl" "$entity_profile" "$name" "$today"

  print_step "Created first entity: $entity_profile"
}

create_first_entity "$target_wiki" "$ENTITY_NAME"

# ----- run index + lint -----
if [[ $SKIP_INDEX -eq 0 ]]; then
  python_bin=""
  if   command -v python3 >/dev/null 2>&1; then python_bin="python3"
  elif command -v python  >/dev/null 2>&1; then python_bin="python"
  fi

  if [[ -n "$python_bin" ]]; then
    print_step "Generating wiki index"
    (cd "$target_dir_abs" && "$python_bin" ./scripts/wiki_index.py)
    (cd "$target_dir_abs" && "$python_bin" ./scripts/wiki_index.py --lint) \
      || die "wiki lint failed"
  else
    print_warn "python not detected; skipped index generation. Install Python 3 then run: python3 scripts/wiki_index.py"
  fi
fi

echo
print_done "Installation complete. Next steps:"
print_done "1. Drop a source file into $WIKI_DIR_NAME/raw/articles/ (or papers/, books/, podcasts/, conversations/)"
print_done "2. Open Claude Code in $target_dir_abs"
print_done "3. Tell it: \"Read $WIKI_DIR_NAME/_schema.md and CLAUDE.md, then ingest the file I just dropped following the ingest protocol.\""
