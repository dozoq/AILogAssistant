from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from logassistant.core.database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


db_dependency = Annotated[AsyncSession, Depends(get_db)]
