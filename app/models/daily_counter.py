"""DailyCounter model for order number generation."""

from datetime import date

from sqlalchemy import Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyCounter(Base):
    """Daily counter for generating sequential order numbers."""
    
    __tablename__ = "daily_counters"
    
    counter_date: Mapped[date] = mapped_column(Date, primary_key=True)
    counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<DailyCounter(date={self.counter_date}, counter={self.counter})>"
