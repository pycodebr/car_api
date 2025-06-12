# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker


# DATABASE_URL = 'sqlite:///./cars.db'

# engine = create_engine(
#     DATABASE_URL,
#     connect_args={'check_same_thread': False},
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
# )


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = 'sqlite+aiosqlite:///./cars.db'

engine = create_async_engine(DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
