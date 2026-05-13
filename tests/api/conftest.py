import pytest
from uuid import uuid4
from ..types import TestTokens
from app.main import create_app
from sqlalchemy.pool import NullPool
from unittest.mock import patch, AsyncMock
from pytest_mock import MockerFixture, AsyncMockType
from sqlmodel import SQLModel, select
from fastapi.testclient import TestClient
from app.user.models import User, RoleEnum
from app.database.config import get_session
from app.common.dependencies import get_http_client, get_redis_client
from typing import AsyncGenerator, Generator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5434/test_db"

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session

    mock_redis = AsyncMock()
    with patch("app.main.redis_from_url", return_value=mock_redis):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def mock_http_client(client: TestClient, mocker: MockerFixture) -> Generator[AsyncMockType, None, None]:
    mock = mocker.AsyncMock()
    client.app.dependency_overrides[get_http_client] = lambda: mock  # type: ignore
    yield mock
    client.app.dependency_overrides.pop(get_http_client)  # type: ignore


@pytest.fixture()
def mock_redis_client(client: TestClient, mocker: MockerFixture) -> Generator[AsyncMockType, None, None]:
    mock = mocker.AsyncMock()
    client.app.dependency_overrides[get_redis_client] = lambda: mock  # type: ignore
    yield mock
    client.app.dependency_overrides.pop(get_redis_client)  # type: ignore


@pytest.fixture()
async def commander_tokens(client: TestClient) -> TestTokens:
    email = f"commander_{uuid4().hex[:8]}@test.com"
    client.post("/v1/auth/register/", json={
        "full_name": "Commander",
        "email": email,
        "password": "password"
    })
    async with TestingSessionLocal() as session:
        user = (await session.exec(select(User).where(User.email == email))).one()
        user.role = RoleEnum.COMMANDER
        await session.commit()
    login_response = client.post("/v1/auth/login/", json={"email": email, "password": "password"})

    return login_response.json()["data"]  # type: ignore
