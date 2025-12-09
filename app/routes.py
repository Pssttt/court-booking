"""
API Routes
All endpoints are defined here
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
import logging
from datetime import datetime, timedelta

from app.models import BookingRequest, BookingResponse, CancelBookingRequest
from app.services import wait_until_and_submit, FormSubmissionError, cancel_task
from app.storage import add_booking, get_all_bookings, delete_booking, get_booking
from config.settings import COURTS, CANCEL_PASSWORD

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["booking"])


def parse_time(time_str: str) -> tuple[int, int]:
    """Parse time string 'HH:MM' to (hour, minute)"""
    try:
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM")


def get_next_submission_time(hour: int, minute: int) -> tuple[int, int, str]:
    """
    Get the next submission time, accounting for past times (next day).

    Returns:
        Tuple of (target_hour, target_minute, submission_date_str)
    """
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target_time < now:
        target_time += timedelta(days=1)

    submission_date = target_time.strftime("%Y-%m-%d %H:%M")
    return target_time.hour, target_time.minute, submission_date


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

        target_hour, target_minute, submission_date = get_next_submission_time(
            hour, minute
        )

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
            submission_date,
        )

        logger.info(
            f"Scheduled: {booking.p1}, {booking.p2}, {booking.p3} for {booking.court} at {submission_date}"
        )

        # Schedule submission in background
        background_tasks.add_task(
            wait_until_and_submit,
            booking_info["id"],
            player_names,
            booking.court,
            target_hour,
            target_minute,
            booking.confirmation_email,
        )

        return BookingResponse(
            status="scheduled",
            message=f"Booking scheduled for {submission_date}",
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


@router.delete("/cancel")
async def cancel_booking(request: CancelBookingRequest):
    """
    Cancel a scheduled booking

    Requires password authentication for security.
    Cancels the scheduled background task immediately.
    """
    if request.password != CANCEL_PASSWORD:
        logger.warning(f"Failed cancel attempt for booking {request.booking_id}")
        raise HTTPException(status_code=401, detail="Invalid password")

    booking = get_booking(request.booking_id)
    if not booking:
        logger.error(f"Booking {request.booking_id} not found")
        raise HTTPException(status_code=404, detail="Booking not found")

    cancel_task(request.booking_id)

    delete_booking(request.booking_id)

    logger.info(
        f"Cancelled booking {request.booking_id}: {booking['p1']}, {booking['p2']}, {booking['p3']}"
    )

    return {
        "status": "cancelled",
        "message": f"Booking {request.booking_id} has been cancelled",
        "booking": booking,
        "total_scheduled": len(get_all_bookings()),
    }
