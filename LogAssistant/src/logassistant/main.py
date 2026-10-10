import asyncio
import os

import uvicorn
from dotenv import load_dotenv

from logassistant.core import ENV

load_dotenv(ENV)
from qdrant_client import QdrantClient

from logassistant.core.database import init_db
from logassistant.tools.seed_knowledge_base import auto_seed_if_needed


async def initialize_app():
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection_name = "mitre_knowledge_base"

    client = QdrantClient(url=qdrant_url)

    for _ in range(10):
        try:
            await auto_seed_if_needed(client, collection_name)
            break
        # TODO: Refactor
        except Exception as e:
            await asyncio.sleep(2)

    await init_db()


def main():
    asyncio.run(initialize_app())
    uvicorn.run(
        "logassistant.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


print("test")


if __name__ == "__main__":
    main()
