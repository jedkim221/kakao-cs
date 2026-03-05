from langchain_core.tools import tool
from app.database import get_order, get_orders_by_user


@tool
def get_order_status(order_id: str, user_key: str) -> str:
    """특정 주문번호의 배송 상태를 조회합니다. 주문번호와 사용자 ID가 필요합니다."""
    order = get_order(order_id, user_key)
    if not order:
        return f"주문번호 {order_id}를 찾을 수 없거나 본인 주문이 아닙니다."
    tracking = f"\n송장번호: {order['tracking_number']}" if order['tracking_number'] else ""
    return (
        f"주문번호: {order['id']}\n"
        f"상품: {order['product_name']}\n"
        f"상태: {order['status']}\n"
        f"주문일: {order['created_at']}"
        f"{tracking}"
    )


@tool
def get_my_orders(user_key: str) -> str:
    """사용자의 최근 주문 목록을 조회합니다."""
    orders = get_orders_by_user(user_key)
    if not orders:
        return "최근 주문 내역이 없습니다."
    lines = []
    for o in orders:
        lines.append(f"- [{o['id']}] {o['product_name']} : {o['status']} ({o['created_at']})")
    return "\n".join(lines)
