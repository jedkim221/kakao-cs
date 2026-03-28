# 카카오톡 CS 챗봇 시스템 설계

## 개요

쇼핑몰 고객 응대 자동화를 위한 카카오톡 CS 챗봇.
로컬 LLM(Ollama)과 벡터 DB(ChromaDB)를 활용한 RAG 기반 시스템.

- 처리 문의 유형: 주문 상태 조회, 상품 문의, 정책/FAQ 안내
- 환경: Mac M5 32GB, 로컬 실행

---

## 전체 아키텍처

```
카카오톡 사용자
      ↓ 메시지
카카오 i 오픈빌더
      ↓ webhook (HTTP POST)
FastAPI 서버 (로컬 or 내부망)
      ↓
LangChain Agent
   ├─ RAG Tool → ChromaDB (상품 문의 / 정책 FAQ)
   ├─ DB Tool  → 주문 DB (실시간 주문 조회)
   └─ LLM      → Ollama (응답 생성)
```

**핵심 흐름:**
1. 사용자가 카카오톡 채널에 메시지 전송
2. 카카오 i 오픈빌더가 FastAPI webhook으로 전달
3. LangChain Agent가 의도 파악 후 적절한 Tool 선택
4. Ollama LLM이 검색 결과 기반으로 자연스러운 답변 생성
5. FastAPI가 카카오 오픈빌더 응답 포맷으로 반환

**LLM 모델:** `EXAONE 3.5 7.8B` (한국어 특화, LG AI Research)
**대안 모델:** `Qwen2.5 7B`

---

## 데이터 구성 및 RAG 파이프라인

### CS 데이터 구조

```
data/
├── faq/
│   ├── policy.md        # 환불/교환 정책, 운영시간 등
│   └── shipping.md      # 배송 안내, 지연 처리 등
└── products/
    └── {상품명}.md      # 상품별 사이즈, 소재, 재고 안내
```

### RAG 파이프라인

```
Markdown 문서
    ↓ 청크 분할 (RecursiveCharacterTextSplitter)
    ↓ 임베딩 생성 (nomic-embed-text via Ollama)
ChromaDB 저장
    ↓ 사용자 질문 → 임베딩 → 유사도 검색 (top-k 3~5개)
LangChain에 컨텍스트로 전달
```

- **임베딩 모델:** `nomic-embed-text` (Ollama, 로컬 실행, 한국어 지원)
- **청크 크기:** 500 토큰, 오버랩 50 토큰
- FAQ는 Q&A 단위로 분리하여 검색 정확도 향상

---

## 주문 DB 연동 및 LangChain Agent

### 주문 DB 스키마 (예시)

```
orders: id, user_id, status, product_name, created_at, tracking_number
```

### LangChain Tool 구성

```python
Agent (ReAct 방식)
├── Tool 1: search_faq       → ChromaDB RAG
├── Tool 2: get_order_status → 주문 DB 조회
└── Tool 3: escalate         → 상담원 연결 안내
```

- 카카오톡 `user_key`를 활용해 본인 주문만 조회 가능하도록 인증
- 복잡하거나 감정적인 문의는 `escalate` Tool로 상담원 연결 안내
- 대화 맥락 유지: `ConversationBufferWindowMemory` (최근 5턴)

---

## FastAPI 서버 및 카카오 오픈빌더 연동

### 프로젝트 구조

```
app/
├── main.py              # FastAPI 앱, webhook 엔드포인트
├── agent.py             # LangChain Agent 초기화
├── tools/
│   ├── rag_tool.py      # ChromaDB 검색 Tool
│   └── order_tool.py    # 주문 DB 조회 Tool
├── ingest.py            # 문서 → ChromaDB 임베딩 스크립트
└── data/                # FAQ, 상품 문서
```

### Webhook 엔드포인트

```python
@app.post("/webhook")
async def kakao_webhook(request: KakaoRequest):
    user_key = request.userRequest.user.id
    utterance = request.userRequest.utterance

    response = await agent.ainvoke({
        "input": utterance,
        "user_key": user_key
    })

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": response["output"]}}]
        }
    }
```

### 배포 구성

- 개발: FastAPI 로컬 실행 + `ngrok`으로 외부 노출 → 오픈빌더 webhook 등록
- 프로덕션: 내부망 서버 or 클라우드로 이전

---

## 기술 스택 요약

| 컴포넌트 | 기술 |
|---|---|
| LLM | Ollama + EXAONE 3.5 7.8B |
| 임베딩 | Ollama + nomic-embed-text |
| 벡터 DB | ChromaDB |
| RAG/Agent | LangChain |
| API 서버 | FastAPI |
| 카카오 연동 | 카카오 i 오픈빌더 |
| 개발 터널 | ngrok |
