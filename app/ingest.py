import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = str(Path(__file__).parent.parent / "chroma_db")
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
