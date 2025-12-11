"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TZ_BANGKOK = ZoneInfo("Asia/Bangkok")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    p1 = Column(String, index=True)
    p2 = Column(String)
    p3 = Column(String)
    court = Column(String)
    submit_time = Column(String)
    scheduled_datetime = Column(DateTime, nullable=True)
    confirmation_email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    student_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(TZ_BANGKOK))

    booking_name = Column(String, nullable=True)
    booking_email = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
