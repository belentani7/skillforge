# ⚒️ SkillForge

> **The universal package manager for AI coding skills.**
> Write once. Install everywhere.

```
    ╔═══════════════════════════════════════╗
    ║   ⚒️  SKILLFORGE — The AI Grimoire   ║
    ║   One skill to rule them all.         ║
    ╚═══════════════════════════════════════╝
```

SkillForge converts and installs selected AI coding skills into **detected, enabled tools** when you explicitly invoke `skillforge install`.
Claude Code, Codex, Aider, Qwen Code, Gemini CLI — one command, every platform.

Think: **npm/brew but for AI agent skills.**

---

## 🚀 Install (local, reviewed source)

Use a reviewed checkout of `belentani7/skillforge`; the repository is currently **public**. The installer **does not download code**, change GitHub visibility, or publish skills.

```bash
git clone git@github.com:belentani7/skillforge.git
cd skillforge
bash install.sh --dry-run
bash install.sh
```

The Bash installer supports Linux/macOS/WSL with Python 3.10+. It preserves `~/.skillforge/local.db` and `config/user.yaml` on upgrades, refuses symlinked installation trees, and does not replace unrelated commands in PATH. It does **not** currently implement a full rollback or uninstall of the application itself. `skillforge uninstall <name>` removes only verified, unmodified skill files.

## ⚡ Quick Start

```bash
# Search the grimoire for spells
skillforge search code-review

# Install a skill (auto-detects your AI tools)
skillforge install code-review

# List your installed skills
skillforge list

# Update all skills to latest versions
skillforge update

# Create a new skill from template
skillforge init my-awesome-skill

# Validate a skill and get instructions for optional manual publication
skillforge publish ./my-awesome-skill
```

## 🛠️ Supported Tools

| Tool | Install Location | Format |
|------|-----------------|--------|
| **Claude Code** | `~/.claude/commands/` | CLAUDE.md slash commands |
| **Codex** | `~/.codex/skills/` | AGENTS.md instructions |
| **Aider** | `~/.aider/conventions/` | conventions.md files |
| **Qwen Code** | `~/.qwen/skills/` | QWEN.md skill blocks |
| **Gemini CLI** | `~/.gemini/prompts/` | System prompt files |

## 📜 Skill Format

Skills are defined in a universal YAML format and automatically converted to each tool's native format:

```yaml
name: code-review
version: 1.0.0
author: your-username
description: Comprehensive code review skill
tags: [code-quality, review, best-practices]
tools: [claude, codex, aider, qwen, gemini]
content:
  prompt: |
    Review this code for:
    - Correctness and edge cases
    - Performance bottlenecks
    - Security vulnerabilities
    - Best practices and conventions
  examples:
    - input: "Review this function for bugs"
      output: "I'll analyze the function for..."
  constraints:
    - "Always provide specific line references"
    - "Suggest fixes, not just problems"
```

## 🔮 The Lore

- Skills are **spells** that empower AI agents
- The Forge is where skills are **crafted**
- Publishing a skill is **enchanting the community**
- The Registry is a **grimoire** of collective knowledge

## 📁 Project Structure

```
skillforge/
├── skillforge          # Main CLI entry point
├── install.sh          # Installation script
├── engine/
│   ├── installer.py    # Installation engine
│   ├── converters.py   # Format conversion engine
│   └── registry.py     # Registry client
├── format/
│   ├── universal.yaml  # Universal skill format spec
│   ├── claude.py       # Claude Code converter
│   ├── codex.py        # Codex converter
│   ├── aider.py        # Aider converter
│   ├── qwen.py         # Qwen Code converter
│   └── gemini.py       # Gemini CLI converter
├── templates/
│   └── basic.skill     # Skill template
├── database/
│   └── schema.sql      # SQLite schema for local cache
├── config/
│   └── default.yaml    # Default configuration
├── ascii/
│   └── forge.txt       # ASCII art
└── registry/
    └── popular.json    # Curated popular skills
```

## 🧩 How It Works

1. **Search** — Queries GitHub repos tagged `ai-skill` and the local curated registry
2. **Install** — Downloads the skill YAML, converts it to each detected tool's format, and places files in the correct locations
3. **Convert** — Each tool has a converter that translates universal YAML → native format
4. **Cache** — SQLite tracks installed skills, versions, and dependencies
5. **Update** — Compares local versions against registry and updates only verified, unmodified installed files

## ⚙️ Requirements

- Python 3.10+ (stdlib only — no pip installs needed)
- Git only for cloning; remote registry search uses HTTPS and is optional
- Linux / macOS / WSL

## 📄 License

MIT — see [LICENSE](LICENSE) for the canonical copyright and license text.
