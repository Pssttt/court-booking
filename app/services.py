"""
Google Form Submission Service
"""

import requests
import logging
from typing import Optional
from datetime import datetime
import time
from config.settings import GOOGLE_FORM, BOOKING_DATA
from app.email_service import send_confirmation_email

logger = logging.getLogger(__name__)


class FormSubmissionError(Exception):
    """Custom exception for form submission errors"""

    pass


def submit_form(
    player_names: dict, court_time: str, user_email: Optional[str] = None
) -> bool:
    """
    Submit booking form to Google Form

    Args:
        player_names: {"p1": "Name1", "p2": "Name2", "p3": "Name3"}
        court_time: Selected court and time slot
        user_email: Optional user email for confirmation

    Returns:
        True if successful, False otherwise
    """
    try:
        field_ids = GOOGLE_FORM["field_ids"]
        submit_url = GOOGLE_FORM["submit_url"]

        logger.info("Submitting final page with all data")

        payload = {
            field_ids["name"]: BOOKING_DATA.get("name", BOOKING_DATA["phone"]),
            field_ids["phone"]: BOOKING_DATA["phone"],
            field_ids["email"]: BOOKING_DATA["email"],
            field_ids["type_of_client"]: BOOKING_DATA["type_of_client"],
            field_ids["student_code"]: BOOKING_DATA["student_code"],
            field_ids["department"]: BOOKING_DATA["department"],
            field_ids["faculty"]: BOOKING_DATA["faculty"],
            field_ids["degree"]: BOOKING_DATA["degree"],
            field_ids["year_of_study"]: BOOKING_DATA["year_of_study"],
            field_ids["court_time"]: court_time,
            field_ids["p1"]: player_names.get("p1"),
            field_ids["p2"]: player_names.get("p2"),
            field_ids["p3"]: player_names.get("p3"),
            "pageHistory": "0,1,3,4",
        }

        response = requests.post(submit_url, data=payload, timeout=10)

        logger.info(f"Response status: {response.status_code}")

        if response.status_code in [200, 201, 301]:
            logger.info(
                f"Form submitted successfully: {player_names['p1']}, {player_names['p2']}, {player_names['p3']} for {court_time}"
            )

            if user_email:
                send_confirmation_email(player_names, court_time, user_email)

            send_confirmation_email(player_names, court_time)

            return True
        else:
            logger.error(f"Form submission failed with status {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return False

    except requests.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        raise FormSubmissionError(f"Failed to submit form: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise FormSubmissionError(f"Error submitting form: {str(e)}")


def wait_until_and_submit(
    player_names: dict,
    court_time: str,
    target_hour: int,
    target_minute: int,
    user_email: Optional[str] = None,
) -> bool:
    """
    Wait until target time, then submit form

    Args:
        player_names: {"p1": "Name1", "p2": "Name2", "p3": "Name3"}
        court_time: Selected court and time slot
        target_hour: Hour in 24-hour format (0-23)
        target_minute: Minute (0-59)
        user_email: Optional user email for confirmation

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Scheduled submission at {target_hour:02d}:{target_minute:02d}")

    while True:
        now = datetime.now()
        if now.hour == target_hour and now.minute == target_minute:
            logger.info(f"Submitting form at {now.strftime('%H:%M:%S')}")
            return submit_form(player_names, court_time, user_email)

        time.sleep(1)
