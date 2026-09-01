# ⚒️ SkillForge

> **The universal package manager for AI coding skills.**
> Write once. Install everywhere.

```
    ╔═══════════════════════════════════════╗
    ║   ⚒️  SKILLFORGE — The AI Grimoire   ║
    ║   One skill to rule them all.         ║
    ╚═══════════════════════════════════════╝
```

SkillForge installs AI coding skills into **all your AI tools** automatically.
Claude Code, Codex, Aider, Qwen Code, Gemini CLI — one command, every platform.

Think: **npm/brew but for AI agent skills.**

---

## 🚀 Install

```bash
curl -fsSL https://raw.githubusercontent.com/skillforge/skillforge/main/install.sh | bash
```

Or clone and install manually:

```bash
git clone https://github.com/skillforge/skillforge.git ~/.skillforge
~/.skillforge/install.sh
```

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

# Publish your skill to the community registry
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
5. **Update** — Compares local versions against registry, updates changed skills

## ⚙️ Requirements

- Python 3.7+ (stdlib only — no pip installs needed)
- Git (for registry access)
- Linux / macOS / WSL

## 📄 License

MIT — see below.

```
MIT License

Copyright (c) 2026 SkillForge Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
