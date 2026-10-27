"""Offline regression tests for partial and complete skill uninstallation."""
import json
import sqlite3
import unittest

from engine.installed_state import reconcile_after_uninstall


class InstalledStateTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript("""
            CREATE TABLE installed_skills (name TEXT PRIMARY KEY, tools_installed TEXT);
            CREATE TABLE skill_files (skill_name TEXT, tool TEXT);
            INSERT INTO installed_skills VALUES ('review', '["claude", "codex"]');
            INSERT INTO skill_files VALUES ('review', 'codex');
        """)

    def test_partial_uninstall_preserves_parent_record_and_remaining_tool(self):
        self.assertEqual(reconcile_after_uninstall(self.db, "review"), ["codex"])
        row = self.db.execute("SELECT tools_installed FROM installed_skills WHERE name='review'").fetchone()
        self.assertEqual(json.loads(row[0]), ["codex"])

    def test_complete_uninstall_removes_parent_record(self):
        self.db.execute("DELETE FROM skill_files WHERE skill_name='review'")
        self.assertEqual(reconcile_after_uninstall(self.db, "review"), [])
        self.assertIsNone(self.db.execute("SELECT name FROM installed_skills WHERE name='review'").fetchone())

    def test_no_cross_skill_deletion_or_sql_injection(self):
        self.db.execute("INSERT INTO installed_skills VALUES (?, '[]')", ("review' OR 1=1 --",))
        self.assertEqual(reconcile_after_uninstall(self.db, "review' OR 1=1 --"), [])
        self.assertIsNotNone(self.db.execute("SELECT name FROM installed_skills WHERE name='review'").fetchone())

    def test_unverified_legacy_entry_is_still_visible(self):
        self.db.execute("INSERT INTO skill_files VALUES ('review', 'claude')")
        self.assertEqual(reconcile_after_uninstall(self.db, "review"), ["claude", "codex"])
        row = self.db.execute("SELECT tools_installed FROM installed_skills WHERE name='review'").fetchone()
        self.assertEqual(json.loads(row[0]), ["claude", "codex"])


if __name__ == "__main__":
    unittest.main()
