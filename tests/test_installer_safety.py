"""Regression coverage for safe, reversible AI skill installs (stdlib only)."""
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.installer import Installer, TOOL_DIRS

ROOT = Path(__file__).resolve().parent.parent


class InstallerSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript((ROOT / "database/schema.sql").read_text(encoding="utf-8"))
        tools = {tool: self.directory / tool for tool in TOOL_DIRS}
        patched = patch.dict(TOOL_DIRS, tools, clear=True)
        patched.start()
        self.addCleanup(patched.stop)
        self.installer = Installer(self.db, {})

    def test_installs_file_and_records_complete_sqlite_row(self):
        path = self.installer.install("codex", "debug-skill", "Helpful instructions")
        self.assertEqual(path.read_text(encoding="utf-8"), "Helpful instructions")
        row = self.db.execute(
            "SELECT installed_at, content_sha256 FROM skill_files WHERE skill_name=? AND tool=?",
            ("debug-skill", "codex"),
        ).fetchone()
        self.assertTrue(row[0])
        self.assertEqual(row[1], hashlib.sha256(b"Helpful instructions").hexdigest())

    def test_rejects_path_traversal_and_absolute_names(self):
        for name in ("../steal", "/tmp/steal", "x/y", "x\\y", ".", "..", "-hidden", ""):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.installer.install("codex", name, "content")
        self.assertFalse((self.directory / "steal").exists())

    def test_rejects_overwriting_user_managed_file(self):
        path = TOOL_DIRS["codex"] / "manual.md"
        path.parent.mkdir(parents=True)
        path.write_text("my original notes", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.installer.install("codex", "manual", "new content")
        self.assertEqual(path.read_text(encoding="utf-8"), "my original notes")

    def test_allows_verified_upgrade_of_unmodified_install(self):
        path = self.installer.install("codex", "build", "version one")
        self.assertEqual(self.installer.install("codex", "build", "version two"), path)
        self.assertEqual(path.read_text(), "version two")
        self.assertEqual(self.installer.install("codex", "build", "version two"), path)

    def test_blocks_update_and_uninstall_if_user_changed_file(self):
        path = self.installer.install("codex", "build", "initial")
        path.write_text("valuable changes")
        with self.assertRaises(FileExistsError):
            self.installer.install("codex", "build", "upgraded")
        self.assertEqual(self.installer.uninstall("build"), [])
        self.assertEqual(path.read_text(), "valuable changes")
        self.assertEqual(self.db.execute("SELECT count(*) FROM skill_files").fetchone()[0], 1)

    def test_uninstall_only_tracked_files_and_not_similarly_named_files(self):
        path = self.installer.install("codex", "safe", "owned")
        unrelated = TOOL_DIRS["codex"] / "safe.txt"
        unrelated.write_text("user notes")
        self.assertEqual(self.installer.uninstall("safe"), [str(path)])
        self.assertFalse(path.exists())
        self.assertEqual(unrelated.read_text(), "user notes")

    def test_forged_registry_path_cannot_delete_outside_tool_dir(self):
        outside = self.directory / "important.txt"
        outside.write_text("private")
        digest = hashlib.sha256(b"private").hexdigest()
        self.db.execute(
            "INSERT INTO skill_files(skill_name,tool,file_path,installed_at,content_sha256) VALUES(?,?,?,?,?)",
            ("safe", "codex", str(outside), "now", digest),
        )
        self.db.commit()
        self.assertEqual(self.installer.uninstall("safe"), [])
        self.assertEqual(outside.read_text(), "private")

    def test_legacy_without_checksum_is_not_deleted_or_overwritten(self):
        path = TOOL_DIRS["codex"] / "legacy.md"
        path.parent.mkdir(parents=True)
        path.write_text("existing")
        self.db.execute(
            "INSERT INTO skill_files(skill_name,tool,file_path,installed_at) VALUES(?,?,?,?)",
            ("legacy", "codex", str(path), "past"),
        )
        self.db.commit()
        self.assertEqual(self.installer.uninstall("legacy"), [])
        with self.assertRaises(FileExistsError):
            self.installer.install("codex", "legacy", "replaced")
        self.assertEqual(path.read_text(), "existing")

    def test_failed_database_write_removes_newly_created_file(self):
        with patch.object(self.installer, "_record_tool_install", side_effect=sqlite3.OperationalError("readonly")):
            with self.assertRaises(sqlite3.OperationalError):
                self.installer.install("codex", "unstored", "text")
        self.assertFalse((TOOL_DIRS["codex"] / "unstored.md").exists())

    def test_unknown_tool_is_rejected(self):
        with self.assertRaises(ValueError):
            self.installer.install("unknown-tool", "safe", "data")

    def test_legacy_database_schema_is_migrated_non_destructively(self):
        old = sqlite3.connect(":memory:")
        self.addCleanup(old.close)
        old.execute(
            "CREATE TABLE skill_files (skill_name TEXT NOT NULL, tool TEXT NOT NULL, "
            "file_path TEXT NOT NULL, installed_at TEXT NOT NULL, UNIQUE(skill_name, tool))"
        )
        legacy = Installer(old, {})
        path = legacy.install("codex", "migrated", "data")
        self.assertTrue(path.exists())
        self.assertIn("content_sha256", [row[1] for row in old.execute("PRAGMA table_info(skill_files)")])


if __name__ == "__main__":
    unittest.main()
