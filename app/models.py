"""
API Models and Data Validation
"""

from pydantic import BaseModel, Field
from typing import Optional


class BookingRequest(BaseModel):
    """Incoming booking request from frontend"""

    p1: str = Field(..., min_length=1, max_length=100)
    p2: str = Field(..., min_length=1, max_length=100)
    p3: str = Field(..., min_length=1, max_length=100)
    court: str = Field(..., min_length=1)
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


class CancelBookingRequest(BaseModel):
    """Request to cancel a booking"""

    booking_id: int
    password: str


class CancelCodeRequest(BaseModel):
    """Request to generate a cancellation code"""

    booking_id: int
