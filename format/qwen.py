"""Qwen Code format converter.

Qwen Code uses skill definition files in ~/.qwen/skills/.
Skills are loaded as context into the Qwen Code agent session.
"""
from __future__ import annotations
from typing import Any, Dict


class QwenConverter:
    """Convert universal skill to Qwen Code skill format."""

    TOOL_NAME = "qwen"
    EXTENSION = ".md"
    INSTALL_DIR = "~/.qwen/skills"

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
            f"# {name}",
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
            lines.append(f"**{' | '.join(meta_parts)}**")
            lines.append("")

        lines.append("## Skill Instructions")
        lines.append("")
        lines.append(prompt.strip())
        lines.append("")

        if constraints:
            lines.append("## Constraints")
            lines.append("")
            for c in constraints:
                lines.append(f"- {c}")
            lines.append("")

        if examples:
            lines.append("## Examples")
            lines.append("")
            for i, ex in enumerate(examples, 1):
                if isinstance(ex, dict):
                    lines.append(f"### Example {i}")
                    if ex.get("input"):
                        lines.append(f"**Input:** {ex['input']}")
                    if ex.get("output"):
                        lines.append(f"**Output:** {ex['output']}")
                    lines.append("")
                else:
                    lines.append(f"- {ex}")
            lines.append("")

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️ — Write once, use everywhere.*")

        return "\n".join(lines)
