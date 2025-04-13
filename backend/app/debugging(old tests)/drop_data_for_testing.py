import os
from sqlalchemy import text
from backend.app.database import SessionLocal

# Настройки подключения (должны совпадать с вашим приложением)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db/restaurant")

session = SessionLocal()

def delete_all_data():
    if os.getenv("NEED_TO_DROP_TEST_DATA", "False").lower() != "true":
        return
    try:
        # Удаляем в правильном порядке из-за foreign key
        session.execute(text("DELETE FROM reservations"))
        session.execute(text("DELETE FROM tables"))
        session.commit()
        print("✅ Test data is gone!")
    except Exception as e:
        session.rollback()
        print(f"❌ Something went wrong while deleting test data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    delete_all_data()