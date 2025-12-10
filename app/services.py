"""
Google Form Submission Service
"""

import requests
import logging
from typing import Optional
from datetime import datetime
import time
from config.settings import GOOGLE_FORM, BOOKING_DATA, COURTS
from app.email_service import send_confirmation_email

logger = logging.getLogger(__name__)

active_tasks = {}


class FormSubmissionError(Exception):
    """Custom exception for form submission errors"""

    pass


class TaskCancelled(Exception):
    """Exception raised when a task is cancelled"""

    pass


def submit_form(
    player_names: dict,
    court_time: str,
    user_email: Optional[str] = None,
    phone: Optional[str] = None,
    student_id: Optional[str] = None,
) -> bool:
    """
    Submit booking form to Google Form

    Args:
        player_names: {"p1": "Name1", "p2": "Name2", "p3": "Name3"}
        court_time: Selected court and time slot
        user_email: Optional user email for confirmation
        phone: Optional phone number
        student_id: Optional student ID

    Returns:
        True if successful, False otherwise
    """
    try:
        field_ids = GOOGLE_FORM["field_ids"]
        submit_url = GOOGLE_FORM["submit_url"]

        logger.info("Submitting final page with all data")

        if user_email:
            booking_name = player_names.get("p1")
            booking_email = user_email
            booking_phone = phone
            booking_student_code = student_id
        else:
            booking_name = BOOKING_DATA["name"]
            booking_email = BOOKING_DATA["email"]
            booking_phone = BOOKING_DATA["phone"]
            booking_student_code = BOOKING_DATA["student_code"]

        payload = {
            field_ids["name"]: booking_name,
            field_ids["phone"]: booking_phone,
            field_ids["email"]: booking_email,
            field_ids["type_of_client"]: BOOKING_DATA["type_of_client"],
            field_ids["student_code"]: booking_student_code,
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

        response = requests.post(
            submit_url,
            data=payload,
            timeout=10,
            allow_redirects=True,
        )

        logger.info(f"Response status: {response.status_code}")

        if response.status_code in [200, 201, 301]:
            display_court_time = court_time
            for court_data in COURTS:
                if court_data["name"] == court_time:
                    display_court_time = court_data.get("alias", court_time)
                    break

            logger.info(
                f"Form submitted successfully: {player_names['p1']}, {player_names['p2']}, {player_names['p3']} for {display_court_time}"
            )

            if user_email:
                send_confirmation_email(player_names, display_court_time, user_email)
            else:
                send_confirmation_email(player_names, display_court_time)

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
    booking_id: int,
    player_names: dict,
    court_time: str,
    target_hour: int,
    target_minute: int,
    user_email: Optional[str] = None,
    phone: Optional[str] = None,
    student_id: Optional[str] = None,
) -> bool:
    """
    Wait until target time, then submit form

    Registers task in active_tasks dict for potential cancellation.

    Args:
        booking_id: Unique booking identifier for task tracking
        player_names: {"p1": "Name1", "p2": "Name2", "p3": "Name3"}
        court_time: Selected court and time slot
        target_hour: Hour in 24-hour format (0-23)
        target_minute: Minute (0-59)
        user_email: Optional user email for confirmation
        phone: Optional phone number
        student_id: Optional student ID

    Returns:
        True if successful, False otherwise
    """
    logger.info(
        f"Scheduled submission at {target_hour:02d}:{target_minute:02d} for booking {booking_id}"
    )

    active_tasks[booking_id] = True

    try:
        while True:
            if booking_id not in active_tasks:
                logger.info(f"Task for booking {booking_id} was cancelled")
                raise TaskCancelled(f"Booking {booking_id} was cancelled")

            now = datetime.now()
            if now.hour == target_hour and now.minute == target_minute:
                logger.info(f"Submitting form at {now.strftime('%H:%M:%S')}")
                result = submit_form(
                    player_names, court_time, user_email, phone, student_id
                )
                active_tasks.pop(booking_id, None)
                return result

            time.sleep(1)
    except TaskCancelled:
        return False


def cancel_task(booking_id: int) -> bool:
    """
    Cancel a scheduled booking task

    Args:
        booking_id: The booking ID to cancel

    Returns:
        True if task was cancelled, False if not found
    """
    if booking_id in active_tasks:
        del active_tasks[booking_id]
        logger.info(f"Cancelled task for booking {booking_id}")
        return True
    return False
