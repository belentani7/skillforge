"""No-network, isolated HOME smoke tests for the Bash installer."""
from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("bash"), "Bash is required for install.sh")
class InstallScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.source = base / "package"
        self.source.mkdir()
        shutil.copy2(ROOT / "install.sh", self.source / "install.sh")
        (self.source / "skillforge").write_text("#!/usr/bin/env python3\nprint('v1')\n")
        for directory, filename, body in (
            ("database", "schema.sql", "CREATE TABLE IF NOT EXISTS installed (name TEXT);"),
            ("config", "default.yaml", "auto_update: false\n"),
            ("engine", "installer.py", "# stub"),
            ("ascii", "forge.txt", "SkillForge"),
        ):
            folder = self.source / directory
            folder.mkdir()
            (folder / filename).write_text(body)
        (self.source / "README.md").write_text("README")
        (self.source / "LICENSE").write_text("MIT")
        self.home = base / "User's Home 中文"
        self.home.mkdir()
        self.environment = {**os.environ, "HOME": str(self.home)}
        self.destination = self.home / ".skillforge"

    def run_installer(self, script=None, *args):
        return subprocess.run(
            ["bash", str(script or self.source / "install.sh"), *args],
            env=self.environment, text=True, capture_output=True, timeout=20,
        )

    def test_dry_run_has_no_side_effects(self):
        result = self.run_installer(None, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.destination.exists())

    def test_clean_install_and_reinstall_from_installed_directory(self):
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.destination / "skillforge").exists())
        self.assertTrue((self.destination / "local.db").exists())
        self.assertTrue((self.destination / "config/user.yaml").exists())
        result = self.run_installer(self.destination / "install.sh")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_upgrade_preserves_database_and_preferences(self):
        self.assertEqual(self.run_installer().returncode, 0)
        with sqlite3.connect(self.destination / "local.db") as db:
            db.execute("INSERT INTO installed VALUES ('valuable')")
            db.commit()
        preferences = self.destination / "config/user.yaml"
        preferences.write_text("custom: true\n")
        (self.source / "skillforge").write_text("#!/usr/bin/env python3\nprint('v2')\n")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(preferences.read_text(), "custom: true\n")
        self.assertIn("v2", (self.destination / "skillforge").read_text())
        with sqlite3.connect(self.destination / "local.db") as db:
            self.assertEqual(db.execute("SELECT name FROM installed").fetchone(), ("valuable",))

    def test_does_not_replace_unrelated_path_command(self):
        self.assertEqual(self.run_installer().returncode, 0)
        entry = self.home / ".local/bin/skillforge"
        entry.unlink()
        entry.write_text("personal executable")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING", result.stderr)
        self.assertEqual(entry.read_text(), "personal executable")

    def test_refuses_linked_destination_before_copy(self):
        self.assertEqual(self.run_installer().returncode, 0)
        (self.destination / "engine/linked.py").symlink_to(self.source / "skillforge")
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinks", result.stderr)

    def test_refuses_linked_source_before_copy(self):
        (self.source / "engine/linked.py").symlink_to(self.source / "skillforge")
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("linked source", result.stderr)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
