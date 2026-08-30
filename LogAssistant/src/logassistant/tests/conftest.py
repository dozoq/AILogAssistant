import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from logassistant.core.database import Base
from logassistant.services.threat_service import ThreatService
from fastapi.testclient import TestClient
from logassistant.app import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=False,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _clear_auth_caches():
    from logassistant.services.auth_service import _get_jwt_secret_key, _get_internal_secret_key
    _get_jwt_secret_key.cache_clear()
    _get_internal_secret_key.cache_clear()
    yield

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_database) -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def threat_service(db_session: AsyncSession) -> ThreatService:
    return ThreatService(db_session)