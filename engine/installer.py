"""
Installation engine — downloads, converts, and places skills into each AI tool's directory.
"""
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
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

    @staticmethod
    def _validate_name(skill_name: str) -> None:
        # One basename only: no path separators, dot-files or traversal.
        if not isinstance(skill_name, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", skill_name
        ):
            raise ValueError("Unsafe skill name: expected a single filename-safe identifier")

    @staticmethod
    def _digest(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _ensure_digest_column(self) -> None:
        """Migrate older SQLite installs without destroying their inventory."""
        fields = {row[1] for row in self.db.execute("PRAGMA table_info(skill_files)")}
        if "content_sha256" not in fields:
            self.db.execute("ALTER TABLE skill_files ADD COLUMN content_sha256 TEXT")
            self.db.commit()

    def install(self, tool: str, skill_name: str, content: str) -> Path:
        """Install/upgrade only a file demonstrably owned by SkillForge.

        Manual files, symlinks, changed files and legacy installs without a
        recorded checksum are never overwritten. New writes are exclusive;
        updates are atomic and use the previous checksum as an ownership check.
        """
        self._validate_name(skill_name)
        target_dir = TOOL_DIRS.get(tool)
        if target_dir is None:
            raise ValueError(f"Unknown tool: {tool}")
        if not isinstance(content, str):
            raise TypeError("Skill content must be text")
        self._ensure_digest_column()

        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{skill_name}{self._get_extension(tool)}"
        digest = self._digest(content.encode("utf-8"))
        row = self.db.execute(
            "SELECT file_path, content_sha256 FROM skill_files WHERE skill_name = ? AND tool = ?",
            (skill_name, tool),
        ).fetchone()

        if target.is_symlink():
            raise FileExistsError(f"Refusing to write through a symlink: {target}")
        previous: bytes | None = None
        if target.exists():
            # Only an exact path and a digest-matched previous install may
            # be updated. Never silently destroy a human-edited file.
            if not target.is_file() or not row or row[0] != str(target) or not row[1]:
                raise FileExistsError(f"File already exists and is not a verified SkillForge install: {target}")
            previous = target.read_bytes()
            if self._digest(previous) != row[1]:
                raise FileExistsError(f"File has been modified; refusing overwrite: {target}")
            if self._digest(previous) == digest:
                return target
            fd, temp_name = tempfile.mkstemp(dir=target_dir, prefix=".skillforge-")
            try:
                with os.fdopen(fd, "wb") as output:
                    output.write(content.encode("utf-8"))
                os.replace(temp_name, target)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
        else:
            # 'x' is exclusive: it also refuses dangling symlinks and races
            # with an existing human file.
            with target.open("x", encoding="utf-8") as output:
                output.write(content)

        try:
            self._record_tool_install(skill_name, tool, str(target), digest)
        except Exception:
            # Keep file and database states aligned if SQLite cannot commit.
            if previous is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(previous)
            raise
        return target

    def uninstall(self, skill_name: str) -> List[str]:
        """Delete only registered, checksum-matched, unmodified skill files.

        No wildcard scan: a similarly named file from another tool or an old
        manually edited version is not ours to remove.
        """
        self._validate_name(skill_name)
        self._ensure_digest_column()
        rows = self.db.execute(
            "SELECT tool, file_path, content_sha256 FROM skill_files WHERE skill_name = ?",
            (skill_name,),
        ).fetchall()
        removed: List[str] = []
        for tool, path_str, expected_hash in rows:
            root = TOOL_DIRS.get(tool)
            if root is None:
                continue
            path = Path(path_str)
            expected_path = root / f"{skill_name}{self._get_extension(tool)}"
            if path != expected_path or path.is_symlink():
                continue
            if not path.exists():
                self.db.execute(
                    "DELETE FROM skill_files WHERE skill_name = ? AND tool = ?",
                    (skill_name, tool),
                )
                continue
            if not path.is_file() or not expected_hash:
                continue
            if self._digest(path.read_bytes()) != expected_hash:
                continue
            path.unlink()
            removed.append(str(path))
            self.db.execute(
                "DELETE FROM skill_files WHERE skill_name = ? AND tool = ?",
                (skill_name, tool),
            )
        self.db.commit()
        return removed

    def _get_extension(self, tool: str) -> str:
        extensions = {
            "claude": ".md",
            "codex": ".md",
            "aider": ".md",
            "qwen": ".md",
            "gemini": ".prompt",
        }
        return extensions.get(tool, ".md")

    def _record_tool_install(self, skill_name: str, tool: str, file_path: str, digest: str) -> None:
        # installed_at is NOT NULL in database/schema.sql.
        now = datetime.now(timezone.utc).isoformat()
        self.db.execute(
            "INSERT INTO skill_files (skill_name, tool, file_path, installed_at, content_sha256) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(skill_name, tool) DO UPDATE SET "
            "file_path=excluded.file_path, installed_at=excluded.installed_at, "
            "content_sha256=excluded.content_sha256",
            (skill_name, tool, file_path, now, digest),
        )
        self.db.commit()
