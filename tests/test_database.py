from builtins import anext

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from car_api import database
from car_api.models import Base
from car_api.settings import Settings


@pytest.mark.asyncio
async def test_get_session(monkeypatch):
    engine = create_async_engine(Settings().DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    monkeypatch.setattr(database, 'engine', engine)
    gen = database.get_session()
    session = await anext(gen)

    assert isinstance(session, AsyncSession)

    await gen.aclose()
    await engine.dispose()
