import unittest

from profile_generator.errors import TemplateError
from profile_generator.template import placeholders, render


class TemplateTests(unittest.TestCase):
    def test_dotted_lookup(self):
        self.assertEqual(render("{{ a.b }} and {{c}}", {"a": {"b": 1}, "c": "x"}), "1 and x")

    def test_unknown_placeholder_raises(self):
        with self.assertRaises(TemplateError) as cm:
            render("{{ a.nope }}", {"a": {}})
        self.assertIn("a.nope", str(cm.exception))

    def test_comments_are_stripped_and_not_parsed(self):
        out = render("{# {{ ignored }} #}\nhi {{ x }}", {"x": 1})
        self.assertEqual(out, "hi 1")
        self.assertEqual(placeholders("{# {{ y }} #}{{ x }}"), ["x"])
