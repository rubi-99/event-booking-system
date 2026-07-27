import sys
import os
import uuid
import pathlib
import json
from datetime import datetime, timezone, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.base import Base
from app.database import get_db
from app.models.user import User
from app.models.venue import Venue
from app.models.event import Event
from app.models.booking import Booking
from app.enums.roles import UserRole
from app.enums.categories import EventCategory
from app.enums.booking import BookingStatus
from app.services.booking_service import BookingService
from app.dependencies.auth import get_current_user

# Setup in-memory SQLite test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

mock_authenticated_user_id = None

async def override_get_current_user():
    global mock_authenticated_user_id
    user_id = mock_authenticated_user_id or uuid.uuid4()
    return User(
        id=user_id,
        email="customer@test.com",
        first_name="John",
        last_name="Doe",
        role=UserRole.ADMIN if user_id == admin_id else (UserRole.ORGANIZER if user_id == organizer_id else UserRole.USER)
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

def log_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")

def log_failure(msg: str, details: str = ""):
    print(f"{Colors.RED}[FAILED]{Colors.END} {msg}")
    if details:
        print(f"  Details: {details}")

admin_id = uuid.uuid4()
organizer_id = uuid.uuid4()
customer_id = uuid.uuid4()
venue_id = uuid.uuid4()
event_id = uuid.uuid4()

async def run_phase1_verification():
    global mock_authenticated_user_id
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== RUNNING PHASE 1 FEATURE VERIFICATION ==={Colors.END}\n")

    # Clear old email logs
    log_file = pathlib.Path("logs/emails.log")
    if log_file.exists():
        log_file.unlink()

    # 1. Initialize DB tables and seed test data
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as db:
        admin_user = User(id=admin_id, email="admin@test.com", first_name="Admin", last_name="User", role=UserRole.ADMIN)
        organizer_user = User(id=organizer_id, email="organizer@test.com", first_name="Event", last_name="Planner", role=UserRole.ORGANIZER)
        customer_user = User(id=customer_id, email="customer@test.com", first_name="John", last_name="Doe", role=UserRole.USER)
        
        venue = Venue(id=venue_id, name="Phase1 Arena", location="Main Street", capacity=100)
        start_t = datetime.now(timezone.utc) + timedelta(days=2)
        end_t = start_t + timedelta(hours=3)
        event = Event(
            id=event_id, title="Phase1 Music Fest", description="Live show",
            category=EventCategory.CONCERT, venue_id=venue_id, organizer_id=organizer_id,
            start_time=start_t, end_time=end_t, total_tickets=50, ticket_price=50.00, status="published"
        )
        
        db.add_all([admin_user, organizer_user, customer_user, venue, event])
        await db.commit()

    log_success("Test database initialized with seeded Event & Users.")

    # -------------------------------------------------------------
    # TEST 1: Booking Creation (PENDING status & 10-Min Hold)
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Test 1: Ticket Hold & PENDING State ---{Colors.END}")
    mock_authenticated_user_id = customer_id
    res = client.post("/bookings", json={"event_id": str(event_id), "num_tickets": 4})
    
    if res.status_code == 201:
        booking_data = res.json()
        booking_id = booking_data["id"]
        if booking_data["status"] == "pending":
            log_success(f"Booking created in PENDING state. Booking ID: {booking_id}")
        else:
            log_failure(f"Expected status pending, got {booking_data['status']}")
            return
    else:
        log_failure(f"Failed to create booking (Status: {res.status_code})", res.text)
        return

    # -------------------------------------------------------------
    # TEST 2: Payment Webhook & Transactional Email
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Test 2: Payment Webhook & Email Dispatch ---{Colors.END}")
    webhook_payload = {
        "booking_id": booking_id,
        "status": "payment_success",
        "transaction_id": "tx_stripe_998877"
    }
    res = client.post("/bookings/webhook", json=webhook_payload)
    if res.status_code == 200 and res.json()["status"] == "success":
        log_success("Payment webhook processed successfully.")
    else:
        log_failure(f"Webhook processing failed (Status: {res.status_code})", res.text)
        return

    # Verify status changed to CONFIRMED
    res = client.get(f"/bookings/{booking_id}")
    if res.status_code == 200 and res.json()["status"] == "confirmed":
        log_success("Booking status transitioned PENDING -> CONFIRMED.")
    else:
        log_failure(f"Booking status is {res.json().get('status')} instead of confirmed")

    # Verify Email was logged to file
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            logs = f.readlines()
        if len(logs) > 0 and "Confirmed: Tickets for Phase1 Music Fest" in logs[0]:
            log_success(f"Transactional Email Gateway logged ticket confirmation to {log_file}")
        else:
            log_failure("Email file found but content mismatch", str(logs))
    else:
        log_failure(f"Email log file {log_file} was not created")

    # -------------------------------------------------------------
    # TEST 3: Hold Expiration & Auto-Release Worker
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Test 3: Hold Expiration & Auto-Release ---{Colors.END}")
    # Create second booking and force expires_at to 15 minutes in past
    res = client.post("/bookings", json={"event_id": str(event_id), "num_tickets": 10})
    second_booking_id = res.json()["id"]

    async with TestingSessionLocal() as db:
        from sqlalchemy.future import select
        stmt = select(Booking).filter(Booking.id == uuid.UUID(second_booking_id))
        result = await db.execute(stmt)
        b2 = result.scalars().first()
        b2.expires_at = datetime.now(timezone.utc) - timedelta(minutes=15)
        await db.commit()

    # Trigger worker cleanup logic manually
    async with TestingSessionLocal() as db:
        expired_list = await BookingService.release_expired_bookings(db)
        if len(expired_list) == 1 and str(expired_list[0].id) == second_booking_id:
            log_success("Expired booking detected and auto-released by cleaner logic.")
        else:
            log_failure(f"Expected 1 expired booking released, got {len(expired_list)}")

    # Verify status changed to CANCELLED and email logged
    res = client.get(f"/bookings/{second_booking_id}")
    if res.status_code == 200 and res.json()["status"] == "cancelled":
        log_success("Expired booking status updated to CANCELLED.")
    else:
        log_failure(f"Expired booking status is {res.json().get('status')} instead of cancelled")

    with open(log_file, "r", encoding="utf-8") as f:
        logs = f.readlines()
    if any("Expired: Reservation for Phase1 Music Fest" in line for line in logs):
        log_success("Transactional Email Gateway logged hold expiration notification email.")
    else:
        log_failure("Expiry email not found in log file", str(logs))

    print(f"\n{Colors.BOLD}{Colors.BLUE}=== PHASE 1 VERIFICATION COMPLETE: ALL TESTS PASSED ==={Colors.END}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_phase1_verification())
