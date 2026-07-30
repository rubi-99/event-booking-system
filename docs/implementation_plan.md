# Implementation Plan: Venues, Events, & Bookings Integration

This phase integrates Venues and Events Services/Routers and introduces the core **Booking Engine** with strict transaction control to handle concurrency.

---

## User Review Required

> [!IMPORTANT]
> **Pessimistic Concurrency Locking**: To prevent double-booking or overselling tickets when multiple users try to buy at the exact same millisecond, we will lock the event record during booking creation using SQLAlchemy's `with_for_update()`.
> Since we removed the `available_tickets` column from the database model, we will calculate available tickets dynamically inside the locked transaction by fetching:
> `available_tickets = event.total_tickets - SUM(tickets_booked where status='confirmed')`.

---

## Proposed Changes

### 1. Enums & Models

#### [NEW] [booking.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/enums/booking.py)
*   Create a string enum representing the state of a booking:
    ```python
    class BookingStatus(str, Enum):
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
    ```

#### [NEW] [booking.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/models/booking.py)
*   Define the `Booking` database model:
    *   `id: Mapped[UUID]` (Primary Key, default `uuid.uuid4`)
    *   `user_id: Mapped[UUID]` (Foreign Key to `users.id`)
    *   `event_id: Mapped[UUID]` (Foreign Key to `events.id`)
    *   `tickets_booked: Mapped[int]` (Integer, positive)
    *   `total_price: Mapped[Decimal]` (Numeric(10, 2))
    *   `status: Mapped[BookingStatus]` (Stored as String Enum)
    *   Inherits `Base` and `TimestampMixin`.
    *   Relationships: `event: Mapped["Event"] = relationship("Event")`, `user: Mapped["User"] = relationship("User")`

---

### 2. Validation Schemas (Pydantic v2)

#### [NEW] [booking.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/schemas/booking.py)
*   Define the serialization schemas:
    *   `BookingCreate`: Contains `event_id: UUID` and `tickets_booked: int = Field(..., gt=0)`.
    *   `BookingResponse`: Contains the fields `id`, `user_id`, `event_id`, `tickets_booked`, `total_price`, `status`, `created_at`, `updated_at`. Optionally includes a nested `EventResponse` under `event` attribute.

---

### 3. Database Repositories

#### [NEW] [booking_repository.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/repositories/booking_repository.py)
*   Implement database queries for bookings:
    *   `create()`: Creates a new booking.
    *   `get_by_id()`: Fetches a booking by its UUID (with joined loading of `event`).
    *   `get_by_user()`: Fetches all bookings made by a specific user.
    *   `get_booked_tickets_count()`: Calculates the total confirmed tickets booked for an event:
        `SELECT SUM(tickets_booked) FROM bookings WHERE event_id = :event_id AND status = 'confirmed'`
    *   `update()`: Updates the booking record.

---

### 4. Orchestrating Services

#### [NEW] [venue_service.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/services/venue_service.py)
*   CRUD service logic for venues (fetching, creating, updating, deleting).

#### [NEW] [event_service.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/services/event_service.py)
*   Coordinate event catalog rules:
    *   **Create/Update Validations**: Verify that `end_time` is after `start_time` and that the event is not scheduled in the past.
    *   Verify the venue exists, and that `total_tickets` does not exceed the maximum capacity of the venue.

#### [NEW] [booking_service.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/services/booking_service.py)
*   Handles transaction logic for booking operations:
    *   `create_booking()`:
        1.  Start database transaction.
        2.  Lock the target Event record using `with_for_update()`.
        3.  Check event status (must be `published`) and date (cannot book past events).
        4.  Calculate `booked_tickets` count and check if the event has enough available tickets:
            `available_tickets = event.total_tickets - booked_tickets`
            If `requested_tickets > available_tickets`, raise `HTTP 400 Bad Request`.
        5.  Insert the new `Booking` in Postgres with status `confirmed` and `total_price = event.ticket_price * tickets_booked`.
        6.  Commit transaction.
    *   `cancel_booking()`:
        1.  Fetch booking by ID.
        2.  Verify the user is the booking owner or an admin.
        3.  Ensure the event has not started yet.
        4.  Update status to `cancelled` and commit.

---

### 5. API Routing Controllers

#### [NEW] [venues.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/routers/venues.py)
*   `POST /venues` (Admin only)
*   `GET /venues/{id}` (Public)
*   `GET /venues` (Public)
*   `PUT /venues/{id}` (Admin only)
*   `DELETE /venues/{id}` (Admin only)

#### [NEW] [events.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/routers/events.py)
*   `POST /events` (Organizer or Admin)
*   `GET /events/{id}` (Public)
*   `GET /events` (Public - filters by status, category, venue, search)
*   `PUT /events/{id}` (Organizer or Admin)
*   `DELETE /events/{id}` (Organizer or Admin)

#### [NEW] [bookings.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/routers/bookings.py)
*   `POST /bookings` (Authenticated Customers/Organizers/Admins)
*   `GET /bookings/my` (Authenticated - gets current user's booking history)
*   `GET /bookings/{id}` (Authenticated - only owner or admin)
*   `POST /bookings/{id}/cancel` (Authenticated - only owner or admin)

#### [MODIFY] [main.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/main.py)
*   Register the new routers in the FastAPI app: `venues`, `events`, `bookings`.
*   Import `Venue`, `Event`, and `Booking` models inside the `init_db()` lifespan block so SQLAlchemy registers and creates their tables on startup.

---

## Verification Plan

### Manual Verification
1.  **Start Uvicorn**: Ensure the server boots without import/syntax errors.
2.  **Table Creation**: Check that `venues`, `events`, and `bookings` tables are correctly initialized in Postgres.
3.  **Endpoint Testing**:
    *   Create a venue (Admin role).
    *   Create an event (Organizer role) assigned to that venue. Verify date and capacity constraint errors return properly.
    *   List events as public visitor (verify joins work).
    *   Book tickets for the event as a customer (verify concurrency checks and price calculations).
    *   Cancel the booking.
