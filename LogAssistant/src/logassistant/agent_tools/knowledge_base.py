import os
from functools import lru_cache

from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


@lru_cache
def _get_vector_store() -> QdrantVectorStore:
    client = QdrantClient(url=os.environ.get("QDRANT_URL"))
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return QdrantVectorStore(
        client=client, collection_name="mitre_knowledge_base", embedding=embeddings
    )


@tool
def get_mitre_knowledge_base(query: str) -> str:
    """query the MITRE ATT&CK knowledge base for information related to a specific query"""
    results = _get_vector_store().similarity_search(query, k=1)
    return results[0].page_content if results else "No relevant information found."
