import pytest
from app.ingest import load_documents, create_vectorstore, get_vectorstore


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
