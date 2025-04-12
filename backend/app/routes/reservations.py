from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, and_
from sqlalchemy.sql.expression import cast
from sqlalchemy import text
from backend.app.database import get_db
from backend.app.models import Reservation, Table
from backend.app.schemas import ReservationCreate, ReservationResponse
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
router = APIRouter(prefix="/reservations")

@router.get("/", response_model=list[ReservationResponse])
def read_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    """
    Создать новое бронирование столика
    """
    try:
        # Проверка существования столика
        table = db.query(Table).filter(Table.id == reservation.table_id).first()
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Столик с ID {reservation.table_id} не найден"
            )

        # Проверка что время бронирования не в прошлом
        moscow_tz = ZoneInfo("Europe/Moscow")
        current_time = datetime.now(moscow_tz)
        reservation_time = reservation.reservation_time.replace(tzinfo=moscow_tz)
        
        if reservation_time < current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя бронировать на прошедшее время"
            )

        # Проверка пересечения временных интервалов
        existing = db.query(Reservation).filter(
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
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Столик уже забронирован на это время"
            )

        db_reservation = Reservation(
            customer_name=reservation.customer_name,
            table_id=reservation.table_id,
            reservation_time=reservation_time,  # Используем исправленное время
            duration_minutes=reservation.duration_minutes
        )
        
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании бронирования: {str(e)}"
        )

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """
    Удалить бронирование по ID
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {reservation_id} не найдено"
        )
    
    try:
        db.delete(reservation)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось удалить бронирование: {str(e)}"
        )