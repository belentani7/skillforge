#!/usr/bin/env bash
# SkillForge local installer. Never downloads or executes remote code.
set -euo pipefail

usage() { printf 'Usage: %s [--dry-run]\n' "${0##*/}"; }
die() { printf 'SkillForge install refused: %s\n' "$*" >&2; exit 1; }
DRY_RUN=0
case "${1:-}" in
  '') ;;
  --dry-run) DRY_RUN=1 ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || { usage >&2; exit 2; }
[[ -n "${HOME:-}" ]] || die 'HOME is not set'
REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
FORGE_DIR="$HOME/.skillforge"
[[ ! -L "$FORGE_DIR" ]] || die 'destination is a symbolic link'
[[ -f "$REPO_DIR/skillforge" && -f "$REPO_DIR/database/schema.sql" ]] || die 'source package is incomplete'

# Copy only application files, not a source-tree database, user configuration,
# Git metadata, compiled Python caches, or files belonging to the user.
FILES=(skillforge install.sh README.md LICENSE config/default.yaml)
for pattern in \
  "$REPO_DIR"/ascii/*.txt "$REPO_DIR"/database/*.sql \
  "$REPO_DIR"/engine/*.py "$REPO_DIR"/format/*.py \
  "$REPO_DIR"/registry/*.json "$REPO_DIR"/templates/*.skill; do
  [[ -f "$pattern" ]] || continue
  FILES+=("${pattern#"$REPO_DIR"/}")
done
if [[ -d "$FORGE_DIR" ]] && [[ -n "$(find "$FORGE_DIR" -type l -print -quit)" ]]; then
  die 'destination contains symlinks; inspect them manually before upgrading'
fi
for relative in "${FILES[@]}"; do
  [[ -f "$REPO_DIR/$relative" && ! -L "$REPO_DIR/$relative" ]] || die "missing or linked source: $relative"
  [[ ! -L "$FORGE_DIR/$relative" ]] || die "linked destination: $relative"
done
if [[ "$DRY_RUN" == 1 ]]; then
  printf 'DRY RUN: would install %s application files to %s; keep local.db and config/user.yaml intact.\n' "${#FILES[@]}" "$FORGE_DIR"
  exit 0
fi
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  die 'Python 3.10+ is required; no files changed'
fi
"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"' || die 'Python 3.10+ required; no files changed'

if [[ "$REPO_DIR" != "$FORGE_DIR" ]]; then
  for relative in "${FILES[@]}"; do
    mkdir -p -- "$FORGE_DIR/$(dirname -- "$relative")"
    cp -p -- "$REPO_DIR/$relative" "$FORGE_DIR/$relative"
  done
else
  printf 'SkillForge: in-place installation; application files already present.\n'
fi
chmod u+x "$FORGE_DIR/skillforge"

# An upgrade must never rewrite a person's preferences.
if [[ ! -e "$FORGE_DIR/config/user.yaml" ]]; then
  cat > "$FORGE_DIR/config/user.yaml" <<'YAML'
# SkillForge user configuration; edit as needed. Preserved on upgrades.
auto_update: false
registry_url: https://api.github.com
tools:
  claude: true
  codex: true
  aider: true
  qwen: true
  gemini: true
YAML
fi

# Preserve unrelated executables in PATH rather than replacing them.
if [[ -d "$HOME/.local/bin" ]]; then
  BIN_DIR="$HOME/.local/bin"
elif [[ -d "$HOME/bin" ]]; then
  BIN_DIR="$HOME/bin"
else
  BIN_DIR="$HOME/bin"
  mkdir -p -- "$BIN_DIR"
fi
LINK="$BIN_DIR/skillforge"
if [[ ! -e "$LINK" && ! -L "$LINK" ]]; then

  ln -s -- "$FORGE_DIR/skillforge" "$LINK"
elif [[ ! -L "$LINK" || "$(readlink -- "$LINK")" != "$FORGE_DIR/skillforge" ]]; then
  printf 'WARNING: existing PATH entry left untouched: %s\n' "$LINK" >&2
fi

# Pass paths as arguments; HOME may contain spaces, quotes, or Unicode.
"$PYTHON" - "$FORGE_DIR" <<'PY'
import pathlib
import sqlite3
import sys
root = pathlib.Path(sys.argv[1])
with sqlite3.connect(root / 'local.db') as db:
    db.executescript((root / 'database/schema.sql').read_text(encoding='utf-8'))
PY
printf 'SkillForge installed at %s (existing database and preferences preserved).\n' "$FORGE_DIR"
printf 'Run %s --help; add %s to PATH if needed.\n' "$FORGE_DIR/skillforge" "$BIN_DIR"
