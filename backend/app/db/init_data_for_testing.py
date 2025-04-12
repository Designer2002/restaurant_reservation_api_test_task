import os
from datetime import datetime, timedelta
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text 
from app.database import SessionLocal
from app.models import Table, Reservation

def init_test_data():
    if os.getenv("INIT_TEST_DATA", "False").lower() != "true":
        print("Skipping test data initialization (INIT_TEST_DATA=False)")
        return

    db = SessionLocal()
    if not db.query(Table).first():
        try:
            # 1. Сначала создаём столы
            tables_data = [
                {"id": 1, "name" : "Big Table", "seats": 4, "location": "Window"},
                {"id": 2, "name" : "Little Bar Table", "seats": 2, "location": "Bar"}
            ]

            for table in tables_data:
                db.execute(
                    text("INSERT INTO tables (id, name, seats, location) VALUES (:id, :name, :seats, :location)"),  # <-- text()
                    table
                )

            # 2. Создаём тестовые брони (reservations)
            reservations_data = [
                {"customer_name": "John Doe", "table_id": 1, "duration_minutes": 90, "reservation_time": "2025-04-10 20:00:00"},
                {"customer_name": "Expired Booking", "table_id": 2, "duration_minutes": 60, "reservation_time": "2025-04-10 15:00:00"}
            ]

            for reservation in reservations_data:
                db.execute(
                    text("INSERT INTO reservations (customer_name, table_id, duration_minutes, reservation_time) VALUES (:customer_name, :table_id, :duration_minutes, :reservation_time)"),  # <-- text()
                    reservation
                )
        except OperationalError as e:
            print(f"Database not ready: {str(e)}")
        except Exception as e:
            db.rollback()
            print(f"Error initializing test data: {str(e)}")
        finally:
            db.commit()
            print("Added testing fields")
            db.close()

if __name__ == "__main__":
    init_test_data()