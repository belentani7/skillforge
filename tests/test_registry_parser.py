"""RED tests for engine.registry._parse_simple_yaml nesting.

The universal skill format documented in README.md keeps `prompt`,
`examples` and `constraints` inside the `content:` mapping, and every
converter in engine/converters.py reads them from `skill["content"]`.
The parser must therefore preserve that nesting.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.registry import _parse_simple_yaml, validate_skill_yaml  # noqa: E402

TEMPLATE = ROOT / "templates" / "basic.skill"


class TestSkillYamlNesting(unittest.TestCase):
    def setUp(self):
        self.data = _parse_simple_yaml(TEMPLATE.read_text(encoding="utf-8"))

    def test_publish_accepts_the_template_that_init_generates(self):
        self.assertEqual(validate_skill_yaml(TEMPLATE), [])

    def test_prompt_stays_inside_content(self):
        content = self.data.get("content")
        self.assertIsInstance(content, dict, "content must be a mapping")
        prompt = content.get("prompt")
        self.assertIsInstance(prompt, str)
        self.assertIn("expert software engineer", prompt)

    def test_constraints_stay_inside_content(self):
        content = self.data.get("content")
        self.assertIsInstance(content, dict)
        constraints = content.get("constraints")
        self.assertIsInstance(constraints, list)
        self.assertEqual(len(constraints), 3)

    def test_examples_stay_inside_content(self):
        content = self.data.get("content")
        self.assertIsInstance(content, dict)
        examples = content.get("examples")
        self.assertIsInstance(examples, list)
        self.assertEqual(len(examples), 1)
        for example in examples:
            self.assertIsInstance(example, dict)
            self.assertIn("input", example)
            self.assertIn("output", example)


if __name__ == "__main__":
    unittest.main()
