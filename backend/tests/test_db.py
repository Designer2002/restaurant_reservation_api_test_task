import pytest
from sqlalchemy import select
from backend.app.models.table import Table
from backend.app.models.reservation import Reservation

@pytest.mark.asyncio
async def test_db_connection(async_session):
    async with async_session() as session:
        result = await session.execute(select(1))
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_table_model(async_session):
    async with async_session() as session:
        table = Table(name="Test", capacity=4, location="Test")
        session.add(table)
        await session.commit()
        
        result = await session.execute(select(Table))
        tables = result.scalars().all()
        assert len(tables) == 1
        assert tables[0].name == "Test"