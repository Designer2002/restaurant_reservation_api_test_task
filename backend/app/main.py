from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db, engine, Base
from backend.app.models.reservation import Reservation
from backend.app.routes import tables_router, reservations_router

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(tables_router)
app.include_router(reservations_router)

async def cleanup_expired_reservations():
    """Фоновая задача для очистки просроченных бронирований"""
    moscow_tz = ZoneInfo("Europe/Moscow")
    while True:
        async with AsyncSession(engine) as db:
            try:
                # Получаем текущее время с учетом часового пояса
                now = datetime.now(moscow_tz)
                
                # Удаляем бронирования, у которых время окончания прошло
                stmt = delete(Reservation).where(
                    Reservation.reservation_time +
                (Reservation.duration_minutes * timedelta(minutes=1)) < datetime.now())
                
                result = await db.execute(stmt)
                await db.commit()
                
                if result.rowcount > 0:
                    print(f"Удалено {result.rowcount} просроченных бронирований")
                
            except Exception as e:
                print(f"Ошибка при очистке бронирований: {e}")
                await db.rollback()
            
            # Пауза 3 минуты между проверками
            await asyncio.sleep(180)

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    # Создаем таблицы в БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Запускаем фоновую задачу очистки
    asyncio.create_task(cleanup_expired_reservations())

@app.get("/")
async def root():
    """Проверка работоспособности API"""
    return {"message": "Restaurant API is working!"}