"""SQLite persistence for SmartStoke."""
from __future__ import annotations

import sqlite3
from pathlib import Path


APP_DIR = Path.home() / ".smartstoke"
DEFAULT_DB = APP_DIR / "smartstoke.db"


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: str | Path | None = None) -> None:
    with connect(db_path) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                category TEXT NOT NULL DEFAULT '',
                price REAL NOT NULL DEFAULT 0 CHECK(price >= 0),
                quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
                min_stock INTEGER NOT NULL DEFAULT 0 CHECK(min_stock >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                movement_type TEXT NOT NULL CHECK(movement_type IN ('entry', 'exit')),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
            );
            CREATE INDEX IF NOT EXISTS idx_movements_type ON movements(movement_type);
            CREATE INDEX IF NOT EXISTS idx_movements_date ON movements(created_at);
            """
        )
