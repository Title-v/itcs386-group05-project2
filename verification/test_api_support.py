"""Offline checks of the test harness; these are NOT assignment API cases."""

import importlib.util
from pathlib import Path
import unittest


SUPPORT_PATH = Path(__file__).parents[1] / "API testing" / "shop_support.py"
SPEC = importlib.util.spec_from_file_location("shop_support", SUPPORT_PATH)
support = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(support)


class OwnershipChecks(unittest.TestCase):
    def setUp(self):
        self.run_id = "a123456789abcdef"
        self.name = "G05-a123456789abcdef-case123"
        self.product = {
            "id": 123,
            "name": self.name,
            "meta_data": [{"key": "itcs386_test_run", "value": self.run_id}],
        }

    def test_accepts_exact_product_created_by_this_run(self):
        self.assertTrue(support.is_owned_product(self.product, self.name, self.run_id))

    def test_rejects_a_product_from_another_run(self):
        self.assertFalse(support.is_owned_product(self.product, self.name, "another-run"))

    def test_rejects_a_different_product_name(self):
        self.assertFalse(support.is_owned_product(self.product, self.name + "-other", self.run_id))

    def test_rejects_other_group_even_with_matching_metadata(self):
        self.product["name"] = "G06-a123456789abcdef-case123"
        self.assertFalse(support.is_owned_product(self.product, self.product["name"], self.run_id))

    def test_rejects_a_boolean_product_id(self):
        self.product["id"] = True
        self.assertFalse(support.is_owned_product(self.product, self.name, self.run_id))

    def test_rejects_missing_run_metadata(self):
        self.product["meta_data"] = []
        self.assertFalse(support.is_owned_product(self.product, self.name, self.run_id))

    def test_an_ambiguous_post_is_not_declared_clean_after_one_empty_lookup(self):
        class EmptyResponse:
            status_code = 200

            def json(self):
                return []

        class InterruptedAPI:
            def admin(self, method, path, **kwargs):
                if method == "POST":
                    raise support.requests.Timeout("simulated interrupted response")
                return EmptyResponse()

        factory = support.ProductFactory(InterruptedAPI(), self.run_id)
        with self.assertRaises(support.requests.Timeout):
            factory.submit(factory.payload())
        with self.assertRaisesRegex(AssertionError, "unknown"):
            factory.cleanup()


if __name__ == "__main__":
    unittest.main()
