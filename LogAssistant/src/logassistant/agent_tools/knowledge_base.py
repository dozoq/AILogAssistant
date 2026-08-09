import os
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

client = QdrantClient(url=os.environ.get("QDRANT_URL"))
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
vector_store = QdrantVectorStore(client=client, collection_name="mitre_knowledge_base", embedding=embeddings)



@tool
def get_mitre_knowledge_base(query: str) -> str:
    """query the MITRE ATT&CK knowledge base for information related to a specific query"""
    results = vector_store.similarity_search(query, k=1)
    return results[0].page_content if results else "No relevant information found."