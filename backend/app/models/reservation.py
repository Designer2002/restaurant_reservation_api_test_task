from backend.app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    reservation_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Добавляем обратную ссылку на столик
    table = relationship("Table", back_populates="reservations")