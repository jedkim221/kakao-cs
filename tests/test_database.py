import pytest
from app.database import init_db, get_order, seed_sample_orders, get_orders_by_user


def test_get_order_returns_order():
    init_db(":memory:")
    seed_sample_orders(":memory:")
    order = get_order("ORD-001", "kakao_user_1", db_path=":memory:")
    assert order is not None
    assert order["status"] == "배송중"


def test_get_order_wrong_user_returns_none():
    init_db(":memory:")
    seed_sample_orders(":memory:")
    order = get_order("ORD-001", "kakao_user_999", db_path=":memory:")
    assert order is None


def test_get_order_not_found_returns_none():
    init_db(":memory:")
    order = get_order("ORD-999", "kakao_user_1", db_path=":memory:")
    assert order is None
