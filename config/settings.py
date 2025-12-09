"""
Application Settings
Loads from environment variables (.env file)
"""

import os
from dotenv import load_dotenv

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
    "type_of_client": "Student",
}

# ============================================================================
# GOOGLE FORM CONFIGURATION
# ============================================================================

GOOGLE_FORM = {
    "form_url": os.getenv("GOOGLE_FORM_URL"),
    "submit_url": os.getenv("GOOGLE_FORM_SUBMIT_URL"),
    "field_ids": {
        "name": "entry.167015706",
        "phone": "entry.1279526764",
        "email": "entry.118361342",
        "type_of_client": "entry.1823184155",
        "student_code": "entry.738742748",
        "department": "entry.413295108",
        "faculty": "entry.204898568",
        "degree": "entry.129371148",
        "year_of_study": "entry.448340794",
        "court": "entry.1456468180",
        "p1": "entry.1726626976",
        "p2": "entry.924493527",
        "p3": "entry.1057624971",
    },
}

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

EMAIL_CONFIG = {
    "api_key": os.getenv("RESEND_API_KEY", ""),
    "from_email": os.getenv("RESEND_FROM_EMAIL"),
    "confirmation_to": os.getenv("CONFIRMATION_EMAIL"),
}

# ============================================================================
# COURT OPTIONS
# ============================================================================

COURTS = [
    {"id": "1", "name": "Court No. 1"},
    {"id": "2", "name": "Court No. 2"},
    {"id": "3", "name": "Court No. 3"},
    {"id": "4", "name": "Court No. 4"},
    {"id": "5", "name": "Court No. 5"},
    {"id": "6", "name": "Court No. 6"},
    {"id": "7", "name": "Court No. 7"},
    {"id": "8", "name": "Court No. 8"},
]

# ============================================================================
# SERVER SETTINGS
# ============================================================================

SERVER = {
    "host": os.getenv("SERVER_HOST", "0.0.0.0"),
    "port": int(os.getenv("SERVER_PORT", "8000")),
    "debug": os.getenv("SERVER_DEBUG", "false").lower() == "true",
}

# ============================================================================
# DEFAULT SUBMISSION TIME
# ============================================================================

DEFAULT_SUBMIT_TIME = "13:00"
