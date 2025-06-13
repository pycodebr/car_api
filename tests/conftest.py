import httpx
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from car_api.app import app
from car_api.database import get_session
from car_api.models import Base
from car_api.settings import Settings

DATABASE_URL = Settings().DATABASE_URL


@pytest_asyncio.fixture(scope='function')
async def engine():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url='http://testserver'
    ) as client:
        yield client
    app.dependency_overrides.clear()
