"""
API Routes
All endpoints are defined here
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
import logging

from app.models import BookingRequest, BookingResponse
from app.services import wait_until_and_submit, FormSubmissionError
from app.storage import add_booking, get_all_bookings
from config.settings import COURTS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["booking"])


def parse_time(time_str: str) -> tuple[int, int]:
    """Parse time string 'HH:MM' to (hour, minute)"""
    try:
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM")


@router.post("/book", response_model=BookingResponse)
async def create_booking(booking: BookingRequest, background_tasks: BackgroundTasks):
    """
    Schedule a court booking

    Submits form at specified time with player names and court/time slot selection.
    All other data (phone, email, student ID, etc.) is auto-filled.
    """
    try:
        # Validate time
        hour, minute = parse_time(booking.submit_time)
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Time out of range")

        # Validate court
        valid_courts = [court["name"] for court in COURTS]
        if booking.court not in valid_courts:
            raise ValueError(f"Invalid court. Must be one of: {valid_courts}")

        player_names = {
            "p1": booking.p1,
            "p2": booking.p2,
            "p3": booking.p3,
        }

        # Save to JSON file
        booking_info = add_booking(
            booking.p1,
            booking.p2,
            booking.p3,
            booking.court,
            booking.submit_time,
            booking.confirmation_email,
        )

        logger.info(
            f"Scheduled: {booking.p1}, {booking.p2}, {booking.p3} for {booking.court} at {booking.submit_time}"
        )

        # Schedule submission in background
        background_tasks.add_task(
            wait_until_and_submit,
            player_names,
            booking.court,
            hour,
            minute,
            booking.confirmation_email,
        )

        return BookingResponse(
            status="scheduled",
            message=f"Booking scheduled for {booking.submit_time}",
            booking=booking_info,
            total_scheduled=len(get_all_bookings()),
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FormSubmissionError as e:
        logger.error(f"Form submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings")
async def get_bookings():
    """Get all scheduled bookings"""
    bookings = get_all_bookings()
    return {"total": len(bookings), "bookings": bookings}


@router.get("/courts")
async def get_courts():
    """Get available courts and time slots"""
    return {"courts": COURTS}
