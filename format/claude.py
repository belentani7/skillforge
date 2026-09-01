"""Claude Code format converter.

Claude Code uses slash commands stored as Markdown files in ~/.claude/commands/.
Each file becomes a /command-name slash command.
"""
from __future__ import annotations
from typing import Any, Dict


class ClaudeConverter:
    """Convert universal skill to Claude Code slash command format."""

    TOOL_NAME = "claude"
    EXTENSION = ".md"
    INSTALL_DIR = "~/.claude/commands"

    def convert(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        version = skill.get("version", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])
        examples = content.get("examples", [])

        lines = [
            f"# {name}",
            "",
            f"> {desc}" if desc else "",
            f"> v{version}" if version else "",
            "",
            "## Instructions",
            "",
            prompt.strip(),
            "",
        ]

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
