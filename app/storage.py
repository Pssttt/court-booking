"""
Booking Storage Service
Persists bookings to JSON file
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# store bookings in data/bookings.json
DATA_DIR = Path(__file__).parent.parent / "data"
BOOKINGS_FILE = DATA_DIR / "bookings.json"


def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    DATA_DIR.mkdir(exist_ok=True)


def load_bookings():
    """Load bookings from JSON file"""
    try:
        if BOOKINGS_FILE.exists():
            with open(BOOKINGS_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading bookings: {e}")
        return []


def save_bookings(bookings):
    """Save bookings to JSON file"""
    try:
        ensure_data_dir()
        with open(BOOKINGS_FILE, "w") as f:
            json.dump(bookings, f, indent=2)
        logger.info(f"Saved {len(bookings)} bookings to {BOOKINGS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving bookings: {e}")
        return False


def add_booking(
    p1: str,
    p2: str,
    p3: str,
    court: str,
    submit_time: str,
    confirmation_email: Optional[str] = None,
):
    """Add a new booking"""
    bookings = load_bookings()

    booking = {
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "court": court,
        "submit_time": submit_time,
        "confirmation_email": confirmation_email,
        "created_at": datetime.now().isoformat(),
        "id": len(bookings) + 1,
    }

    bookings.append(booking)
    save_bookings(bookings)

    return booking


def get_all_bookings():
    """Get all bookings"""
    return load_bookings()


def get_booking(booking_id: int):
    """Get a specific booking"""
    bookings = load_bookings()
    for booking in bookings:
        if booking.get("id") == booking_id:
            return booking
    return None


def delete_booking(booking_id: int):
    """Delete a booking"""
    bookings = load_bookings()
    bookings = [b for b in bookings if b.get("id") != booking_id]
    save_bookings(bookings)
    return True
