"""
Email Service
Send confirmation emails using Resend
"""

import logging
from typing import Optional
from config.settings import EMAIL_CONFIG

logger = logging.getLogger(__name__)


def send_confirmation_email(
    player_names: dict, court_time: str, recipient_email: Optional[str] = None
) -> bool:
    """
    Send booking confirmation email to user and admin

    Args:
        player_names: {"p1": "Name1", "p2": "Name2", "p3": "Name3"}
        court_time: Selected court and time slot
        recipient_email: Optional user email (admin always gets one)

    Returns:
        True if successful, False otherwise
    """
    try:
        if not EMAIL_CONFIG["api_key"]:
            logger.warning("Resend API key not configured, skipping email")
            return False

        import resend

        resend.api_key = EMAIL_CONFIG["api_key"]

        html_content = f"""
        <html>
            <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #333;">Booking Confirmed</h1>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="margin-top: 0; color: #555;">Booking Details</h2>
                    
                    <p><strong>Court & Time:</strong> {court_time}</p>
                    
                    <h3 style="margin-top: 20px; color: #555;">Players</h3>
                    <ul>
                        <li>{player_names.get("p1", "N/A")}</li>
                        <li>{player_names.get("p2", "N/A")}</li>
                        <li>{player_names.get("p3", "N/A")}</li>
                    </ul>
                </div>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    This is an automated confirmation email. Please do not reply.
                </p>
            </body>
        </html>
        """

        # Send to user if provided
        if recipient_email:
            params = {
                "from": EMAIL_CONFIG["from_email"],
                "to": [recipient_email],
                "subject": f"Badminton Court Booking Confirmed - {court_time}",
                "html": html_content,
            }

            response = resend.Emails.send(params)

            if response and response.get("id"):
                logger.info(
                    f"Confirmation email sent to user {recipient_email} (ID: {response.get('id')})"
                )
            else:
                logger.error(f"Email to user failed: {response}")

        # Always send to admin
        admin_email = EMAIL_CONFIG["confirmation_to"]
        params = {
            "from": EMAIL_CONFIG["from_email"],
            "to": [admin_email],
            "subject": f"Badminton Court Booking Confirmed - {court_time}",
            "html": html_content,
        }

        response = resend.Emails.send(params)

        if response and response.get("id"):
            logger.info(
                f"Confirmation email sent to admin {admin_email} (ID: {response.get('id')})"
            )
            return True
        else:
            logger.error(f"Email to admin failed: {response}")
            return False

    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return False
