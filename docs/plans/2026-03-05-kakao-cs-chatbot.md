# 카카오톡 CS 챗봇 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 쇼핑몰 카카오톡 CS 자동화 챗봇 - 주문 조회, 상품 문의, 정책 FAQ를 로컬 LLM(Ollama)과 RAG(ChromaDB)로 처리

**Architecture:** FastAPI webhook 서버가 카카오 i 오픈빌더 요청을 받아 LangChain Agent에 전달. Agent는 RAG Tool(ChromaDB)과 DB Tool(주문 DB)을 선택적으로 호출한 뒤 Ollama LLM으로 응답 생성.

**Tech Stack:** Python 3.11+, FastAPI, LangChain, ChromaDB, Ollama (EXAONE 3.5 7.8B + nomic-embed-text), SQLite, pytest, ngrok

---

## Task 1: 프로젝트 환경 세팅

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `app/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Python 가상환경 및 의존성 파일 생성**

```bash
cd /Users/jed/home/dev/kakao-cs
python3 -m venv .venv
source .venv/bin/activate
```

`requirements.txt` 내용:
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
langchain==0.3.0
langchain-community==0.3.0
langchain-ollama==0.2.0
chromadb==0.5.20
sqlalchemy==2.0.36
pydantic==2.9.0
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.0
python-dotenv==1.0.1
```

```bash
pip install -r requirements.txt
```

**Step 2: 디렉토리 구조 생성**

```bash
mkdir -p app/tools tests data/faq data/products docs/plans chroma_db
touch app/__init__.py app/tools/__init__.py tests/__init__.py
```

**Step 3: .gitignore 생성**

`.gitignore` 내용:
```
.venv/
__pycache__/
*.pyc
chroma_db/
.env
*.db
```

**Step 4: git 초기화 및 첫 커밋**

```bash
git init
git add .
git commit -m "chore: initial project setup"
```

---

## Task 2: Ollama 설치 및 모델 준비

**Step 1: Ollama 설치**

```bash
brew install ollama
```

**Step 2: Ollama 서비스 시작**

```bash
ollama serve &
```

**Step 3: LLM 모델 다운로드**

```bash
ollama pull exaone3.5:7.8b
```

> 약 5GB. 다운로드 완료까지 대기.

**Step 4: 임베딩 모델 다운로드**

```bash
ollama pull nomic-embed-text
```

**Step 5: 모델 동작 확인**

```bash
ollama run exaone3.5:7.8b "안녕하세요, 테스트입니다."
```

Expected: 한국어 응답 출력

**Step 6: 커밋**

```bash
git commit -m "chore: ollama setup with exaone3.5 and nomic-embed-text" --allow-empty
```

---

## Task 3: CS 데이터 파일 작성

**Files:**
- Create: `data/faq/policy.md`
- Create: `data/faq/shipping.md`
- Create: `data/products/sample.md`

**Step 1: 환불/정책 FAQ 작성**

`data/faq/policy.md` 내용:
```markdown
# 환불 및 교환 정책

Q: 환불은 어떻게 신청하나요?
A: 상품 수령 후 7일 이내에 고객센터로 문의하시면 환불 처리가 가능합니다. 단, 상품에 하자가 없는 경우 배송비는 고객 부담입니다.

Q: 교환은 언제까지 가능한가요?
A: 상품 수령 후 7일 이내에 교환 신청이 가능합니다. 상품 불량/오배송의 경우 30일 이내 무료 교환됩니다.

Q: 고객센터 운영 시간은 어떻게 되나요?
A: 평일 오전 9시 ~ 오후 6시 운영합니다. 주말 및 공휴일은 휴무입니다.

Q: 부분 환불이 가능한가요?
A: 네, 여러 상품을 주문하신 경우 일부 상품만 환불하실 수 있습니다.
```

**Step 2: 배송 안내 FAQ 작성**

