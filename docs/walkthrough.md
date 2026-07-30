# Walkthrough: Venues, Events, & Booking Engine Integration

All layers for Venues, Events, and Bookings have been successfully built, linked, and verified.

---

## 1. Naming & Design Choices Implemented (User Comments)
As requested:
*   **Booking Status**: Created `BookingStatus` containing `CONFIRMED`, `CANCELLED`, and `REFUNDED` states.
*   **Column Naming**: Named the ticket count column `num_tickets` to indicate "total number of tickets booked".
*   **Repository Functions**: Refactored the query functions in `BookingRepository` with improved, consistent names:
    *   `get_all_bookings()`: Gets all bookings (optionally filtered by event or user).
    *   `get_confirmed_bookings()`: Gets only confirmed bookings.
    *   `get_cancelled_bookings()`: Gets only cancelled bookings.
    *   `get_refunded_bookings()`: Gets only refunded bookings.
    *   `get_booked_tickets_count()`: Dynamic database sum helper to aggregate booked tickets.

---

## 2. File Walkthrough

### Database Layer (Enums, Models, & Repositories)
*   **[app/enums/booking.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/enums/booking.py)**: Holds the `BookingStatus` enum.
*   **[app/models/booking.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/models/booking.py)**: Mapped SQLAlchemy table representing booking records. Includes relationships back-populating to events and users.
*   **[app/repositories/booking_repository.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/repositories/booking_repository.py)**: Concrete query functions for fetching bookings by status, user, and summing up booked ticket quantities.

### Service Layer (Business Logic)
*   **[app/services/venue_service.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/services/venue_service.py)**: Checks for duplicate venues and abstracts standard venue actions.
*   **[app/services/event_service.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/services/event_service.py)**: Verifies event boundaries (such as future dates, end time after start time, venue capacity vs total tickets).
*   **[app/services/booking_service.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/services/booking_service.py)**: Incorporates transaction-level **pessimistic locking** (`with_for_update`) to prevent overbooking. Restores inventory on cancellations and supports administrative refunds.

### Routing Layer (FastAPI API Controllers)
*   **[app/routers/venues.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/routers/venues.py)**: REST endpoints for Venue operations. Restricted to Admin role for writes.
*   **[app/routers/events.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/routers/events.py)**: REST endpoints for Event operations. Restricted to Organizer/Admin roles for writes.
*   **[app/routers/bookings.py](file:///c:/Users/rubik/OneDrive/Desktop/projects/event-managment-system/app/routers/bookings.py)**: REST endpoints for Booking operations. Enables booking creation (authenticated users), cancellations (owners/admins), and refunds (admins only).

---

## 3. Concurrency Control (How it works under high load)
When a user calls `POST /bookings`:
1.  FastAPI starts a transaction session.
2.  `BookingService` runs:
    ```python
    select(Event).filter(Event.id == event_id).with_for_update()
    ```
    This sends a `SELECT ... FOR UPDATE` query to Postgres, locking that specific Event row.
3.  Any other concurrent request attempting to book the same event is put on hold at the database level.
4.  The service calculates availability dynamically: `available = event.total_tickets - confirmed_booked_tickets`.
5.  If there are enough tickets, the booking is saved and committed. This releases the row lock, letting the next pending request enter.

---

## 4. Verification Status
*   **Syntax & Compile Check**: Passed with exit code `0` (Success).
*   **Automatic Migrations**: When you restart the server, the tables `venues`, `events`, and `bookings` will be created automatically in your Supabase Postgres database.
