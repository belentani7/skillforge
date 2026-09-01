"""
Installation engine — downloads, converts, and places skills into each AI tool's directory.
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


# ── Tool directory mappings ───────────────────────────────────
TOOL_DIRS: Dict[str, Path] = {
    "claude": Path.home() / ".claude" / "commands",
    "codex":  Path.home() / ".codex" / "skills",
    "aider":  Path.home() / ".aider" / "conventions",
    "qwen":   Path.home() / ".qwen" / "skills",
    "gemini": Path.home() / ".gemini" / "prompts",
}


class Installer:
    """Handles installing skills into each AI tool's native directory."""

    def __init__(self, db: sqlite3.Connection, config: dict):
        self.db = db
        self.config = config
        self.forge_dir = Path(__file__).resolve().parent.parent

    def detect_tools(self) -> List[str]:
        """Detect which AI tools are installed on this system."""
        detected = []
        tool_checks = {
            "claude": [
                Path.home() / ".claude",
                Path.home() / ".claude" / "commands",
            ],
            "codex": [
                Path.home() / ".codex",
                Path.home() / ".codex" / "skills",
            ],
            "aider": [
                Path.home() / ".aider",
                Path.home() / ".aider" / "conventions",
            ],
            "qwen": [
                Path.home() / ".qwen",
                Path.home() / ".qwen" / "skills",
            ],
            "gemini": [
                Path.home() / ".gemini",
                Path.home() / ".gemini" / "prompts",
            ],
        }

        # Also check config for explicit enable/disable
        tools_config = self.config.get("tools", {})

        for tool, check_paths in tool_checks.items():
            # If explicitly disabled in config, skip
            if tools_config.get(tool) is False:
                continue
            # Check if any of the paths exist
            for p in check_paths:
                if p.exists():
                    detected.append(tool)
                    break

        return detected

    def install(self, tool: str, skill_name: str, content: str) -> Path:
        """
        Install skill content into the specified tool's directory.

        Args:
            tool: Tool identifier (claude, codex, aider, qwen, gemini)
            skill_name: Name of the skill
            content: Converted content string for this tool

        Returns:
            Path where the file was written
        """
        target_dir = TOOL_DIRS.get(tool)
        if not target_dir:
            raise ValueError(f"Unknown tool: {tool}")

        # Ensure directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename based on tool
        ext = self._get_extension(tool)
        filename = f"{skill_name}{ext}"
        target_path = target_dir / filename

        # Write the content
        target_path.write_text(content, encoding="utf-8")

        # Record installation in database
        self._record_tool_install(skill_name, tool, str(target_path))

        return target_path

    def uninstall(self, skill_name: str) -> List[str]:
        """
        Remove a skill from all tool directories.

        Returns:
            List of paths that were removed
        """
        removed = []

        # Check database for known paths
        cursor = self.db.execute(
            "SELECT file_path FROM skill_files WHERE skill_name = ?",
            (skill_name,),
        )
        known_paths = [row[0] for row in cursor.fetchall()]

        # Remove known paths
        for path_str in known_paths:
            path = Path(path_str)
            if path.exists():
                path.unlink()
                removed.append(str(path))

        # Also scan tool directories for any files matching the skill name
        for tool, tool_dir in TOOL_DIRS.items():
            if not tool_dir.exists():
                continue
            for ext in [".md", ".txt", ".yaml", ".yml", ".prompt"]:
                candidate = tool_dir / f"{skill_name}{ext}"
                if candidate.exists() and str(candidate) not in removed:
                    candidate.unlink()
                    removed.append(str(candidate))

        # Clean up database records
        self.db.execute(
            "DELETE FROM skill_files WHERE skill_name = ?", (skill_name,)
        )
        self.db.commit()

        return removed

    def _get_extension(self, tool: str) -> str:
        """Get the file extension for a given tool."""
        extensions = {
            "claude": ".md",
            "codex": ".md",
            "aider": ".md",
            "qwen": ".md",
            "gemini": ".prompt",
        }
        return extensions.get(tool, ".md")

    def _record_tool_install(self, skill_name: str, tool: str, file_path: str):
        """Record a file installation in the database."""
        try:
            self.db.execute(
                "INSERT OR REPLACE INTO skill_files (skill_name, tool, file_path) "
                "VALUES (?, ?, ?)",
                (skill_name, tool, file_path),
            )
            self.db.commit()
        except Exception:
            pass  # Non-fatal if DB write fails
