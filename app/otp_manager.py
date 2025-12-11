"""
OTP Manager
Handles generation, storage, and verification of One-Time Passwords (OTPs).
"""

import logging
import random
import string
import time
from typing import Dict

logger = logging.getLogger(__name__)

_otp_store: Dict[int, Dict] = {}
_otp_request_timestamps: Dict[int, float] = {}
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


def store_otp(booking_id: int, code: str) -> None:
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
