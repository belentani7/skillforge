"""Offline regression tests for GitHub skill discovery and installable manifests."""
import sqlite3
import unittest
from unittest.mock import patch

from engine.registry import Registry


class RegistrySafetyTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.registry = Registry(self.db, {})

    def test_github_topics_are_strings_not_name_objects(self):
        payload = {"items": [{
            "name": "sample-skill", "owner": {"login": "someone"},
            "description": "A sample", "topics": ["ai-skill", "python", "testing"],
            "html_url": "https://github.com/someone/sample-skill",
            "default_branch": "main",
        }]}
        with patch("engine.registry._fetch_json", return_value=payload):
            results = self.registry._search_github("sample-skill")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["tags"], ["python", "testing"])

    def test_search_hit_without_manifest_is_not_installed(self):
        metadata = {"name": "unverified-unique-name", "repo_url": "https://github.com/a/b", "default_branch": "main"}
        with patch.object(self.registry, "_search_github", return_value=[metadata]), patch.object(
            self.registry, "_fetch_remote_skill", return_value=None
        ):
            self.assertIsNone(self.registry.fetch("unverified-unique-name"))

    def test_remote_manifest_requires_matching_name_and_prompt(self):
        metadata = {"name": "unverified-unique-name", "repo_url": "https://github.com/a/b", "default_branch": "main"}
        invalid = {"name": "unverified-unique-name", "version": "1.0.0", "description": "x", "content": {}}
        with patch.object(self.registry, "_search_github", return_value=[metadata]), patch.object(
            self.registry, "_fetch_remote_skill", return_value=invalid
        ):
            self.assertIsNone(self.registry.fetch("unverified-unique-name"))

    def test_valid_remote_manifest_is_returned(self):
        metadata = {"name": "unverified-unique-name", "repo_url": "https://github.com/a/b", "default_branch": "main"}
        valid = {"name": "unverified-unique-name", "version": "1.0.0", "description": "x", "content": {"prompt": "do work"}}
        with patch.object(self.registry, "_search_github", return_value=[metadata]), patch.object(
            self.registry, "_fetch_remote_skill", return_value=valid
        ):
            self.assertEqual(self.registry.fetch("unverified-unique-name"), valid)


if __name__ == "__main__":
    unittest.main()
