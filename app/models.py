"""
API Models and Data Validation
"""

from pydantic import BaseModel
from typing import Optional


class BookingRequest(BaseModel):
    """Incoming booking request from frontend"""

    p1: str
    p2: str
    p3: str
    court: str
    submit_time: str = "13:00"
    confirmation_email: Optional[str] = None


class BookingResponse(BaseModel):
    """Response after booking is scheduled"""

    status: str
    message: str
    booking: dict
    total_scheduled: int


class BookingsListResponse(BaseModel):
    """Response for listing all bookings"""

    total: int
    bookings: list
