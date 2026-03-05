import pytest
from app.tools.rag_tool import search_faq
from app.tools.order_tool import get_order_status, get_my_orders


def test_search_faq_returns_relevant_result():
    result = search_faq.invoke("환불 신청 방법")
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_order_status_found():
    result = get_order_status.invoke({
        "order_id": "ORD-001",
        "user_key": "kakao_user_1"
    })
    assert "배송중" in result


def test_get_order_status_not_found():
    result = get_order_status.invoke({
        "order_id": "ORD-999",
        "user_key": "kakao_user_1"
    })
    assert "찾을 수 없" in result


def test_get_my_orders_returns_list():
    result = get_my_orders.invoke("kakao_user_1")
    assert isinstance(result, str)
    assert "ORD-" in result


def test_get_my_orders_empty():
    result = get_my_orders.invoke("unknown_user_999")
    assert "없습니다" in result
