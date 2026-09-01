"""Codex format converter.

Codex uses AGENTS.md-style instruction files in ~/.codex/skills/.
These are read as persistent instructions for the agent.
"""
from __future__ import annotations
from typing import Any, Dict


class CodexConverter:
    """Convert universal skill to Codex AGENTS.md instruction format."""

    TOOL_NAME = "codex"
    EXTENSION = ".md"
    INSTALL_DIR = "~/.codex/skills"

    def convert(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        version = skill.get("version", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])
        examples = content.get("examples", [])

        lines = [
            f"# Skill: {name}",
            "",
        ]

        if desc:
            lines.append(f"**Purpose:** {desc}")
            lines.append("")
        if version:
            lines.append(f"**Version:** {version}")
            lines.append("")

        lines.append("## Agent Instructions")
        lines.append("")
        lines.append("When the user invokes this skill, follow these instructions:")
        lines.append("")
        lines.append(prompt.strip())
        lines.append("")

        if constraints:
            lines.append("## Rules")
            lines.append("")
            for c in constraints:
                lines.append(f"- MUST: {c}")
            lines.append("")

        if examples:
            lines.append("## Reference Examples")
            lines.append("")
            for i, ex in enumerate(examples, 1):
                if isinstance(ex, dict):
                    lines.append(f"**Example {i}:**")
                    if ex.get("input"):
                        lines.append(f"  - Given: {ex['input']}")
                    if ex.get("output"):
                        lines.append(f"  - Produce: {ex['output']}")
                else:
                    lines.append(f"- {ex}")
            lines.append("")

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️ — Write once, use everywhere.*")

        return "\n".join(lines)
