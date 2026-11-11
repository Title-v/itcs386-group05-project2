"""Offline checks of the source-to-example transformation. No network/test execution."""
import ast
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


class CaseExampleTests(unittest.TestCase):
    def builder(self):
        path = HERE / "case_examples.py"
        self.assertTrue(path.exists(), "The case-example generator must exist")
        spec = importlib.util.spec_from_file_location("case_examples", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.build_example

    def generate(self, text, values):
        tree = ast.parse(text)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
        return self.builder()(tree, fn, values, "S01-01")

    def test_bind_known_inputs_and_keep_only_selected_branches(self):
        code = self.generate("def test_case(api, products, value):\n    if value == 0:\n        assert api.status == 400\n    else:\n        assert api.status == 200\n", {"value": 0})
        self.assertIn("assert api.status == 400", code)
        self.assertNotIn("== 200", code)
        self.assertNotIn("if value", code)
        self.assertIn("def example_s01_01(api, products):", code)

    def test_return_cuts_unreachable_tail_but_runtime_if_is_preserved(self):
        code = self.generate("def test_case(api, products, value):\n    if value == 0:\n        assert api.status == 400\n        return\n    assert api.status == 200\n", {"value": 0})
        self.assertNotIn("== 200", code)
        runtime = self.generate("def test_case(api, products, value):\n    if api.ready:\n        return\n    assert value == 10\n", {"value": 10})
        self.assertIn("if api.ready", runtime)
        self.assertIn("assert 10 == 10", runtime)

    def test_conditional_expression_and_only_used_imports(self):
        code = self.generate("from decimal import Decimal\nimport pytest\ndef test_case(api, products, status):\n    result = products.create('publish' if status == 'publish' else 'draft')\n    assert Decimal(result['price']) == Decimal('100.00')\n", {"status": "draft"})
        self.assertIn("products.create('draft')", code)
        self.assertIn("from decimal import Decimal", code)
        self.assertNotIn("import pytest", code)
        compile(code, "case-example", "exec")

    def test_bound_parameters_are_never_reassigned_silently(self):
        with self.assertRaisesRegex(ValueError, "reassigned"):
            self.generate("def test_case(api, products, value):\n    value = 20\n    assert value == 20\n", {"value": 10})

    def test_all_real_examples_compile_and_bind_every_case_parameter(self):
        model = json.loads((HERE / "map-model.json").read_text())
        cases = [n for n in model["nodes"] if n["kind"] == "case"]
        self.assertEqual(len(cases), 15)
        for case in cases:
            self.assertIn("exampleCode", case, case["id"])
            code = case["exampleCode"]["code"]
            compile(code, case["id"], "exec")  # Syntax check only: not exec().
            tree = ast.parse(code)
            loaded = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            self.assertFalse(loaded & set(case["input"]), case["id"])


if __name__ == "__main__":
    unittest.main()
