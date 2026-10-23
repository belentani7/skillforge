"""Configuration parsing and opt-in installation safety (offline)."""
import contextlib
import io
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]


class CliConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(ROOT / "skillforge"))

    def test_nested_tool_disable_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "user.yaml"
            path.write_text("auto_update: false\ntools:\n  claude: false\n  codex: true\n  gemini: false\n")
            data = self.module["_parse_simple_yaml"](path)
        self.assertEqual(data["tools"], {"claude": False, "codex": True, "gemini": False})
        self.assertIs(data["auto_update"], False)

    def test_flat_values_and_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text("cache_ttl: 3600\ncolor: never\nallowed:\n  - codex\n  - gemini\n")
            data = self.module["_parse_simple_yaml"](path)
        self.assertEqual(data["cache_ttl"], 3600)
        self.assertEqual(data["color"], "never")
        self.assertEqual(data["allowed"], ["codex", "gemini"])

    def test_no_detected_tool_does_not_install_everywhere(self):
        namespace = self.module
        globals_dict = namespace["cmd_install"].__globals__
        original = {name: globals_dict[name] for name in ("load_config", "get_db", "Registry", "Installer")}
        registry = MagicMock()
        registry.fetch.return_value = {"name": "example", "version": "1.0.0", "description": "safe", "content": {"prompt": "x"}}
        installer = MagicMock()
        installer.detect_tools.return_value = []
        try:
            globals_dict["load_config"] = lambda: {}
            globals_dict["get_db"] = lambda: object()
            globals_dict["Registry"] = lambda *args: registry
            globals_dict["Installer"] = lambda *args: installer
            with contextlib.redirect_stdout(io.StringIO()):
                globals_dict["cmd_install"](type("Args", (), {"skill": "example"})())
            installer.install.assert_not_called()
            registry.record_install.assert_not_called()
        finally:
            globals_dict.update(original)


if __name__ == "__main__":
    unittest.main()
