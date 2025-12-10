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
from config.settings import DISCORD_CONFIG

logger = logging.getLogger(__name__)

_otp_store = {}
OTP_VALIDITY_SECONDS = 300  # 5 minutes


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


def send_otp_to_discord(booking_id: int, player_name: str, code: str) -> bool:
    """
    Send the generated OTP to Discord via Webhook

    Args:
        booking_id: The ID of the booking
        player_name: Name of the primary player
        code: The generated OTP code

    Returns:
        True if successful, False otherwise
    """
    webhook_url = DISCORD_CONFIG["webhook_url"]
    if not webhook_url:
        logger.warning("Discord Webhook URL not configured")
        return False

    try:
        payload = {
            "content": None,
            "embeds": [
                {
                    "title": "🔐 Cancellation Code Requested",
                    "description": f"A cancellation code was requested for Booking **#{booking_id}**.",
                    "color": 16711680,
                    "fields": [
                        {
                            "name": "Booking ID",
                            "value": str(booking_id),
                            "inline": True,
                        },
                        {"name": "Booked By", "value": player_name, "inline": True},
                        {
                            "name": "One-Time Password",
                            "value": f"**`{code}`**",
                            "inline": False,
                        },
                        {
                            "name": "Expires In",
                            "value": f"{OTP_VALIDITY_SECONDS // 60} minutes",
                            "inline": True,
                        },
                    ],
                    "footer": {
                        "text": f"Requested at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    },
                }
            ],
        }

        response = requests.post(webhook_url, json=payload, timeout=5)

        if response.status_code in [200, 204]:
            logger.info(f"OTP sent to Discord for booking {booking_id}")
            return True
        else:
            logger.error(f"Failed to send Discord webhook: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error sending Discord webhook: {str(e)}")
        return False
