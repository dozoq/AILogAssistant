import asyncio
import os
import uvicorn
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from logassistant.tools.seed_knowledge_base import auto_seed_if_needed
load_dotenv()


async def start_app():
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection_name = "mitre_knowledge_base"
    
    client = QdrantClient(url=qdrant_url)
    
    for attempt in range(10):
        try:
            await auto_seed_if_needed(client, collection_name)
            break
        except Exception as e:
            await asyncio.sleep(2)
            
    config = uvicorn.Config("logassistant.app:app", host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    await server.serve()

def main() -> None:
    asyncio.run(start_app())

if __name__ == "__main__":
    main()