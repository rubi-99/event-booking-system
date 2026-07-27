import asyncio
import logging
from app.database import async_session_maker
from app.services.booking_service import BookingService

logger = logging.getLogger(__name__)

async def booking_cleaner_worker(interval_seconds: int = 60):
    """
    Background worker process that periodically sweeps the database for expired
    PENDING ticket holds (expires_at < NOW()) and releases them back to inventory.
    Runs continuously during the FastAPI lifespan cycle.
    """
    logger.info(f"Starting ticket hold cleaner worker (interval: {interval_seconds}s)...")
    while True:
        try:
            async with async_session_maker() as db:
                expired_bookings = await BookingService.release_expired_bookings(db)
                if expired_bookings:
                    logger.info(f"Released {len(expired_bookings)} expired ticket hold(s).")
        except asyncio.CancelledError:
            logger.info("Ticket cleaner worker shutting down gracefully.")
            break
        except Exception as e:
            logger.error(f"Error in ticket cleaner worker: {e}")
            
        await asyncio.sleep(interval_seconds)
