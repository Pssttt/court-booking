"""
Application Settings
Loads from environment variables (.env file)
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ============================================================================
# BOOKING FORM DATA
# ============================================================================

BOOKING_DATA = {
    "name": os.getenv("BOOKING_NAME"),
    "phone": os.getenv("BOOKING_PHONE"),
    "email": os.getenv("BOOKING_EMAIL"),
    "student_code": os.getenv("BOOKING_STUDENT_CODE"),
    "department": os.getenv("BOOKING_DEPARTMENT"),
    "faculty": os.getenv("BOOKING_FACULTY"),
    "year_of_study": os.getenv("BOOKING_YEAR_OF_STUDY"),
    "degree": os.getenv("BOOKING_DEGREE"),
    "type_of_client": os.getenv("BOOKING_TYPE_OF_CLIENT"),
}

# ============================================================================
# GOOGLE FORM CONFIGURATION
# ============================================================================

GOOGLE_FORM = {
    "submit_url": os.getenv("GOOGLE_FORM_SUBMIT_URL"),
    "field_ids": {
        "name": "entry.1447004130",
        "phone": "entry.1162689565",
        "email": "entry.397132313",
        "type_of_client": "entry.60086338",
        "student_code": "entry.1758389959",
        "department": "entry.578101683",
        "faculty": "entry.2138721565",
        "degree": "entry.188451592",
        "year_of_study": "entry.1610619932",
        "court_time": "entry.1063303379",
        "p1": "entry.1572571765",
        "p2": "entry.1458140720",
        "p3": "entry.1099932442",
    },
}

# ============================================================================
# COURT OPTIONS (Court + Time Slot)
# ============================================================================

COURTS = [
    {
        "id": "1",
        "name": "คอร์ทที่ 1   รอบที่ 1  เวลา 17.30 – 18.30 น. | Court no.1: 1st Period: 17.30-18.30 hrs.",
        "alias": "Court 1, 1st Period (17:30 - 18:30)",
    },
    {
        "id": "2",
        "name": "คอร์ทที่ 1   รอบที่ 2  เวลา 18.45 – 19.45 น. | Court no.1: 2nd Period: 18.45-19.45 hrs.",
        "alias": "Court 1, 2nd Period (18:45 - 19:45)",
    },
    {
        "id": "3",
        "name": "คอร์ทที่ 2   รอบที่ 1  เวลา 17.30 – 18.30 น. | Court no.1: 1st Period: 17.30-18.30 hrs.",
        "alias": "Court 2, 1st Period (17:30 - 18:30)",
    },
    {
        "id": "4",
        "name": "คอร์ทที่ 2   รอบที่ 2  เวลา 18.45 – 19.45 น. | Court no.1: 2nd Period: 18.45-19.45 hrs.",
        "alias": "Court 2, 2nd Period (18:45 - 19:45)",
    },
    {
        "id": "5",
        "name": "คอร์ทที่ 3   รอบที่ 1  เวลา 17.30 – 18.30 น. | Court no.1: 1st Period: 17.30-18.30 hrs.",
        "alias": "Court 3, 1st Period (17:30 - 18:30)",
    },
    {
        "id": "6",
        "name": "คอร์ทที่ 3   รอบที่ 2  เวลา 18.45 – 19.45 น. | Court no.1: 2nd Period: 18.45-19.45 hrs.",
        "alias": "Court 3, 2nd Period (18:45 - 19:45)",
    },
    {
        "id": "7",
        "name": "คอร์ทที่ 4   รอบที่ 1  เวลา 17.30 – 18.30 น. | Court no.1: 1st Period: 17.30-18.30 hrs.",
        "alias": "Court 4, 1st Period (17:30 - 18:30)",
    },
    {
        "id": "8",
        "name": "คอร์ทที่ 4   รอบที่ 2  เวลา 18.45 – 19.45 น. | Court no.1: 2nd Period: 18.45-19.45 hrs.",
        "alias": "Court 4, 2nd Period (18:45 - 19:45)",
    },
]

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_CONFIG = {
    "api_key": os.getenv("RESEND_API_KEY", ""),
    "from_email": os.getenv("RESEND_FROM_EMAIL", ""),
    "confirmation_to": os.getenv("CONFIRMATION_EMAIL", ""),
}

# ============================================================================
# SERVER SETTINGS
# ============================================================================

SERVER = {
    "host": os.getenv("SERVER_HOST", "0.0.0.0"),
    "port": int(os.getenv("SERVER_PORT", "3000")),
    "debug": os.getenv("SERVER_DEBUG", "false").lower() == "true",
}

# ============================================================================
# DEFAULT SUBMISSION TIME
# ============================================================================

DEFAULT_SUBMIT_TIME = "13:00"

# ============================================================================
# CANCEL BOOKING PASSWORD
# ============================================================================

CANCEL_PASSWORD = os.getenv("CANCEL_PASSWORD")

# ============================================================================
# DISCORD CONFIGURATION
# ============================================================================

DISCORD_CONFIG = {
    "webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
}

# ============================================================================
# TELEGRAM CONFIGURATION
# ============================================================================

TELEGRAM_CONFIG = {
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
}
