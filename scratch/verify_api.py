import sys
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add CWD to system path to import app modules
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.enums.roles import UserRole
from app.base import Base

# Setup a clean, isolated SQLite in-memory database for rapid verification
# This guarantees we test our SQL queries and relationships without polluting the Supabase DB!
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Global variable to simulate different authenticated user IDs (using UUIDs prevents DetachedInstanceError)
mock_authenticated_user_id = None

from fastapi import Depends
from sqlalchemy.future import select

async def override_get_current_user(db: AsyncSession = Depends(get_db)):
    global mock_authenticated_user_id
    if not mock_authenticated_user_id:
        raise Exception("Mock user ID not configured for this test step.")
    result = await db.execute(select(User).filter(User.id == mock_authenticated_user_id))
    user = result.scalars().first()
    return user

# Mock Supabase Storage upload method to run locally without hitting the real network
import app.supabase as supabase_module
supabase_module.upload_to_storage = lambda bucket_name, file_path, file_bytes, content_type: (
    f"https://mock-supabase.co/storage/v1/object/public/{bucket_name}/{file_path}"
)

# Test client
client = TestClient(app)

# Helper to format terminal output colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS] {message}{Colors.END}")

def log_failure(message: str, error: str = ""):
    print(f"{Colors.RED}[FAILED] {message}{Colors.END}")
    if error:
        print(f"  Details: {error}")

