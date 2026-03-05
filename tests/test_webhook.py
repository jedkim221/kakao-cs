import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
import app.main as main_module

@pytest.fixture(autouse=True)
def clear_agent_cache():
    main_module._agent_cache.clear()
    yield
    main_module._agent_cache.clear()

client = TestClient(app)

KAKAO_PAYLOAD = {
    "userRequest": {
        "user": {"id": "kakao_user_1"},
        "utterance": "환불 방법 알려줘"
    }
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_returns_kakao_format():
    with patch("app.main.create_agent") as mock_agent_factory:
        mock_executor = MagicMock()
        mock_executor.invoke.return_value = {"output": "환불은 7일 이내 신청 가능합니다."}
        mock_agent_factory.return_value = mock_executor

        response = client.post("/webhook", json=KAKAO_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "2.0"
    assert "outputs" in body["template"]
    assert body["template"]["outputs"][0]["simpleText"]["text"] == "환불은 7일 이내 신청 가능합니다."


def test_webhook_missing_utterance_returns_422():
    response = client.post("/webhook", json={"userRequest": {"user": {"id": "u1"}}})
    assert response.status_code == 422