`data/faq/shipping.md` 내용:
```markdown
# 배송 안내

Q: 배송은 얼마나 걸리나요?
A: 결제 완료 후 영업일 기준 1-2일 이내 출고되며, 출고 후 1-3일 이내 배송됩니다.

Q: 배송비는 얼마인가요?
A: 3만원 이상 구매 시 무료배송입니다. 3만원 미만은 3,000원의 배송비가 부과됩니다.

Q: 배송이 너무 늦어지고 있어요.
A: 주문번호를 알려주시면 현재 배송 상태를 바로 확인해드리겠습니다. 물류사 사정으로 인해 1-2일 지연될 수 있습니다.

Q: 제주도나 도서산간 지역도 배송되나요?
A: 가능하지만 추가 배송비(3,000원~5,000원)가 부과되며 1-2일 추가 소요됩니다.
```

**Step 3: 샘플 상품 정보 작성**

`data/products/sample.md` 내용:
```markdown
# 오버핏 코튼 티셔츠

- 소재: 면 100%
- 사이즈: S, M, L, XL
- 사이즈 가이드:
  - S: 어깨 44cm, 가슴 96cm, 총장 68cm
  - M: 어깨 46cm, 가슴 100cm, 총장 70cm
  - L: 어깨 48cm, 가슴 104cm, 총장 72cm
  - XL: 어깨 50cm, 가슴 108cm, 총장 74cm
- 색상: 화이트, 블랙, 그레이, 네이비
- 세탁: 손세탁 권장, 30도 이하 물 사용
- 재고: S(있음), M(있음), L(품절), XL(있음)
```

**Step 4: 커밋**

```bash
git add data/
git commit -m "feat: add initial CS data (faq, product info)"
```

---

## Task 4: ChromaDB 임베딩 파이프라인

**Files:**
- Create: `app/ingest.py`
- Create: `tests/test_ingest.py`

**Step 1: 테스트 먼저 작성**

`tests/test_ingest.py` 내용:
```python
import pytest
from app.ingest import load_documents, create_vectorstore

def test_load_documents_returns_nonempty_list():
    docs = load_documents("data/")
    assert len(docs) > 0

def test_load_documents_have_content():
    docs = load_documents("data/")
    for doc in docs:
        assert len(doc.page_content) > 0

def test_create_vectorstore_and_search():
    docs = load_documents("data/")
    vectorstore = create_vectorstore(docs, collection_name="test_collection")
    results = vectorstore.similarity_search("환불 방법", k=2)
    assert len(results) > 0
    assert "환불" in results[0].page_content
```

**Step 2: 테스트 실패 확인**

```bash
pytest tests/test_ingest.py -v
```

Expected: FAIL - `ModuleNotFoundError`

**Step 3: ingest.py 구현**

`app/ingest.py` 내용:
```python
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma_db"
EMBED_MODEL = "nomic-embed-text"


def load_documents(data_dir: str):
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "Q:", "A:"],
    )
    return splitter.split_documents(documents)


def create_vectorstore(docs, collection_name: str = "cs_knowledge"):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_PATH,
    )
    return vectorstore


def get_vectorstore(collection_name: str = "cs_knowledge"):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )


if __name__ == "__main__":
    docs = load_documents("data/")
    print(f"Loaded {len(docs)} chunks")
    create_vectorstore(docs)
    print("Vectorstore created successfully.")
```

**Step 4: 테스트 통과 확인**

```bash
pytest tests/test_ingest.py -v
```

Expected: PASS (3 tests)

**Step 5: 실제 데이터 임베딩 실행**

```bash
python -m app.ingest
```

Expected: `Loaded N chunks` 출력 후 `Vectorstore created successfully.`

**Step 6: 커밋**

```bash
git add app/ingest.py tests/test_ingest.py
git commit -m "feat: add document ingest pipeline with ChromaDB"
```

---

## Task 5: 주문 DB 세팅

**Files:**
- Create: `app/database.py`
- Create: `tests/test_database.py`

**Step 1: 테스트 작성**

`tests/test_database.py` 내용:
```python
import pytest
from app.database import init_db, get_order, seed_sample_orders

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
```

**Step 2: 테스트 실패 확인**

```bash
pytest tests/test_database.py -v
```

Expected: FAIL