async def run_verification():
    global mock_authenticated_user_id

    print(f"\n{Colors.BOLD}{Colors.BLUE}=== RUNNING BACKEND FLOW VERIFICATION ==={Colors.END}\n")

    # 1. Initialize memory database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log_success("Test database tables created.")
    except Exception as e:
        log_failure("Failed to initialize test database.", str(e))
        return

    # Override database dependency in FastAPI
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    # 2. Seed mock users into the in-memory database
    admin_id = uuid4()
    organizer_id = uuid4()
    customer_id = uuid4()

    admin_user = User(id=admin_id, email="admin@test.com", first_name="System", last_name="Admin", role=UserRole.ADMIN)
    organizer_user = User(id=organizer_id, email="organizer@test.com", first_name="Event", last_name="Planner", role=UserRole.ORGANIZER)
    customer_user = User(id=customer_id, email="customer@test.com", first_name="John", last_name="Doe", role=UserRole.USER)

    async with TestingSessionLocal() as session:
        session.add(admin_user)
        session.add(organizer_user)
        session.add(customer_user)
        await session.commit()
    log_success("Mock users (Admin, Organizer, Customer) seeded.")

    # -------------------------------------------------------------
    # TEST 1: Venue Creation & Role Access
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Verification Step 1: Venues CRUD ---{Colors.END}")
    
    venue_payload = {
        "name": "Grand Symphony Hall",
        "location": "Downtown 5th Ave",
        "capacity": 100
    }

    # A. Customer tries to create venue (should fail with 403 Forbidden)
    mock_authenticated_user_id = customer_id
    res = client.post("/venues", json=venue_payload)
    if res.status_code == 403:
        log_success("RBAC block: Customer forbidden from creating venue.")
    else:
        log_failure(f"RBAC failed: Customer created venue (Status: {res.status_code})")

    # B. Admin creates venue (should succeed)
    mock_authenticated_user_id = admin_id
    res = client.post("/venues", json=venue_payload)
    if res.status_code == 201:
        venue_id = res.json()["id"]
        log_success(f"Admin created venue: {res.json()['name']} (ID: {venue_id})")
    else:
        log_failure("Admin failed to create venue", res.text)
        return

    # C. Try to create a duplicate venue (should fail with 400 Bad Request)
    res = client.post("/venues", json=venue_payload)
    if res.status_code == 400:
        log_success("Duplicate Venue protection verified (returned 400).")
    else:
        log_failure(f"Duplicate Venue check failed (Status: {res.status_code})")

    # -------------------------------------------------------------
    # TEST 2: Event Bounds & Capacity Validations
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Verification Step 2: Event Scheduling & Rules ---{Colors.END}")

    # A. Create event in the past (should fail with 400)
    mock_authenticated_user_id = organizer_id
    past_event_payload = {
        "title": "Retro Night",
        "description": "Music of the 80s",
        "category": "concert",
        "venue_id": venue_id,
        "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        "end_time": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "total_tickets": 50,
        "ticket_price": "25.00",
        "status": "published"
    }
    res = client.post("/events", json=past_event_payload)
    if res.status_code == 400 and "past" in res.json()["detail"].lower():
        log_success("Event creation blocked for past dates.")
    else:
        log_failure(f"Date check failed: Created event in the past (Status: {res.status_code})", res.text)

    # B. Create event exceeding venue capacity (should fail with 400)
    overcapacity_payload = {
        "title": "Rock Festival",
        "category": "concert",
        "venue_id": venue_id,
        "start_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=3)).isoformat(),
        "total_tickets": 150,  # Exceeds venue capacity of 100
        "ticket_price": "50.00",
        "status": "published"
    }
    res = client.post("/events", json=overcapacity_payload)
    if res.status_code == 400 and "exceed" in res.json()["detail"].lower():
        log_success("Event creation blocked for exceeding venue capacity limit.")
    else:
        log_failure(f"Capacity check failed: Allowed event to exceed venue capacity (Status: {res.status_code})", res.text)

    # C. Create a valid event (should succeed)
    valid_event_payload = {
        "title": "Summer Jazz Fest",
        "description": "Chill outdoor vibes",
        "category": "concert",
        "venue_id": venue_id,
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=4)).isoformat(),
        "total_tickets": 80,  # Below venue capacity of 100
        "ticket_price": "40.00",
        "status": "published"
    }
    res = client.post("/events", json=valid_event_payload)
    if res.status_code == 201:
        event_id = res.json()["id"]
        log_success(f"Organizer created valid event: {res.json()['title']} (ID: {event_id})")
    else:
        log_failure("Organizer failed to create valid event", res.text)
        return

    # -------------------------------------------------------------
    # TEST 3: Booking Concurrency & Limit Validations
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Verification Step 3: Ticket Purchases & Inventory Check ---{Colors.END}")

    # A. Book tickets (should succeed, verify pricing math)
    mock_authenticated_user_id = customer_id
    booking_payload = {
        "event_id": event_id,
        "num_tickets": 5
    }
    res = client.post("/bookings", json=booking_payload)
    if res.status_code == 201:
        booking_data = res.json()
        booking_id = booking_data["id"]
        # Expected price: 5 tickets * $40.00 = $200.00
        if float(booking_data["total_price"]) == 200.00:
            log_success(f"Customer purchased 5 tickets. Total price correctly calculated: ${booking_data['total_price']}")
        else:
            log_failure(f"Math check failed: expected $200.00, got ${booking_data['total_price']}")
    else:
        log_failure("Failed to purchase tickets", res.text)
        return

    # B. Try to purchase more tickets than are available (should fail with 400)
    # Tickets remaining: 80 total - 5 booked = 75 available. Requesting 80.
    excess_booking_payload = {
        "event_id": event_id,
        "num_tickets": 80
    }
    res = client.post("/bookings", json=excess_booking_payload)
    if res.status_code == 400 and "not enough" in res.json()["detail"].lower():
        log_success("Booking blocked due to insufficient ticket availability.")
    else:
        log_failure(f"Inventory check failed: allowed selling over event limit (Status: {res.status_code})", res.text)

    # -------------------------------------------------------------
    # TEST 4: Booking Cancellations & Restore Inventory
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Verification Step 4: Booking Cancellations ---{Colors.END}")

    # A. User cancels booking (should succeed and restore tickets)
    res = client.post(f"/bookings/{booking_id}/cancel")
    if res.status_code == 200 and res.json()["status"] == "cancelled":
        log_success("Booking cancelled successfully.")
    else:
        log_failure("Failed to cancel booking", res.text)
        return

    # B. Double check that tickets are restored by trying to book 80 tickets again
    # Since 5 tickets were restored, all 80 should be available again. Requesting 80 should succeed!
    res = client.post("/bookings", json={"event_id": event_id, "num_tickets": 80})
    if res.status_code == 201:
        second_booking_id = res.json()["id"]
        log_success("Inventory correctly restored after booking cancellation.")
    else:
        log_failure(f"Inventory recovery check failed: could not re-book restored tickets (Status: {res.status_code})", res.text)

    # -------------------------------------------------------------
    # TEST 5: Admin Moderation & Dashboard Operations
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Verification Step 5: Admin Moderation & Dashboard Operations ---{Colors.END}")

    # A. Customer tries to access admin dashboard (should fail with 403)
    mock_authenticated_user_id = customer_id
    res = client.get("/admin/dashboard")
    if res.status_code == 403:
        log_success("RBAC block: Customer forbidden from accessing Admin Dashboard.")
    else:
        log_failure(f"RBAC failed: Customer accessed Admin Dashboard (Status: {res.status_code})")

    # B. Admin accesses dashboard (should succeed and return seeded stats)
    mock_authenticated_user_id = admin_id
    res = client.get("/admin/dashboard")
    if res.status_code == 200:
        stats = res.json()
        if stats["total_users"] == 3 and stats["total_tickets_sold"] == 80:
            log_success(f"Admin Dashboard loaded successfully. Total Users: {stats['total_users']}, Tickets Sold: {stats['total_tickets_sold']}")
        else:
            log_failure("Dashboard metrics mismatch", str(stats))
    else:
        log_failure("Admin failed to access Dashboard", res.text)

    # C. Admin updates Customer role to Organizer (should succeed)
    res = client.put(f"/admin/users/{customer_id}/role", json={"role": "organizer"})
    if res.status_code == 200 and res.json()["role"] == "organizer":
        log_success("Admin successfully promoted Customer to Organizer.")
    else:
        log_failure("Admin failed to update user role", res.text)

    # D. Admin cancels event globally (should succeed)
    res = client.post(f"/admin/events/{event_id}/cancel")
    if res.status_code == 200 and res.json()["status"] == "cancelled":
        log_success("Admin successfully force-cancelled event.")
    else:
        log_failure("Admin failed to cancel event", res.text)

    # E. Verify that the customer's confirmed booking has been automatically refunded
    mock_authenticated_user_id = customer_id
    res = client.get(f"/bookings/{second_booking_id}")
    if res.status_code == 200 and res.json()["status"] == "refunded":
        log_success("Cascade validation: Confirmed booking was automatically refunded after event cancellation.")
    else:
        log_failure(f"Cascade validation failed: booking status is {res.json().get('status')} instead of refunded", res.text)

    # -------------------------------------------------------------
    # TEST 6: File Upload & Size Limits
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}--- Verification Step 6: Poster Image Uploads & Limits ---{Colors.END}")

    # A. Customer tries to upload poster (should fail with 403)
    mock_authenticated_user_id = customer_id
    files = {"file": ("poster.jpg", b"dummy_content", "image/jpeg")}
    res = client.post(f"/events/{event_id}/poster", files=files)
    if res.status_code == 403:
        log_success("RBAC block: Customer forbidden from uploading event posters.")
    else:
        log_failure(f"RBAC failed: Customer uploaded event poster (Status: {res.status_code})")

    # B. Organizer uploads unsupported file type (should fail with 400)
    mock_authenticated_user_id = organizer_id
    bad_files = {"file": ("info.txt", b"some plain text", "text/plain")}
    res = client.post(f"/events/{event_id}/poster", files=bad_files)
    if res.status_code == 400 and "unsupported" in res.json()["detail"].lower():
        log_success("Validation block: Blocked upload of unsupported file type (text/plain).")
    else:
        log_failure(f"File validation failed: Allowed unsupported file type upload (Status: {res.status_code})", res.text)

    # C. Organizer uploads file exceeding 5MB (should fail with 400)
    huge_payload = b"0" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
    oversized_files = {"file": ("big_poster.png", huge_payload, "image/png")}
    res = client.post(f"/events/{event_id}/poster", files=oversized_files)
    if res.status_code == 400 and "exceed" in res.json()["detail"].lower():
        log_success("Validation block: Blocked upload of image exceeding 5MB.")
    else:
        log_failure(f"Size validation failed: Allowed oversized file upload (Status: {res.status_code})")

    # D. Organizer uploads a valid image (should succeed)
    valid_files = {"file": ("poster.png", b"fake_png_bytes", "image/png")}
    res = client.post(f"/events/{event_id}/poster", files=valid_files)
    if res.status_code == 200:
        event_data = res.json()
        if "mock-supabase.co" in event_data["event_poster_url"] and "event-posters" in event_data["event_poster_url"]:
            log_success(f"Organizer uploaded poster successfully. Poster URL: {event_data['event_poster_url']}")
        else:
            log_failure("Poster URL response format is incorrect", str(event_data))
    else:
        log_failure("Organizer failed to upload poster", res.text)

    print(f"\n{Colors.BOLD}{Colors.BLUE}=== VERIFICATION COMPLETE ==={Colors.END}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_verification())
