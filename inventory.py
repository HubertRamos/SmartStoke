"""Business rules for products and stock movements."""
from __future__ import annotations

from database import connect, initialize_database


class InventoryError(ValueError):
    """Raised when an inventory operation is invalid."""


class Inventory:
    def __init__(self, db_path=None):
        self.db_path = db_path
        initialize_database(db_path)

    def _connect(self):
        return connect(self.db_path)

    def list_products(self, search: str = ""):
        with self._connect() as db:
            term = f"%{search.strip()}%"
            return db.execute(
                "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY name",
                (term, term),
            ).fetchall()

    def get_product(self, product_id: int):
        with self._connect() as db:
            return db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    def add_product(self, name, category="", price=0, quantity=0, min_stock=0):
        name = str(name).strip()
        if not name:
            raise InventoryError("Informe o nome do produto.")
        price = self._number(price, "Preço")
        quantity = self._integer(quantity, "Quantidade")
        min_stock = self._integer(min_stock, "Estoque mínimo")
        if price < 0 or quantity < 0 or min_stock < 0:
            raise InventoryError("Os valores não podem ser negativos.")
        try:
            with self._connect() as db:
                cursor = db.execute(
                    "INSERT INTO products(name, category, price, quantity, min_stock) VALUES (?, ?, ?, ?, ?)",
                    (name, str(category).strip(), price, quantity, min_stock),
                )
                product_id = cursor.lastrowid
                if quantity:
                    db.execute(
                        "INSERT INTO movements(product_id, product_name, movement_type, quantity, note) VALUES (?, ?, 'entry', ?, 'Estoque inicial')",
                        (product_id, name, quantity),
                    )
                return product_id
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise InventoryError("Já existe um produto com esse nome.") from exc
            raise

    def update_product(self, product_id, name, category, price, min_stock):
        name = str(name).strip()
        if not name:
            raise InventoryError("Informe o nome do produto.")
        price = self._number(price, "Preço")
        min_stock = self._integer(min_stock, "Estoque mínimo")
        if price < 0 or min_stock < 0:
            raise InventoryError("Os valores não podem ser negativos.")
        try:
            with self._connect() as db:
                cursor = db.execute(
                    "UPDATE products SET name=?, category=?, price=?, min_stock=? WHERE id=?",
                    (name, str(category).strip(), price, min_stock, product_id),
                )
                if not cursor.rowcount:
                    raise InventoryError("Produto não encontrado.")
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise InventoryError("Já existe um produto com esse nome.") from exc
            raise

    def delete_product(self, product_id):
        with self._connect() as db:
            db.execute("DELETE FROM products WHERE id=?", (product_id,))

    def register_movement(self, product_id, movement_type, quantity, note=""):
        if movement_type not in ("entry", "exit"):
            raise InventoryError("Tipo de movimentação inválido.")
        quantity = self._integer(quantity, "Quantidade")
        if quantity <= 0:
            raise InventoryError("A quantidade deve ser maior que zero.")
        with self._connect() as db:
            product = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            if product is None:
                raise InventoryError("Produto não encontrado.")
            new_quantity = product["quantity"] + quantity if movement_type == "entry" else product["quantity"] - quantity
            if new_quantity < 0:
                raise InventoryError("Não há estoque suficiente para essa saída.")
            db.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))
            db.execute(
                "INSERT INTO movements(product_id, product_name, movement_type, quantity, note) VALUES (?, ?, ?, ?, ?)",
                (product_id, product["name"], movement_type, quantity, str(note).strip()),
            )

    def low_stock_products(self):
        with self._connect() as db:
            return db.execute(
                "SELECT * FROM products WHERE quantity <= min_stock ORDER BY quantity, name"
            ).fetchall()

    def list_movements(self, limit=200):
        with self._connect() as db:
            return db.execute(
                "SELECT * FROM movements ORDER BY datetime(created_at) DESC, id DESC LIMIT ?", (limit,)
            ).fetchall()

    def dashboard(self):
        with self._connect() as db:
            return db.execute(
                "SELECT COUNT(*) AS products, COALESCE(SUM(price * quantity), 0) AS stock_value, "
                "COALESCE(SUM(quantity), 0) AS units FROM products"
            ).fetchone()

    def best_sellers(self, limit=10):
        with self._connect() as db:
            return db.execute(
                "SELECT product_name, SUM(quantity) AS sold FROM movements "
                "WHERE movement_type='exit' GROUP BY product_name ORDER BY sold DESC, product_name LIMIT ?",
                (limit,),
            ).fetchall()

    @staticmethod
    def _number(value, label):
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError) as exc:
            raise InventoryError(f"{label} inválido.") from exc

    @staticmethod
    def _integer(value, label):
        try:
            number = float(str(value).replace(",", "."))
            if not number.is_integer():
                raise ValueError
            return int(number)
        except (TypeError, ValueError) as exc:
            raise InventoryError(f"{label} deve ser um número inteiro.") from exc
