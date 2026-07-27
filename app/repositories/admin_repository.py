from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.user import User
from app.models.event import Event
from app.models.booking import Booking
from app.enums.booking import BookingStatus

class AdminRepository:
    @staticmethod
    async def get_global_stats(db: AsyncSession) -> dict:
        """
        Fetches global platform aggregates from PostgreSQL using optimized SQL operations.
        """
        # 1. Total registered users
        users_count_result = await db.execute(select(func.count(User.id)))
        total_users = users_count_result.scalar() or 0

        # 2. Total revenue (SUM of active bookings total price)
        revenue_result = await db.execute(
            select(func.sum(Booking.total_price))
            .filter(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]))
        )
        total_revenue = revenue_result.scalar() or 0.0

        # 3. Total tickets sold (SUM of active bookings num_tickets)
        tickets_sold_result = await db.execute(
            select(func.sum(Booking.num_tickets))
            .filter(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]))
        )
        total_tickets_sold = tickets_sold_result.scalar() or 0

        # 4. Events breakdown grouped by status
        events_stats_result = await db.execute(
            select(Event.status, func.count(Event.id))
            .group_by(Event.status)
        )
        events_breakdown = {status: count for status, count in events_stats_result.all()}

        return {
            "total_users": total_users,
            "total_revenue": total_revenue,
            "total_tickets_sold": total_tickets_sold,
            "events_breakdown": {
                "draft": events_breakdown.get("draft", 0),
                "published": events_breakdown.get("published", 0),
                "cancelled": events_breakdown.get("cancelled", 0)
            }
        }
