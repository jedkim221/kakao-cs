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

SYSTEM_PROMPT = """You are a Korean shopping mall CS chatbot. Answer kindly in Korean.

Tools available:
{tools}

Tool names: {tool_names}

Use this EXACT format:
Question: the input question
Thought: which tool to use
Action: tool name (exact match from tool names)
Action Input: input value only
Observation: tool result
Thought: I now know the final answer
Final Answer: 친절한 한국어 답변

Chat history:
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
        return get_my_orders.invoke({"user_key": user_key})

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
        max_iterations=10,
    )
