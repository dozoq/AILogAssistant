from logassistant.services import FileHandler
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document



async def auto_seed_if_needed(client: QdrantClient, collection_name: str) -> bool:
    if client.collection_exists(collection_name): return False
    try:
        blocks = await FileHandler.load_knowledge_base_blocks(separator="---")
    except Exception as e:
        return False

    documents = [Document(page_content=block) for block in blocks]
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
    )

    qdrant = QdrantVectorStore(client=client, collection_name=collection_name, embeddings=embeddings)
    qdrant.add_documents(documents)
    return True