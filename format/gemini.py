"""Gemini CLI format converter.

Gemini CLI uses system prompt files (.prompt) in ~/.gemini/prompts/.
These are injected as persistent system instructions.
"""
from __future__ import annotations
from typing import Any, Dict


class GeminiConverter:
    """Convert universal skill to Gemini CLI prompt format."""

    TOOL_NAME = "gemini"
    EXTENSION = ".prompt"
    INSTALL_DIR = "~/.gemini/prompts"

    def convert(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        version = skill.get("version", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])
        examples = content.get("examples", [])

        lines = []

        # Header
        if desc:
            lines.append(f"# {name} — {desc}")
        else:
            lines.append(f"# {name}")
        if version:
            lines.append(f"Version: {version}")
        lines.append("")

        # Core instructions
        lines.append("You have the following skill activated:")
        lines.append("")
        lines.append(prompt.strip())
        lines.append("")

        # Constraints as directives
        if constraints:
            lines.append("Follow these constraints:")
            lines.append("")
            for c in constraints:
                lines.append(f"- {c}")
            lines.append("")

        # Examples
        if examples:
            lines.append("Reference examples:")
            lines.append("")
            for i, ex in enumerate(examples, 1):
                if isinstance(ex, dict):
                    lines.append(f"Example {i}:")
                    if ex.get("input"):
                        lines.append(f"  Input: {ex['input']}")
                    if ex.get("output"):
                        lines.append(f"  Output: {ex['output']}")
                    lines.append("")
                else:
                    lines.append(f"- {ex}")
            lines.append("")

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️ — Write once, use everywhere.*")

        return "\n".join(lines)
