"""Aider format converter.

Aider uses conventions.md files in ~/.aider/conventions/ to establish
coding standards and behavioral guidelines for the AI pair programmer.
"""
from __future__ import annotations
from typing import Any, Dict


class AiderConverter:
    """Convert universal skill to Aider conventions format."""

    TOOL_NAME = "aider"
    EXTENSION = ".md"
    INSTALL_DIR = "~/.aider/conventions"

    def convert(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        version = skill.get("version", "")
        tags = skill.get("tags", [])
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])
        examples = content.get("examples", [])

        lines = [
            f"# Convention: {name}",
            "",
        ]

        if desc:
            lines.append(f"{desc}")
            lines.append("")

        meta_parts = []
        if version:
            meta_parts.append(f"v{version}")
        if tags:
            meta_parts.append(f"Tags: {', '.join(tags)}")
        if meta_parts:
            lines.append(f"*{' | '.join(meta_parts)}*")
            lines.append("")

        lines.append("## Guidelines")
        lines.append("")
        lines.append(prompt.strip())
        lines.append("")

        if constraints:
            lines.append("## Requirements")
            lines.append("")
            for c in constraints:
                lines.append(f"- {c}")
            lines.append("")

        if examples:
            lines.append("## Examples")
            lines.append("")
            for i, ex in enumerate(examples, 1):
                if isinstance(ex, dict):
                    lines.append(f"**Example {i}:**")
                    if ex.get("input"):
                        lines.append(f"```")
                        lines.append(ex["input"])
                        lines.append(f"```")
                    if ex.get("output"):
                        lines.append(f"Expected output:")
                        lines.append(f"```")
                        lines.append(ex["output"])
                        lines.append(f"```")
                    lines.append("")
                else:
                    lines.append(f"- {ex}")
            lines.append("")

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️ — Write once, use everywhere.*")

        return "\n".join(lines)