**Step 3: database.py 구현**

`app/database.py` 내용:
```python
import sqlite3
from typing import Optional

DB_PATH = "orders.db"


def get_conn(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH):
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
    conn.close()


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
    conn.close()


def get_order(order_id: str, user_key: str, db_path: str = DB_PATH) -> Optional[dict]:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ? AND user_key = ?",
        (order_id, user_key),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_orders_by_user(user_key: str, db_path: str = DB_PATH) -> list[dict]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_key = ? ORDER BY created_at DESC LIMIT 5",
        (user_key,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

**Step 4: 테스트 통과 확인**

```bash
pytest tests/test_database.py -v
```

Expected: PASS (3 tests)

**Step 5: 샘플 DB 초기화**

```bash
python -c "from app.database import init_db, seed_sample_orders; init_db(); seed_sample_orders(); print('DB ready')"
```

**Step 6: 커밋**

```bash
git add app/database.py tests/test_database.py
git commit -m "feat: add order database with sample data"
```

---

## Task 6: LangChain Tools 구현

**Files:**
- Create: `app/tools/rag_tool.py`
- Create: `app/tools/order_tool.py`
- Create: `tests/test_tools.py`

**Step 1: 테스트 작성**

`tests/test_tools.py` 내용:
```python
import pytest
from app.tools.rag_tool import search_faq
from app.tools.order_tool import get_order_status

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
```

**Step 2: 테스트 실패 확인**

```bash
pytest tests/test_tools.py -v
```

Expected: FAIL

**Step 3: RAG Tool 구현**

`app/tools/rag_tool.py` 내용:
```python
from langchain_core.tools import tool
from app.ingest import get_vectorstore


@tool
def search_faq(query: str) -> str:
    """FAQ, 정책, 상품 정보를 검색합니다. 배송, 환불, 교환, 상품 사이즈 등의 질문에 사용하세요."""
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=3)
    if not docs:
        return "관련 정보를 찾지 못했습니다."
    return "\n\n".join(doc.page_content for doc in docs)
```

**Step 4: Order Tool 구현**

`app/tools/order_tool.py` 내용:
```python
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
```

**Step 5: 테스트 통과 확인**

```bash
pytest tests/test_tools.py -v
```

Expected: PASS (3 tests)

**Step 6: 커밋**

```bash
git add app/tools/ tests/test_tools.py
git commit -m "feat: add RAG and order tools for LangChain agent"
```

---

## Task 7: LangChain Agent 구현

**Files:**
- Create: `app/agent.py`
- Create: `tests/test_agent.py`

**Step 1: 테스트 작성**

`tests/test_agent.py` 내용:
```python
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
```

**Step 2: 테스트 실패 확인**

```bash
pytest tests/test_agent.py -v
```

Expected: FAIL

**Step 3: agent.py 구현**

`app/agent.py` 내용:
```python
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from app.tools.rag_tool import search_faq
from app.tools.order_tool import get_order_status, get_my_orders

LLM_MODEL = "exaone3.5:7.8b"

