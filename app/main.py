from fastapi import FastAPI
from app.schemas import KakaoRequest
from app.agent import create_agent

app = FastAPI(title="Kakao CS Chatbot")

# Per-user agent cache (holds conversation memory across turns)
_agent_cache: dict = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def kakao_webhook(request: KakaoRequest):
    user_key = request.userRequest.user.id
    utterance = request.userRequest.utterance

    if user_key not in _agent_cache:
        _agent_cache[user_key] = create_agent(user_key=user_key)

    agent = _agent_cache[user_key]
    result = agent.invoke({"input": utterance})
    answer = result.get("output", "죄송합니다, 잠시 후 다시 시도해주세요.")

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": answer}}]
        }
    }
