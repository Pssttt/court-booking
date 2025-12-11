"""
Booking Storage Service
Persists bookings to Database (PostgreSQL)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from app.database import get_db_session, get_db_engine
from app.db_models import Base, Booking as DBBooking

logger = logging.getLogger(__name__)


def ensure_data_dir():
    """Initialize database tables"""
    engine = get_db_engine()
    if engine:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created/verified.")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    else:
        logger.error("Database engine not available. Cannot initialize tables.")


def load_bookings() -> List[Dict[str, Any]]:
    """Load bookings from database"""
    session = get_db_session()
    if session:
        try:
            bookings = session.query(DBBooking).all()
            result = []
            for b in bookings:
                # Convert SQLAlchemy model to dict
                b_dict = {
                    "id": b.id,
                    "p1": b.p1,
                    "p2": b.p2,
                    "p3": b.p3,
                    "court": b.court,
                    "submit_time": b.submit_time,
                    "scheduled_datetime": b.scheduled_datetime.isoformat()
                    if b.scheduled_datetime
                    else None,
                    "confirmation_email": b.confirmation_email,
                    "phone": b.phone,
                    "student_id": b.student_id,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                    "booking_name": b.booking_name,
                    "booking_email": b.booking_email,
                    "status": b.status,
                }
                result.append(b_dict)
            return result
        except Exception as e:
            logger.error(f"DB Load Error: {e}")
            return []
        finally:
            session.close()
    return []


def add_booking(
    p1: str,
    p2: str,
    p3: str,
    court: str,
    submit_time: str,
    confirmation_email: Optional[str] = None,
    scheduled_datetime: Optional[str] = None,
    phone: Optional[str] = None,
    student_id: Optional[str] = None,
):
    """Add a new booking"""

    session = get_db_session()
    if not session:
        logger.error("No database session available for adding booking")
        raise RuntimeError("Database unavailable")

    try:
        booking_name = p1 if confirmation_email else None
        booking_email = confirmation_email if confirmation_email else None

        sched_dt = None
        if scheduled_datetime:
            try:
                sched_dt = datetime.fromisoformat(scheduled_datetime)
            except (ValueError, TypeError):
                pass

        new_booking = DBBooking(
            p1=p1,
            p2=p2,
            p3=p3,
            court=court,
            submit_time=submit_time,
            scheduled_datetime=sched_dt,
            confirmation_email=confirmation_email,
            phone=phone,
            student_id=student_id,
            booking_name=booking_name,
            booking_email=booking_email,
            created_at=datetime.now(),
            status="pending",
        )
        session.add(new_booking)
        session.commit()
        session.refresh(new_booking)

        return {
            "id": new_booking.id,
            "p1": new_booking.p1,
            "p2": new_booking.p2,
            "p3": new_booking.p3,
            "court": new_booking.court,
            "submit_time": new_booking.submit_time,
            "scheduled_datetime": new_booking.scheduled_datetime.isoformat()
            if new_booking.scheduled_datetime
            else None,
            "confirmation_email": new_booking.confirmation_email,
            "phone": new_booking.phone,
            "student_id": new_booking.student_id,
            "created_at": new_booking.created_at.isoformat(),
            "booking_name": new_booking.booking_name,
            "booking_email": new_booking.booking_email,
            "status": new_booking.status,
        }
    except Exception as e:
        logger.error(f"DB Add Error: {e}")
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_bookings():
    """Get all bookings"""
    return load_bookings()


def get_booking(booking_id: int):
    """Get a specific booking"""
    session = get_db_session()
    if session:
        try:
            b = session.query(DBBooking).filter(DBBooking.id == booking_id).first()
            if b:
                return {
                    "id": b.id,
                    "p1": b.p1,
                    "p2": b.p2,
                    "p3": b.p3,
                    "court": b.court,
                    "submit_time": b.submit_time,
                    "scheduled_datetime": b.scheduled_datetime.isoformat()
                    if b.scheduled_datetime
                    else None,
                    "confirmation_email": b.confirmation_email,
                    "phone": b.phone,
                    "student_id": b.student_id,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                    "booking_name": b.booking_name,
                    "booking_email": b.booking_email,
                    "status": b.status,
                }
            return None
        except Exception as e:
            logger.error(f"DB Get Error: {e}")
            return None
        finally:
            session.close()
    return None


def update_booking_status(booking_id: int, new_status: str) -> bool:
    """Update the status of a specific booking"""
    session = get_db_session()
    if not session:
        logger.error("No database session available for updating booking status")
        return False
    try:
        booking = session.query(DBBooking).filter(DBBooking.id == booking_id).first()
        if booking:
            booking.status = new_status
            session.commit()
            logger.info(f"Booking {booking_id} status updated to {new_status}")
            return True
        logger.warning(f"Booking {booking_id} not found for status update")
        return False
    except Exception as e:
        logger.error(f"DB Update Status Error for booking {booking_id}: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def delete_booking(booking_id: int):
    """Delete a booking"""
    session = get_db_session()
    if session:
        try:
            b = session.query(DBBooking).filter(DBBooking.id == booking_id).first()
            if b:
                session.delete(b)
                session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"DB Delete Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    return False


def delete_old_bookings(days: int = 5) -> int:
    """Delete bookings older than X days"""
    session = get_db_session()
    if session:
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = (
                session.query(DBBooking)
                .filter(DBBooking.created_at < cutoff_date)
                .delete()
            )
            session.commit()
            return deleted_count
        except Exception as e:
            logger.error(f"DB Cleanup Error: {e}")
            session.rollback()
            return 0
        finally:
            session.close()
    return 0
