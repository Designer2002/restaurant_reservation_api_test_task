from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models import Reservation, Table
from backend.app.schemas import ReservationCreate, ReservationResponse

router = APIRouter(prefix="/reservations")

@router.get("/", response_model=list[ReservationResponse])
async def read_reservations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reservation))
    return result.scalars().all()

@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(reservation: ReservationCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Проверка существования столика
        table_result = await db.execute(select(Table).where(Table.id == reservation.table_id))
        table = table_result.scalars().first()
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Столик с ID {reservation.table_id} не найден"
            )

        # Проверка времени бронирования
        moscow_tz = ZoneInfo("Europe/Moscow")
        current_time = datetime.now(moscow_tz)
        reservation_time = reservation.reservation_time.replace(tzinfo=moscow_tz)
        
        if reservation_time < current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя бронировать на прошедшее время"
            )

        # Проверка пересечения временных интервалов
        existing_query = await db.execute(
            select(Reservation).where(
                Reservation.table_id == reservation.table_id,
                text("""
                    timezone('Europe/Moscow', :res_time) < 
                    timezone('Europe/Moscow', reservations.reservation_time) + 
                    (reservations.duration_minutes * interval '1 minute')
                    AND
                    timezone('Europe/Moscow', :res_time) + 
                    (:duration * interval '1 minute') > 
                    timezone('Europe/Moscow', reservations.reservation_time)
                """).bindparams(
                    res_time=reservation.reservation_time,
                    duration=reservation.duration_minutes
                )
            )
        )
        existing = existing_query.scalars().first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Столик уже забронирован на это время"
            )

        db_reservation = Reservation(
            customer_name=reservation.customer_name,
            table_id=reservation.table_id,
            reservation_time=reservation_time,
            duration_minutes=reservation.duration_minutes
        )
        
        db.add(db_reservation)
        await db.commit()
        await db.refresh(db_reservation)
        return db_reservation
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании бронирования: {str(e)}"
        )

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    reservation = result.scalars().first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {reservation_id} не найдено"
        )
    
    try:
        await db.delete(reservation)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось удалить бронирование: {str(e)}"
        )