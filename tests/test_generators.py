import unittest
from datetime import datetime

from faker import Faker

from ecommerce_data_generator.category import generate_category
from ecommerce_data_generator.products import generate_products
from ecommerce_data_generator.promotion_product import generate_promotion_products


class ProductTests(unittest.TestCase):
    def test_missing_sources_suggest_generator(self):
        # Missing or too-recent sources should suggest the correct generator.
        valid = [(1, datetime(2024, 1, 1))]
        for index, (name, command) in enumerate(
            (
                ("level-2 categories", "generate-categories"),
                ("brands", "generate-brands"),
                ("sellers", "generate-sellers"),
            )
        ):
            for missing in ([], [(1, datetime(2025, 1, 1))]):
                with self.subTest(source=name, rows=missing):
                    sources = [valid, valid, valid]
                    sources[index] = missing
                    with self.assertRaises(ValueError) as error:
                        generate_products(1, *sources)
                    self.assertEqual(
                        str(error.exception),
                        f"No eligible {name}. Run 'uv run {command}' first.",
                    )

    def test_products_reference_sources_without_predating_them(self):
        # Products should use the supplied IDs and not predate their sources.
        created_at = datetime(2024, 12, 1, 12, 0, 0, 123456)
        products = generate_products(
            3, [(10, created_at)], [(20, created_at)], [(30, created_at)]
        )
        self.assertEqual(len(products), 3)
        for product in products:
            self.assertEqual(product["category_id"], 10)
            self.assertEqual(product["brand_id"], 20)
            self.assertEqual(product["seller_id"], 30)
            self.assertGreaterEqual(product["created_at"], created_at)


class PromotionProductTests(unittest.TestCase):
    def test_missing_sources_suggest_generator(self):
        # Missing or too-recent promotions/products should suggest a generator.
        valid = [(1, datetime(2024, 1, 1))]
        for index, name in enumerate(("promotions", "products")):
            for missing in ([], [(1, datetime(2025, 6, 1))]):
                with self.subTest(source=name, rows=missing):
                    sources = [valid, valid]
                    sources[index] = missing
                    with self.assertRaises(ValueError) as error:
                        generate_promotion_products(1, *sources)
                    self.assertEqual(
                        str(error.exception),
                        f"No eligible {name}. Run 'uv run generate-{name}' first.",
                    )

    def test_insufficient_pairs_report_capacity(self):
        # Requesting too many links should report the available pair count.
        source = [(1, datetime(2024, 1, 1))]
        with self.assertRaises(ValueError) as error:
            generate_promotion_products(2, source, source)
        self.assertEqual(
            str(error.exception),
            "Only 1 distinct pairs available. "
            "Reduce '--count' or generate more promotions/products.",
        )

    def test_generated_pairs_are_unique_and_respect_source_dates(self):
        # Links should cover distinct pairs without predating either source.
        created_at = datetime(2025, 5, 1, 12, 0, 0, 123456)
        promotions = [(10, created_at), (20, created_at)]
        products = [(30, created_at), (40, created_at)]
        links = generate_promotion_products(4, promotions, products)
        pairs = {(link["promotion_id"], link["product_id"]) for link in links}
        self.assertEqual(len(links), 4)
        self.assertEqual(pairs, {(10, 30), (10, 40), (20, 30), (20, 40)})
        for link in links:
            self.assertGreaterEqual(link["created_at"], created_at)


class CategoryTests(unittest.TestCase):
    def test_child_cannot_predate_parent(self):
        # A child should reference its parent and be created no earlier than it.
        parent_created_at = datetime(2024, 12, 31, 23, 59, 58, 999999)
        child = generate_category("Child", 1, Faker(), parent_created_at)
        self.assertEqual(child["parent_category_id"], 1)
        self.assertEqual(child["level"], 2)
        self.assertGreaterEqual(child["created_at"], parent_created_at)

    def test_parent_after_generation_window_is_rejected(self):
        # A parent created after 2024 should prevent generating a child in 2024.
        with self.assertRaisesRegex(ValueError, "2024 generation window"):
            generate_category("Child", 1, Faker(), datetime(2025, 1, 1))


if __name__ == "__main__":
    unittest.main()
