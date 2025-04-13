import asyncio
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database import Base, get_db

#TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
TEST_DATABASE_URL = "http://localhost:8000"
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=True  # Для отладки SQL-запросов
    )
    yield engine
    await engine.dispose()

async def wait_for_db(engine, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
                return True
        except Exception as e:
            if attempt == max_attempts - 1:
                raise ConnectionError(f"Не удалось подключиться к БД после {max_attempts} попыток") from e
            await asyncio.sleep(1)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db(async_engine):
    await wait_for_db(async_engine)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(async_engine):
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        async_session = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession
        )
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()
                await transaction.rollback()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()