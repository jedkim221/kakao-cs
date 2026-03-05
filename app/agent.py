import os
import re
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
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
Action: 사용할 도구 이름 (도구 이름 목록에서 정확히 선택)
Action Input: 도구에 전달할 값만 입력 (예: ORD-001, 변수명=값 형식 금지)
Observation: 도구 결과
... (필요시 반복)
Thought: 이제 답변할 수 있습니다
Final Answer: 최종 답변 (친절한 한국어로)

대화 이력:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""


def _extract_order_id(raw: str) -> str:
    """LLM이 'order_id = \"ORD-001\"' 형태로 넘길 때 실제 주문번호만 추출."""
    # 따옴표 안의 ORD-XXX 패턴 찾기
    m = re.search(r'(ORD-\w+)', raw, re.IGNORECASE)
    if m:
        return m.group(1)
    # key = value 형태에서 value 추출
    m = re.search(r"=\s*[\"']?([^\"'\s]+)[\"']?", raw)
    if m:
        return m.group(1).strip().strip('"\'')
    return raw.strip().strip('"\'')


def create_agent(user_key: str) -> AgentExecutor:
    llm = ChatOllama(model=LLM_MODEL, temperature=0.3)

    @tool
    def get_order_status_authed(order_id: str) -> str:
        """고객이 특정 주문번호(예: ORD-001)의 배송 상태나 송장번호를 물어볼 때 사용합니다. Action Input에는 주문번호만 입력하세요 (예: ORD-001)."""
        clean_id = _extract_order_id(order_id)
        return get_order_status.invoke({"order_id": clean_id, "user_key": user_key})

    @tool
    def get_my_orders_authed(dummy: str = "") -> str:
        """고객이 특정 주문번호 없이 최근 주문 목록 전체를 보고 싶을 때 사용합니다."""
        return get_my_orders.invoke(user_key)

    authed_tools = [search_faq, get_order_status_authed, get_my_orders_authed]

    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", input_key="input")

    agent = create_react_agent(llm, authed_tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=authed_tools,
        memory=memory,
        verbose=os.getenv("DEBUG", "").lower() in ("1", "true"),
        handle_parsing_errors=True,
        max_iterations=5,
    )
