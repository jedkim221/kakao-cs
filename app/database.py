import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = str(Path(__file__).parent.parent / "orders.db")
MAX_ORDERS_PER_QUERY = 5

_memory_conn = None


def get_conn(db_path: str = DB_PATH):
    global _memory_conn
    if db_path == ":memory:":
        if _memory_conn is None:
            _memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            _memory_conn.row_factory = sqlite3.Row
        return _memory_conn
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH):
    global _memory_conn
    if db_path == ":memory:":
        _memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
        _memory_conn.row_factory = sqlite3.Row
    conn = get_conn(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_key TEXT NOT NULL,
            product_name TEXT NOT NULL,
            status TEXT NOT NULL,
            tracking_number TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()


def seed_sample_orders(db_path: str = DB_PATH):
    conn = get_conn(db_path)
    conn.executemany(
        "INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?)",
        [
            ("ORD-001", "kakao_user_1", "오버핏 코튼 티셔츠 M/블랙", "배송중", "CJ123456789", "2026-03-03"),
            ("ORD-002", "kakao_user_1", "오버핏 코튼 티셔츠 S/화이트", "배송완료", "CJ987654321", "2026-02-28"),
            ("ORD-003", "kakao_user_2", "오버핏 코튼 티셔츠 XL/그레이", "결제완료", None, "2026-03-04"),
        ],
    )
    conn.commit()


def get_order(order_id: str, user_key: str, db_path: str = DB_PATH) -> Optional[dict]:
    conn = get_conn(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM orders WHERE id = ? AND user_key = ?",
            (order_id, user_key),
        ).fetchone()
        return dict(row) if row else None
    finally:
        if db_path != ":memory:":
            conn.close()


def get_orders_by_user(user_key: str, db_path: str = DB_PATH) -> list[dict]:
    conn = get_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_key = ? ORDER BY created_at DESC LIMIT ?",
            (user_key, MAX_ORDERS_PER_QUERY),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if db_path != ":memory:":
            conn.close()
