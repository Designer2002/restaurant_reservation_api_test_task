from datetime import datetime, timedelta
from database import SessionLocal
from models.reservation import Reservation
from fastapi import FastAPI
import asyncio
from routes import tables_router, reservations_router

app = FastAPI()

app.include_router(tables_router)
app.include_router(reservations_router)

async def cleanup_reservations():
    while True:
        db = SessionLocal()
        try:
            expired = db.query(Reservation).filter(
                Reservation.reservation_time +
                (Reservation.duration_minutes * timedelta(minutes=1)) < datetime.now()
            ).delete()
            db.commit()
            print(f"Удалено {expired} броней")  # Используйте print вместо return
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
        finally:
            db.close()
            await asyncio.sleep(180)  # 3 минуты

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_reservations())  # Запускаем задачу в фоновом режиме

@app.get("/")
async def root():
    return {"message": "Restaurant API is working!"}
