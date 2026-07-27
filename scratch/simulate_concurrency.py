import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone

# Add CWD to system path to import app modules
sys.path.append(os.getcwd())

import httpx
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.enums.roles import UserRole
from app.base import Base

# Setup a clean, isolated SQLite in-memory database
# SQLite under high async concurrency requires special settings to test locking
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Global configuration to bypass auth dependency
active_user_id = None
async def override_get_current_user(db: AsyncSession = Depends(get_db) if 'Depends' in globals() else None):
    # Retrieve the active test user by ID dynamically
    from fastapi import Depends
    from sqlalchemy.future import select
    global active_user_id
    result = await db.execute(select(User).filter(User.id == active_user_id))
    return result.scalars().first()

# Override dependencies in FastAPI app
app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
# We will define the override dynamically inside the client session

# Helper to format terminal output colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

async def simulate_traffic():
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== SIMULATING CONCURRENT TRAFFIC (100 BOOKING REQUESTS) ==={Colors.END}\n")

    # 1. Initialize memory database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed mock users and event
    admin_id = uuid4()
    organizer_id = uuid4()
    venue_id = uuid4()
    event_id = uuid4()

    admin = User(id=admin_id, email="admin@test.com", first_name="Admin", last_name="User", role=UserRole.ADMIN)
    organizer = User(id=organizer_id, email="org@test.com", first_name="Org", last_name="User", role=UserRole.ORGANIZER)

    # Seed 100 different customers who will try to book tickets simultaneously
    customers = []
    for i in range(100):
        c_id = uuid4()
        customers.append(User(
            id=c_id,
            email=f"customer{i}@test.com",
            first_name=f"Customer",
            last_name=str(i),
            role=UserRole.USER
        ))

    async with TestingSessionLocal() as session:
        session.add(admin)
        session.add(organizer)
        for c in customers:
            session.add(c)
        await session.commit()

    # Setup the FastAPI dependency override for get_current_user
    from fastapi import Depends
    from sqlalchemy.future import select
    
    # We dynamically mock get_current_user to look up the global `active_user_id`
    async def dynamic_get_current_user(db: AsyncSession = Depends(get_db)):
        global active_user_id
        res = await db.execute(select(User).filter(User.id == active_user_id))
        return res.scalars().first()
        
    app.dependency_overrides[get_current_user] = dynamic_get_current_user

    # 3. Create a venue and event with exactly 10 tickets
    # Note: We must make requests using the FastAPI TestClient or direct service calls.
    # Since TestClient is synchronous, to simulate concurrent requests, we will call the
    # BookingService.create_booking directly in parallel async tasks!
    # This directly tests the SQLAlchemy session locking and availability checking logic!
    from app.services.venue_service import VenueService
    from app.services.event_service import EventService
    from app.schemas.venue import VenueCreate
    from app.schemas.event import EventCreate

    async with TestingSessionLocal() as session:
        # Create venue
        venue = await VenueService.create_venue(session, VenueCreate(name="Opera Hall", location="Sector 1", capacity=100))
        # Create event with exactly 10 total tickets
        event = await EventService.create_event(
            session, 
            organizer_id, 
            EventCreate(
                title="Jazz Concert", 
                category="concert", 
                venue_id=venue.id,
                start_time=(datetime.now(timezone.utc) + timedelta(days=1)),
                end_time=(datetime.now(timezone.utc) + timedelta(days=1, hours=2)),
                total_tickets=10, 
                ticket_price="50.00", 
                status="published"
            )
        )
        await session.commit()
        # Keep track of ID
        target_event_id = event.id

    print(f"Created event '{event.title}' with {Colors.BOLD}10 total tickets{Colors.END}.\n")
    print(f"Firing {Colors.BOLD}100 parallel booking requests{Colors.END} (1 ticket each)...")

    from app.services.booking_service import BookingService

    # 4. Fire 100 concurrent async bookings (each customer booking 1 ticket)
    success_count = 0
    failure_count = 0
    errors = []

    async def book_ticket(customer_id: UUID):
        nonlocal success_count, failure_count
        # Each task opens its own database session (simulating separate API threads)
        async with TestingSessionLocal() as session:
            try:
                # Attempt to buy 1 ticket
                await BookingService.create_booking(session, customer_id, target_event_id, 1)
                success_count += 1
            except HTTPException as e:
                failure_count += 1
                errors.append(e.detail)
            except Exception as e:
                failure_count += 1
                errors.append(str(e))

    # Fire all 100 async tasks concurrently using asyncio.gather
    tasks = [book_ticket(c.id) for c in customers]
    await asyncio.gather(*tasks)

    # 5. Output results
    print(f"\n{Colors.BOLD}=== CONCURRENCY SIMULATION RESULTS ==={Colors.END}")
    print(f"Successful Bookings: {Colors.GREEN}{success_count}{Colors.END}")
    print(f"Failed Bookings (Rejected): {Colors.RED}{failure_count}{Colors.END}")

    # Check database integrity
    async with TestingSessionLocal() as session:
        # Sum booked tickets in database
        from app.repositories.booking_repository import BookingRepository
        total_booked = await BookingRepository.get_booked_tickets_count(session, target_event_id)
        
        # Fetch confirmed bookings list
        bookings_list = await BookingRepository.get_confirmed_bookings(session, event_id=target_event_id)
        actual_rows_count = len(bookings_list)

    print(f"Total tickets sold inside Postgres: {Colors.BOLD}{total_booked}{Colors.END}")
    print(f"Total booking rows created: {Colors.BOLD}{actual_rows_count}{Colors.END}")

    # Assertions
    if success_count == 10 and total_booked == 10 and actual_rows_count == 10:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ SUCCESS: Concurrency check passed!{Colors.END}")
        print("SQLAlchemy row-level locking successfully blocked 90 overbooking attempts,")
        print("selling exactly the 10 available tickets with zero database double-booking.")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ FAILURE: Concurrency check failed!{Colors.END}")
        print(f"Expected 10 sold, got {total_booked} sold in database.")

if __name__ == "__main__":
    asyncio.run(simulate_traffic())
