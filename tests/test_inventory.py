import tempfile
import unittest
from pathlib import Path

from inventory import Inventory, InventoryError


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.inventory = Inventory(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_product_and_dashboard(self):
        self.inventory.add_product("Café", "Alimentos", "12,50", 8, 2)
        summary = self.inventory.dashboard()
        self.assertEqual(summary["products"], 1)
        self.assertEqual(summary["units"], 8)
        self.assertAlmostEqual(summary["stock_value"], 100)

    def test_initial_stock_is_recorded_as_entry(self):
        self.inventory.add_product("Arroz", quantity=5)
        movements = self.inventory.list_movements()
        self.assertEqual(movements[0]["movement_type"], "entry")
        self.assertEqual(movements[0]["quantity"], 5)

    def test_exit_updates_stock_and_best_sellers(self):
        product_id = self.inventory.add_product("Suco", quantity=10)
        self.inventory.register_movement(product_id, "exit", 3)
        self.assertEqual(self.inventory.get_product(product_id)["quantity"], 7)
        self.assertEqual(self.inventory.best_sellers()[0]["sold"], 3)

    def test_cannot_exit_more_than_available(self):
        product_id = self.inventory.add_product("Leite", quantity=2)
        with self.assertRaises(InventoryError):
            self.inventory.register_movement(product_id, "exit", 3)
        self.assertEqual(self.inventory.get_product(product_id)["quantity"], 2)

    def test_low_stock(self):
        self.inventory.add_product("Farinha", quantity=2, min_stock=2)
        self.assertEqual(len(self.inventory.low_stock_products()), 1)

    def test_duplicate_name_is_rejected(self):
        self.inventory.add_product("Feijão")
        with self.assertRaises(InventoryError):
            self.inventory.add_product("feijão")

    def test_history_survives_product_deletion(self):
        product_id = self.inventory.add_product("Biscoito", quantity=4)
        self.inventory.delete_product(product_id)
        movement = self.inventory.list_movements()[0]
        self.assertEqual(movement["product_name"], "Biscoito")
        self.assertIsNone(movement["product_id"])


if __name__ == "__main__":
    unittest.main()
