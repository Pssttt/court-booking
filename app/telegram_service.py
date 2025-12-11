"""
Telegram Service
Handles interaction with Telegram Bot API for notifications and OTPs
"""

import requests
import logging
from datetime import datetime
from typing import Optional
from config.settings import COURTS, TELEGRAM_CONFIG
from app.otp_manager import OTP_VALIDITY_SECONDS

logger = logging.getLogger(__name__)


def send_otp_to_telegram(
    booking_id: int,
    player_name: str,
    code: str,
    otp_type: str = "cancellation",  # "cancellation" or "confirmation"
    court_name: Optional[str] = None,
    booking_time: Optional[datetime] = None,
) -> bool:
    """
    Send the generated OTP to Telegram via Bot API.

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
    bot_token = TELEGRAM_CONFIG["bot_token"]
    chat_id = TELEGRAM_CONFIG["chat_id"]

    if not bot_token or not chat_id:
        # Only log warning if we expect to use Telegram (e.g. implicitly if not configured)
        # But if the user didn't set it up, maybe we shouldn't spam logs.
        # However, for now, let's log it so they know why it failed if they tried.
        logger.debug("Telegram credentials not configured")
        return False

    message = ""
    if otp_type == "cancellation":
        message = f"🔐 *Cancellation Code Requested*\n\n"
        message += f"Booking ID: *#{booking_id}*\n"
        message += f"Booked By: {player_name}\n"
        message += f"Code: `{code}`\n"
    elif otp_type == "confirmation":
        message = f"✅ *Confirmation Code Requested*\n\n"
        message += f"Booking ID: *#{booking_id}*\n"
        message += f"Booked By: {player_name}\n"

        if court_name and booking_time:
            display_court_name = court_name
            for court_data in COURTS:
                if court_data["name"] == court_name:
                    display_court_name = court_data.get("alias", court_name)
                    break

            date_str = booking_time.strftime("%d %b %Y")
            time_str = booking_time.strftime("%H:%M")

            message += f"Date: {date_str}\n"
            message += f"Time: {time_str}\n"
            message += f"Court: {display_court_name}\n"

        message += f"Code: `{code}`\n"
    else:
        logger.error(f"Invalid OTP type: {otp_type}")
        return False

    message += f"\n_Expires in {OTP_VALIDITY_SECONDS // 60} minutes_"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            logger.info(
                f"{otp_type.capitalize()} OTP sent to Telegram for booking {booking_id}"
            )
            return True
        else:
            logger.error(
                f"Failed to send Telegram message: {response.status_code} {response.text}"
            )
            return False

    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")
        return False
