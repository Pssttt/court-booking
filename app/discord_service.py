"""
Discord Service
Handles interaction with Discord Webhooks for notifications and OTPs
"""

import httpx
import logging
from datetime import datetime, timezone
from typing import Optional
from config.settings import COURTS, DISCORD_CONFIG
from app.otp_manager import OTP_VALIDITY_SECONDS

logger = logging.getLogger(__name__)


async def send_otp_to_discord(
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
    color = 0

    if otp_type == "cancellation":
        title = f"🔐 Cancellation Code Requested for Booking **#{booking_id}**"
        color = 0xE67E22
    elif otp_type == "confirmation":
        title = f"✅ Confirmation Code Requested for Booking **#{booking_id}**"
        color = 0x3498DB
    else:
        logger.error(f"Invalid OTP type: {otp_type}")
        return False

    try:
        fields = [
            {"name": "Booked By", "value": player_name, "inline": True},
            {
                "name": "VERIFICATION CODE",
                "value": f"**```\n{code}\n```**",
                "inline": False,
            },
        ]

        if otp_type == "confirmation" and court_name and booking_time:
            display_court_name = court_name

            for court_data in COURTS:
                if court_data["name"] == court_name:
                    display_court_name = court_data.get("alias", court_name)
                    break

            date_str = booking_time.strftime("%d %b %Y")
            time_str = booking_time.strftime("%H:%M")

            fields.insert(
                2,
                {"name": "DATE", "value": date_str, "inline": True},
            )

            fields.insert(
                3,
                {"name": "TIME", "value": time_str, "inline": True},
            )

            fields.insert(
                4, {"name": "COURT", "value": display_court_name, "inline": False}
            )

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": title,
                    "color": color,
                    "fields": fields,
                    "image": {
                        "url": "https://img.freepik.com/premium-photo/badminton-sports-background-vector-international-sports-day-illustration-graphic-design-decoration-gift-certificates-banners-flyers_880763-31028.jpg"
                    },
                    "footer": {
                        "text": f"Expires in {OTP_VALIDITY_SECONDS // 60} minutes"
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=5)

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
