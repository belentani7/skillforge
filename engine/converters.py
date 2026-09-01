"""
Format conversion engine — translates universal YAML skills into each AI tool's native format.
"""
from __future__ import annotations

from typing import Any, Dict


class ConverterEngine:
    """Routes skill conversion to the appropriate format converter."""

    def convert(self, skill: Dict[str, Any], tool: str) -> str:
        """
        Convert a universal skill dict into the specified tool's native format.

        Args:
            skill: Parsed skill dictionary (from YAML)
            tool: Target tool identifier

        Returns:
            Formatted content string ready to write to disk
        """
        converters = {
            "claude": self.to_claude,
            "codex": self.to_codex,
            "aider": self.to_aider,
            "qwen": self.to_qwen,
            "gemini": self.to_gemini,
        }

        converter = converters.get(tool)
        if not converter:
            raise ValueError(f"No converter for tool: {tool}")

        return converter(skill)

    # ── Claude Code Format ────────────────────────────────────
    # Claude Code uses slash commands stored as .md files in ~/.claude/commands/
    # Format: Markdown with a prompt directive

    def to_claude(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])
        examples = content.get("examples", [])

        lines = [
            f"# {name}",
            "",
            f"> {desc}" if desc else "",
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
        lines.append(f"*Installed by SkillForge ⚒️*")

        return "\n".join(lines)

    # ── Codex Format ──────────────────────────────────────────
    # Codex uses AGENTS.md-style instructions in ~/.codex/skills/

    def to_codex(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])

        lines = [
            f"# Skill: {name}",
            "",
        ]

        if desc:
            lines.append(f"{desc}")
            lines.append("")

        lines.append("## Agent Instructions")
        lines.append("")
        lines.append(f"When the user invokes this skill, follow these instructions:")
        lines.append("")
        lines.append(prompt.strip())
        lines.append("")

        if constraints:
            lines.append("## Rules")
            lines.append("")
            for c in constraints:
                lines.append(f"- MUST: {c}")
            lines.append("")

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️*")

        return "\n".join(lines)

    # ── Aider Format ──────────────────────────────────────────
    # Aider uses conventions.md files in ~/.aider/conventions/

    def to_aider(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])

        lines = [
            f"# Convention: {name}",
            "",
        ]

        if desc:
            lines.append(f"{desc}")
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

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️*")

        return "\n".join(lines)

    # ── Qwen Code Format ──────────────────────────────────────
    # Qwen Code uses QWEN.md skill blocks in ~/.qwen/skills/

    def to_qwen(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
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

        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}")
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
        lines.append("*Installed by SkillForge ⚒️*")

        return "\n".join(lines)

    # ── Gemini CLI Format ────────────────────────────────────
    # Gemini CLI uses system prompt files in ~/.gemini/prompts/

    def to_gemini(self, skill: Dict[str, Any]) -> str:
        name = skill.get("name", "skill")
        desc = skill.get("description", "")
        content = skill.get("content", {})
        prompt = content.get("prompt", "")
        constraints = content.get("constraints", [])

        lines = []

        if desc:
            lines.append(f"# {name} — {desc}")
        else:
            lines.append(f"# {name}")
        lines.append("")

        lines.append("You have the following skill activated:")
        lines.append("")
        lines.append(prompt.strip())
        lines.append("")

        if constraints:
            lines.append("Follow these constraints:")
            lines.append("")
            for c in constraints:
                lines.append(f"- {c}")
            lines.append("")

        lines.append("---")
        lines.append("*Installed by SkillForge ⚒️*")

        return "\n".join(lines)
