from backend.app.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, server_default="Regular Table")
    seats = Column(Integer)
    location = Column(String(100))
    
    # Добавляем связь с бронированиями
    reservations = relationship(
        "Reservation", 
        back_populates="table",
        cascade="all, delete-orphan",  # Автоматическое удаление зависимых броней
        passive_deletes=True
    )