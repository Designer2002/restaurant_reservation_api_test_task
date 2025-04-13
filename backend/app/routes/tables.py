from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models import Table
from backend.app.schemas import TableCreate, TableResponse

router = APIRouter(prefix="/tables")

@router.get("/", response_model=list[TableResponse])
async def read_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Table))
    return result.scalars().all()

@router.post("/", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(table: TableCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_table = Table(**table.model_dump())
        db.add(db_table)
        await db.commit()
        await db.refresh(db_table)
        return db_table
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании столика: {str(e)}"
        )

@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(table_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Table).where(Table.id == table_id))
    table = result.scalars().first()
    
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Столик с ID {table_id} не найден"
        )
    
    try:
        await db.delete(table)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось удалить столик: {str(e)}"
        )