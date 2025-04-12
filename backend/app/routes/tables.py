from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Table
from app.schemas import TableCreate, TableResponse
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tables")

@router.get("/", response_model=list[TableResponse])
def read_tables(db: Session = Depends(get_db)):
    return db.query(Table).all()

#создание столика
@router.post("/", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
def create_table(table: TableCreate, db: Session = Depends(get_db)):
    """
    Создать новый столик в ресторане
    
    - **name**: Название столика (обязательно)
    - **seats**: Количество мест (обязательно)
    - **location**: Расположение (например, "У окна")
    """
    db_table = Table(**table.model_dump())
    db.add(db_table)
    try:
        db.commit()
        db.refresh(db_table)
        return db_table
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании столика: {str(e)}"
        )

# DELETE /tables/{id} - удалить столик
@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    """
    Удалить столик по ID
    
    - **table_id**: ID столика для удаления
    """
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Столик с ID {table_id} не найден"
        )
    
    try:
        db.delete(table)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось удалить столик: {str(e)}"
        )
    
