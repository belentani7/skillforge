#!/usr/bin/env bash
# ⚒️ SkillForge Installer
# Installs SkillForge to ~/.skillforge and sets up PATH
set -euo pipefail

FORGE_DIR="$HOME/.skillforge"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── ASCII Banner ──────────────────────────────────────────────
cat "$REPO_DIR/ascii/forge.txt" 2>/dev/null || echo "⚒️  SkillForge Installer"

echo ""
echo "═══════════════════════════════════════════"
echo "  ⚒️  SkillForge — The AI Skill Grimoire"
echo "═══════════════════════════════════════════"
echo ""

# ── Step 1: Copy files to ~/.skillforge ──────────────────────
echo "📦 Installing to $FORGE_DIR ..."
if [ -d "$FORGE_DIR" ]; then
    echo "   Existing installation found. Updating..."
    # Preserve local database
    if [ -f "$FORGE_DIR/local.db" ]; then
        cp "$FORGE_DIR/local.db" "$FORGE_DIR/local.db.bak"
    fi
fi

mkdir -p "$FORGE_DIR"
cp -r "$REPO_DIR"/* "$FORGE_DIR/"

# Restore database if preserved
if [ -f "$FORGE_DIR/local.db.bak" ]; then
    mv "$FORGE_DIR/local.db.bak" "$FORGE_DIR/local.db"
fi

# Make CLI executable
chmod +x "$FORGE_DIR/skillforge"

# ── Step 2: Detect installed AI tools ────────────────────────
echo ""
echo "🔍 Detecting installed AI tools..."

TOOLS_DETECTED=()

detect_tool() {
    local name="$1"
    local check_cmd="$2"
    local check_dir="$3"

    if command -v "$check_cmd" &>/dev/null || [ -d "$check_dir" ]; then
        echo "   ✅ $name"
        TOOLS_DETECTED+=("$name")
    else
        echo "   ⬜ $name (not found)"
    fi
}

detect_tool "Claude Code" "claude" "$HOME/.claude"
detect_tool "Codex" "codex" "$HOME/.codex"
detect_tool "Aider" "aider" "$HOME/.aider"
detect_tool "Qwen Code" "qwen" "$HOME/.qwen"
detect_tool "Gemini CLI" "gemini" "$HOME/.gemini"

if [ ${#TOOLS_DETECTED[@]} -eq 0 ]; then
    echo ""
    echo "   ⚠️  No AI tools detected. SkillForge will still install."
    echo "   Install skills later when you add a tool."
fi

# ── Step 3: Create default config ────────────────────────────
echo ""
echo "⚙️  Creating configuration..."

mkdir -p "$FORGE_DIR/config"

# Generate config with detected tools
cat > "$FORGE_DIR/config/user.yaml" <<YAML
# SkillForge User Configuration
# Generated on $(date -Iseconds)

install_dir: $FORGE_DIR
auto_update: false
registry_url: https://api.github.com

# Detected tools (edit to enable/disable)
tools:
YAML

for tool in claude codex aider qwen gemini; do
    found="false"
    for detected in "${TOOLS_DETECTED[@]}"; do
        case "$detected" in
            "Claude Code") [ "$tool" = "claude" ] && found="true" ;;
            "Codex") [ "$tool" = "codex" ] && found="true" ;;
            "Aider") [ "$tool" = "aider" ] && found="true" ;;
            "Qwen Code") [ "$tool" = "qwen" ] && found="true" ;;
            "Gemini CLI") [ "$tool" = "gemini" ] && found="true" ;;
        esac
    done
    echo "  $tool: $found" >> "$FORGE_DIR/config/user.yaml"
done

echo "   ✅ Config written to $FORGE_DIR/config/user.yaml"

# ── Step 4: Set up PATH ─────────────────────────────────────
echo ""
echo "🔗 Setting up PATH..."

# Create symlink in ~/.local/bin if it exists, otherwise guide user
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$FORGE_DIR/skillforge" "$HOME/.local/bin/skillforge"
    echo "   ✅ Symlinked to ~/.local/bin/skillforge"
elif [ -d "$HOME/bin" ]; then
    ln -sf "$FORGE_DIR/skillforge" "$HOME/bin/skillforge"
    echo "   ✅ Symlinked to ~/bin/skillforge"
else
    mkdir -p "$HOME/.local/bin"
    ln -sf "$FORGE_DIR/skillforge" "$HOME/.local/bin/skillforge"
    echo "   ✅ Created ~/.local/bin/skillforge"
    echo ""
    echo "   ⚠️  Add this to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "      export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# ── Step 5: Initialize database ──────────────────────────────
echo ""
echo "🗃️  Initializing local cache..."

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "   ⚠️  Python not found. Run 'skillforge' to initialize the database."
    PYTHON=""
fi

if [ -n "$PYTHON" ]; then
    if [ -f "$FORGE_DIR/database/schema.sql" ]; then
        $PYTHON -c "
import sqlite3, os
db = sqlite3.connect('$FORGE_DIR/local.db')
with open('$FORGE_DIR/database/schema.sql') as f:
    db.executescript(f.read())
db.close()
print('   ✅ SQLite database initialized')
" 2>/dev/null || echo "   ⚠️  Database init skipped (will auto-create on first use)"
    fi
fi

# ── Done ──────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  ✅ SkillForge installed successfully!"
echo ""
echo "  Tools detected: ${#TOOLS_DETECTED[@]}"
for t in "${TOOLS_DETECTED[@]}"; do
    echo "    • $t"
done
echo ""
echo "  Get started:"
echo "    skillforge search code-review"
echo "    skillforge install code-review"
echo "    skillforge list"
echo ""
echo "  ⚒️  The forge is lit. Go craft some spells."
echo "═══════════════════════════════════════════"
