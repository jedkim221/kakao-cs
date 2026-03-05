import pytest
from app.agent import create_agent


def test_agent_answers_faq():
    agent = create_agent(user_key="kakao_user_1")
    result = agent.invoke({"input": "환불은 어떻게 신청하나요?"})
    assert isinstance(result["output"], str)
    assert len(result["output"]) > 10


def test_agent_handles_order_query():
    agent = create_agent(user_key="kakao_user_1")
    result = agent.invoke({"input": "ORD-001 주문 상태 알려줘"})
    assert "배송" in result["output"] or "ORD-001" in result["output"]


def test_agent_handles_unknown_query():
    agent = create_agent(user_key="kakao_user_1")
    result = agent.invoke({"input": "오늘 날씨 어때요?"})
    assert isinstance(result["output"], str)
