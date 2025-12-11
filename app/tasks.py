"""
Background Tasks
Periodic maintenance and cleanup tasks
"""

import asyncio
import logging
from app.storage import delete_old_bookings
from app.otp_manager import cleanup_expired_otps

logger = logging.getLogger(__name__)


async def run_cleanup_schedule():
    """Background task to run cleanup jobs periodically"""
    while True:
        try:
            logger.info("Running scheduled cleanup...")

            # 1. Clean old bookings (older than 5 days)
            deleted_bookings = delete_old_bookings(days=5)
            if deleted_bookings > 0:
                logger.info(f"Cleaned up {deleted_bookings} old bookings")

            # 2. Clean expired OTPs
            deleted_otps = cleanup_expired_otps()
            if deleted_otps > 0:
                logger.info(f"Cleaned up {deleted_otps} expired OTPs")

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")

        # Wait for 24 hours (86400 seconds)
        await asyncio.sleep(86400)
