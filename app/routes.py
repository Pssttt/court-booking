"""
API Routes
All endpoints are defined here
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
import logging
import html
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.models import (
    BookingRequest,
    BookingResponse,
    CancelBookingRequest,
    CancelCodeRequest,
    BookingConfirmRequest,
    ConfirmCodeRequest,
)
from app.services import wait_until_and_submit, FormSubmissionError, cancel_task
from app.storage import (
    add_booking,
    get_all_bookings,
    get_booking,
    update_booking_status,
)
from app.discord_service import send_otp_to_discord
from app.telegram_service import send_otp_to_telegram
from app.otp_manager import (
    generate_otp,
    store_otp,
    verify_otp,
    check_otp_request_rate_limit,
    RateLimitExceededError,
)
from config.settings import COURTS, CANCEL_PASSWORD
from app.websockets import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["booking"])

TZ_BANGKOK = ZoneInfo("Asia/Bangkok")


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
    now = datetime.now(TZ_BANGKOK)
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target_time.hour == now.hour and target_time.minute == now.minute:
        pass
    elif target_time < now:
        target_time += timedelta(days=1)

    submission_date = target_time.strftime("%Y-%m-%d %H:%M")
    return target_time.hour, target_time.minute, submission_date


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/book", response_model=BookingResponse)
async def create_booking(booking: BookingRequest):
    """
    Schedule a court booking

    Submits form at specified time with player names and court/time slot selection.
    All other data (phone, email, student ID, etc.) is auto-filled.
    """
    try:
        booking.p1 = html.escape(booking.p1)
        booking.p2 = html.escape(booking.p2)
        booking.p3 = html.escape(booking.p3)
        if booking.confirmation_email:
            booking.confirmation_email = html.escape(booking.confirmation_email)

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

        # Check for duplicate booking
        current_bookings = get_all_bookings()
        for b in current_bookings:
            if (
                b.get("court") == booking.court
                and b.get("p1") == booking.p1
                and b.get("p2") == booking.p2
                and b.get("p3") == booking.p3
                and datetime.fromisoformat(b["created_at"])
                > datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
                and b.get("status") != "cancelled"
            ):
                raise ValueError(
                    "Duplicate booking detected for these players and court."
                )

        # Save to JSON file
        booking_info = add_booking(
            booking.p1,
            booking.p2,
            booking.p3,
            booking.court,
            booking.submit_time,
            booking.confirmation_email,
            submission_date,
            booking.phone,
            booking.student_id,
        )

        confirmation_code = generate_otp()
        store_otp(booking_info["id"], confirmation_code)

        booking_datetime = datetime.strptime(submission_date, "%Y-%m-%d %H:%M")

        discord_success = await send_otp_to_discord(
            booking_info["id"],
            booking.p1,
            confirmation_code,
            otp_type="confirmation",
            court_name=booking.court,
            booking_time=booking_datetime,
        )

        telegram_success = await send_otp_to_telegram(
            booking_info["id"],
            booking.p1,
            confirmation_code,
            otp_type="confirmation",
            court_name=booking.court,
            booking_time=booking_datetime,
        )

        if not discord_success and not telegram_success:
            logger.warning(
                f"Failed to send confirmation OTP for booking {booking_info['id']} to Discord or Telegram."
            )

        logger.info(
            f"Scheduled: {booking.p1}, {booking.p2}, {booking.p3} for {booking.court} at {submission_date}"
        )

        court_aliases = {c["name"]: c.get("alias", c["name"]) for c in COURTS}
        booking_info["alias"] = court_aliases.get(
            booking_info["court"], booking_info["court"]
        )

        await manager.broadcast({"event": "new_booking", "booking": booking_info})

        return BookingResponse(
            status="pending",
            message=f"Booking scheduled for {submission_date} (pending confirmation)",
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

    court_aliases = {c["name"]: c.get("alias", c["name"]) for c in COURTS}

    for booking in bookings:
        booking["alias"] = court_aliases.get(booking["court"], booking["court"])

    return {"total": len(bookings), "bookings": bookings}


@router.get("/courts")
async def get_courts():
    """Get available courts and time slots"""
    return {"courts": COURTS}


@router.post("/confirm-booking")
async def confirm_booking(
    request: BookingConfirmRequest, background_tasks: BackgroundTasks
):
    """
    Confirm a pending booking using an OTP.
    """
    booking = get_booking(request.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Booking is not pending confirmation (current status: {booking['status']})",
        )

    if not verify_otp(request.booking_id, request.confirmation_code):
        raise HTTPException(
            status_code=401, detail="Invalid or expired confirmation code"
        )

    if not update_booking_status(request.booking_id, "confirmed"):
        raise HTTPException(status_code=500, detail="Failed to update booking status.")

    confirmed_booking = get_booking(request.booking_id)
    if not confirmed_booking:
        logger.error(
            f"Confirmed booking {request.booking_id} not found after status update."
        )
        raise HTTPException(status_code=500, detail="Confirmed booking not found.")

    submit_time_str = confirmed_booking.get("submit_time")
    scheduled_datetime_str = confirmed_booking.get("scheduled_datetime")

    if not submit_time_str or not scheduled_datetime_str:
        logger.error(
            f"Missing submit_time or scheduled_datetime for confirmed booking {request.booking_id}"
        )
        raise HTTPException(
            status_code=500, detail="Booking details incomplete for submission."
        )

    submit_hour, submit_minute = map(int, submit_time_str.split(":"))

    player_names = {
        "p1": confirmed_booking.get("p1"),
        "p2": confirmed_booking.get("p2"),
        "p3": confirmed_booking.get("p3"),
    }

    background_tasks.add_task(
        wait_until_and_submit,
        confirmed_booking["id"],
        player_names,
        confirmed_booking["court"],
        submit_hour,
        submit_minute,
        confirmed_booking.get("confirmation_email"),
        confirmed_booking.get("phone"),
        confirmed_booking.get("student_id"),
    )

    logger.info(
        f"Booking {request.booking_id} confirmed and scheduled for submission successfully."
    )

    await manager.broadcast(
        {
            "event": "status_update",
            "booking_id": request.booking_id,
            "status": "confirmed",
        }
    )

    return {
        "status": "confirmed",
        "message": f"Booking {request.booking_id} has been confirmed and submission scheduled.",
        "booking": confirmed_booking,
        "total_scheduled": len(get_all_bookings()),
    }


@router.delete("/cancel")
async def cancel_booking(request: CancelBookingRequest):
    """
    Cancel a scheduled booking

    Requires password authentication for security.
    Accepts either the master CANCEL_PASSWORD or a dynamic OTP sent via Discord.
    Cancels the scheduled background task immediately.
    """
    is_authorized = False

    if request.password == CANCEL_PASSWORD:
        is_authorized = True
    elif verify_otp(request.booking_id, request.password):
        is_authorized = True

    if not is_authorized:
        logger.warning(f"Failed cancel attempt for booking {request.booking_id}")
        raise HTTPException(status_code=401, detail="Invalid password or expired code")

    booking = get_booking(request.booking_id)
    if not booking:
        logger.error(f"Booking {request.booking_id} not found")
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.get("status") == "submitted":
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel a booking that has already been submitted.",
        )

    cancel_task(request.booking_id)

    if not update_booking_status(request.booking_id, "cancelled"):
        logger.error(
            f"Failed to update booking {request.booking_id} status to cancelled in database"
        )
        raise HTTPException(
            status_code=500, detail="Failed to update booking status to cancelled."
        )

    updated_booking = get_booking(request.booking_id)
    if not updated_booking:
        logger.error(f"Booking {request.booking_id} not found after status update.")
        raise HTTPException(
            status_code=500, detail="Booking not found after status update."
        )

    logger.info(
        f"Cancelled booking {request.booking_id}: {updated_booking['p1']}, {updated_booking['p2']}, {updated_booking['p3']}"
    )

    await manager.broadcast(
        {
            "event": "status_update",
            "booking_id": request.booking_id,
            "status": "cancelled",
        }
    )

    return {
        "status": "cancelled",
        "message": f"Booking {request.booking_id} has been cancelled",
        "booking": updated_booking,
        "total_scheduled": len(get_all_bookings()),
    }


@router.post("/request-cancel-code")
async def request_cancel_code(request: CancelCodeRequest):
    """
    Request a dynamic cancellation code (OTP) via Discord
    """
    try:
        check_otp_request_rate_limit(request.booking_id)
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))

    booking = get_booking(request.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    code = generate_otp()
    store_otp(request.booking_id, code)

    discord_success = await send_otp_to_discord(
        request.booking_id, booking["p1"], code, otp_type="cancellation"
    )

    telegram_success = await send_otp_to_telegram(
        request.booking_id, booking["p1"], code, otp_type="cancellation"
    )

    if discord_success or telegram_success:
        return {"message": "Verification code sent to notification channels"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification code. Check server logs.",
        )


@router.post("/request-confirm-code")
async def request_confirm_code(request: ConfirmCodeRequest):
    """
    Request a dynamic confirmation code (OTP) via Discord for a pending booking.
    """
    try:
        check_otp_request_rate_limit(request.booking_id)
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))

    booking = get_booking(request.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Booking is not pending confirmation (current status: {booking['status']}).",
        )

    code = generate_otp()
    store_otp(request.booking_id, code)

    booking_datetime_str = booking.get("scheduled_datetime")
    court_name = booking.get("court")

    if not booking_datetime_str or not court_name:
        logger.error(
            f"Missing scheduled_datetime or court for booking {request.booking_id}"
        )
        raise HTTPException(
            status_code=500, detail="Booking details incomplete for OTP."
        )

    booking_datetime = datetime.fromisoformat(booking_datetime_str)

    discord_success = await send_otp_to_discord(
        request.booking_id,
        booking["p1"],
        code,
        otp_type="confirmation",
        court_name=court_name,
        booking_time=booking_datetime,
    )

    telegram_success = await send_otp_to_telegram(
        request.booking_id,
        booking["p1"],
        code,
        otp_type="confirmation",
        court_name=court_name,
        booking_time=booking_datetime,
    )

    if discord_success or telegram_success:
        return {"message": "Confirmation code sent to notification channels."}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send confirmation code. Check server logs.",
        )
