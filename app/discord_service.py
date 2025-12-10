"""
Discord Service
Handles interaction with Discord Webhooks for notifications and OTPs
"""

import requests
import logging
import random
import string
import time
from datetime import datetime
from typing import Optional
from config.settings import DISCORD_CONFIG

logger = logging.getLogger(__name__)

_otp_store = {}
_otp_request_timestamps = {}
OTP_VALIDITY_SECONDS = 300  # 5 minutes

OTP_REQUEST_RATE_LIMIT_SECONDS = 60


class RateLimitExceededError(Exception):
    """Custom exception for when a rate limit is exceeded"""

    pass


def check_otp_request_rate_limit(booking_id: int) -> None:
    """
    Checks and enforces a rate limit for OTP requests per booking ID.
    Raises RateLimitExceededError if the limit is exceeded.
    """

    now = time.time()
    last_request_time = _otp_request_timestamps.get(booking_id)

    if (
        last_request_time is not None
        and (now - last_request_time) < OTP_REQUEST_RATE_LIMIT_SECONDS
    ):
        raise RateLimitExceededError(
            f"Rate limit exceeded for booking {booking_id}. Please wait before requesting another OTP."
        )

    _otp_request_timestamps[booking_id] = now


def generate_otp() -> str:
    """Generate a 6-digit random numeric code"""
    return "".join(random.choices(string.digits, k=6))


def store_otp(booking_id: int, code: str):
    """Store OTP with expiration"""
    _otp_store[booking_id] = {
        "code": code,
        "expires_at": time.time() + OTP_VALIDITY_SECONDS,
    }


def verify_otp(booking_id: int, code: str) -> bool:
    """Verify if the provided OTP is valid for the booking"""
    if booking_id not in _otp_store:
        return False

    data = _otp_store[booking_id]
    if time.time() > data["expires_at"]:
        del _otp_store[booking_id]
        return False

    if data["code"] == code:
        del _otp_store[booking_id]
        return True

    return False


def send_otp_to_discord(
    booking_id: int,
    player_name: str,
    code: str,
    otp_type: str = "cancellation",  # "cancellation" or "confirmation"
    court_name: Optional[str] = None,
    booking_time: Optional[datetime] = None,
) -> bool:
    """
    Send the generated OTP to Discord via Webhook. This function can be used for both
    cancellation and booking confirmation OTPs.

    Args:
        booking_id: The ID of the booking
        player_name: Name of the primary player
        code: The generated OTP code
        otp_type: Type of OTP, either "cancellation" or "confirmation".
        court_name: Optional, name of the court for confirmation OTPs.
        booking_time: Optional, time of the booking for confirmation OTPs.

    Returns:
        True if successful, False otherwise
    """
    webhook_url = DISCORD_CONFIG["webhook_url"]
    if not webhook_url:
        logger.warning("Discord Webhook URL not configured")
        return False

    title = ""
    description = ""
    color = 0  # Default color

    if otp_type == "cancellation":
        title = "🔐 Cancellation Code Requested"
        description = (
            f"A cancellation code was requested for Booking **#{booking_id}**."
        )
        color = 16711680  # Red
    elif otp_type == "confirmation":
        title = "✅ Booking Confirmation Code Requested"
        description = (
            f"A confirmation code was requested for Booking **#{booking_id}**."
        )
        color = 65280  # Green
    else:
        logger.error(f"Invalid OTP type: {otp_type}")
        return False

    try:
        fields = [
            {"name": "Booking ID", "value": str(booking_id), "inline": True},
            {"name": "Booked By", "value": player_name, "inline": True},
            {"name": "One-Time Password", "value": f"**`{code}`**", "inline": False},
            {
                "name": "Expires In",
                "value": f"{OTP_VALIDITY_SECONDS // 60} minutes",
                "inline": True,
            },
        ]

        if otp_type == "confirmation" and court_name and booking_time:
            fields.insert(2, {"name": "Court", "value": court_name, "inline": True})
            fields.insert(
                3,
                {
                    "name": "Time",
                    "value": booking_time.strftime("%Y-%m-%d %H:%M"),
                    "inline": True,
                },
            )

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": color,
                    "fields": fields,
                    "footer": {
                        "text": f"Requested at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    },
                }
            ],
        }

        response = requests.post(webhook_url, json=payload, timeout=5)

        if response.status_code in [200, 204]:
            logger.info(
                f"{otp_type.capitalize()} OTP sent to Discord for booking {booking_id}"
            )
            return True
        else:
            logger.error(f"Failed to send Discord webhook: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error sending Discord webhook: {str(e)}")
        return False