SYSTEM_PROMPT = """당신은 쇼핑몰 CS 상담 챗봇입니다. 친절하고 간결하게 답변하세요.

사용 가능한 도구:
{tools}

도구 이름 목록: {tool_names}

반드시 다음 형식을 따르세요:
Question: 답해야 할 질문
Thought: 어떤 도구를 사용할지 생각
Action: 사용할 도구 이름
Action Input: 도구에 전달할 입력
Observation: 도구 결과
... (필요시 반복)
Thought: 이제 답변할 수 있습니다
Final Answer: 최종 답변 (친절한 한국어로)

대화 이력:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""


def create_agent(user_key: str) -> AgentExecutor:
    llm = ChatOllama(model=LLM_MODEL, temperature=0.3)

    tools = [search_faq, get_order_status, get_my_orders]

    # order tools에 user_key를 자동 주입하는 wrapper
    from langchain_core.tools import tool

    @tool
    def get_order_status_authed(order_id: str) -> str:
        """주문번호로 배송 상태를 조회합니다. 주문번호만 입력하세요."""
        return get_order_status.invoke({"order_id": order_id, "user_key": user_key})

    @tool
    def get_my_orders_authed(dummy: str = "") -> str:
        """내 최근 주문 목록을 조회합니다."""
        return get_my_orders.invoke(user_key)

    authed_tools = [search_faq, get_order_status_authed, get_my_orders_authed]

    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", input_key="input")

    agent = create_react_agent(llm, authed_tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=authed_tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )
```

**Step 4: 테스트 통과 확인**

```bash
pytest tests/test_agent.py -v
```

Expected: PASS (3 tests) - LLM 호출이 포함되어 시간이 걸릴 수 있음

**Step 5: 커밋**

```bash
git add app/agent.py tests/test_agent.py
git commit -m "feat: add LangChain ReAct agent with memory"
```

---

## Task 8: FastAPI Webhook 서버 구현

**Files:**
- Create: `app/main.py`
- Create: `app/schemas.py`
- Create: `tests/test_webhook.py`

**Step 1: 테스트 작성**

`tests/test_webhook.py` 내용:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

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

def test_webhook_missing_utterance_returns_400():
    response = client.post("/webhook", json={"userRequest": {"user": {"id": "u1"}}})
    assert response.status_code == 422
```

**Step 2: 테스트 실패 확인**

```bash
pytest tests/test_webhook.py -v
```

Expected: FAIL

**Step 3: schemas.py 구현**

`app/schemas.py` 내용:
```python
from pydantic import BaseModel

class KakaoUser(BaseModel):
    id: str

class KakaoUserRequest(BaseModel):
    user: KakaoUser
    utterance: str

class KakaoRequest(BaseModel):
    userRequest: KakaoUserRequest
```

**Step 4: main.py 구현**

`app/main.py` 내용:
```python
from fastapi import FastAPI
from app.schemas import KakaoRequest
from app.agent import create_agent

app = FastAPI(title="Kakao CS Chatbot")

# 간단한 user_key별 agent 캐시 (프로덕션에서는 Redis 등으로 교체)
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
```

**Step 5: 테스트 통과 확인**

```bash
pytest tests/test_webhook.py -v
```

Expected: PASS (3 tests)

**Step 6: 커밋**

```bash
git add app/main.py app/schemas.py tests/test_webhook.py
git commit -m "feat: add FastAPI webhook server for kakao i openbuilder"
```

---

## Task 9: 로컬 실행 및 ngrok 연동

**Step 1: 전체 테스트 통과 확인**

```bash
pytest -v
```

Expected: 전체 PASS

**Step 2: 서버 실행**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Step 3: 로컬 동작 테스트**

새 터미널에서:
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"userRequest": {"user": {"id": "test_user"}, "utterance": "환불 방법 알려줘"}}'
```

Expected: `{"version":"2.0","template":{"outputs":[{"simpleText":{"text":"..."}}]}}`

**Step 4: ngrok 설치 및 터널 오픈**

```bash
brew install ngrok
ngrok http 8000
```

출력된 `https://xxxx.ngrok-free.app` URL 복사

**Step 5: 카카오 i 오픈빌더 webhook 등록**

1. https://i.kakao.com 접속 → 챗봇 생성
2. 스킬 관리 → 스킬 추가 → URL: `https://xxxx.ngrok-free.app/webhook`
3. 시나리오 → 폴백 블록에 스킬 연결
4. 배포 후 카카오톡에서 테스트

**Step 6: 최종 커밋**

```bash
git add .
git commit -m "docs: add ngrok and openbuilder setup instructions"
```

---

## 전체 테스트 실행 명령

```bash
pytest -v --tb=short
```

## 빠른 시작 요약

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. Ollama 모델 준비
ollama pull exaone3.5:7.8b && ollama pull nomic-embed-text

# 3. 데이터 임베딩
python -m app.ingest

# 4. DB 초기화
python -c "from app.database import init_db, seed_sample_orders; init_db(); seed_sample_orders()"

# 5. 서버 실행
uvicorn app.main:app --port 8000
```
