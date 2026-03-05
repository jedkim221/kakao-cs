from langchain_core.tools import tool
from app.ingest import get_vectorstore


@tool
def search_faq(query: str) -> str:
    """FAQ, 정책, 상품 정보를 검색합니다. 배송, 환불, 교환, 상품 사이즈 등의 질문에 사용하세요."""
    try:
        vectorstore = get_vectorstore()
        docs = vectorstore.similarity_search(query, k=3)
        if not docs:
            return "관련 정보를 찾지 못했습니다."
        return "\n\n".join(doc.page_content for doc in docs)
    except Exception:
        return "정보 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
