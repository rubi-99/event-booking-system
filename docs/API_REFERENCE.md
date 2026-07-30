# Event Management System — API Reference

**Base URL:** `http://localhost:8000` (configurable via `APP_PORT`)

**Auth:** Bearer JWT token — must be sent in `Authorization: Bearer <token>` header for protected endpoints.

---

## Table of Contents

- [Health](#health)
- [Auth](#auth)
- [Venues](#venues)
- [Events](#events)
- [Bookings](#bookings)

---

## Health

### `GET /`

Public health check.

**Response `200`**

```json
{
  "status": "online",
  "message": "Welcome to the Event Management System API. Head over to /docs to explore the interactive API specification."
}
```

---

## Auth

### `POST /auth/signup`

Register a new user. Role defaults to `"user"` regardless of what is sent.

**Auth:** None

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

**Response `201`**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors:** `400` (auth registration failed), `500` (profile creation failed)

---

### `POST /auth/login`

Authenticate and receive a JWT token.

**Auth:** None

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response `200`**

```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**Errors:** `401` (invalid credentials), `500`

---

### `GET /auth/me`

Get the authenticated user's profile.

**Auth:** Bearer (any authenticated user)

**Response `200`**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors:** `401`

---

### `PUT /auth/me`

Update the authenticated user's profile.

**Auth:** Bearer (any authenticated user)

**Request Body**

```json
{
  "first_name": "Jane",
  "last_name": "Doe"
}
```

**Response `200`** — same shape as `GET /auth/me`

**Errors:** `401`, `500`

---

### `POST /auth/logout`

Sign out the current session.

**Auth:** Bearer (any authenticated user)

**Response `204`** — no content

---

### `PUT /auth/users/{user_id}/role`

Update a user's role. **Admin only.**

**Auth:** Bearer (admin)

**Request Body**

```json
{
  "role": "organizer"
}
```

**Response `200`**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "organizer",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors:** `401`, `403`, `404`

---

## Venues

### `GET /venues`

List all venues. Public.

**Auth:** None

**Response `200`**

```json
[
  {
    "id": "uuid",
    "name": "Grand Hall",
    "location": "123 Main Street, New York, NY",
    "capacity": 500,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### `POST /venues`

Create a new venue. **Admin only.**

**Auth:** Bearer (admin)

**Request Body**

```json
{
  "name": "Grand Hall",
  "location": "123 Main Street, New York, NY",
  "capacity": 500
}
```

**Response `201`**

```json
{
  "id": "uuid",
  "name": "Grand Hall",
  "location": "123 Main Street, New York, NY",
  "capacity": 500,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors:** `400` (duplicate name+location), `401`, `403`

---

### `GET /venues/{id}`

Get a single venue by ID. Public.

**Auth:** None

**Response `200`** — same shape as `POST /venues` response

**Errors:** `404`

---

### `PUT /venues/{id}`

Update a venue. **Admin only.**

**Auth:** Bearer (admin)

**Request Body** (all fields optional)

```json
{
  "name": "Grand Hall VIP",
  "capacity": 400
}
```

**Response `200`** — same shape as `POST /venues` response

**Errors:** `404`, `401`, `403`

---

### `DELETE /venues/{id}`

Delete a venue. **Admin only.**

**Auth:** Bearer (admin)

**Response `204`** — no content

**Errors:** `404`, `401`, `403`

---

## Events

### `GET /events`

List all events. Public. Default filter is `status=published`.

**Auth:** None

**Query Parameters** (all optional)

| Param | Type | Description |
|---|---|---|
| `search_query` | string | Search title & description (case-insensitive) |
| `category` | enum | `concert`, `movie`, `sports`, `conference`, `theatre`, `other` |
| `venue_id` | UUID | Filter by venue |
| `status` | string | Default `"published"` |

**Response `200`**

```json
[
  {
    "id": "uuid",
    "title": "Summer Jazz Night",
    "description": "An amazing evening of live jazz music.",
    "category": "concert",
    "event_poster_url": "https://example.com/posters/jazz-night.jpg",
    "venue_id": "uuid",
    "organizer_id": "uuid",
    "start_time": "2026-12-01T19:00:00Z",
    "end_time": "2026-12-01T23:00:00Z",
    "total_tickets": 200,
    "ticket_price": 49.99,
    "status": "published",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "venue": {
      "id": "uuid",
      "name": "Grand Hall",
      "location": "123 Main Street, New York, NY",
      "capacity": 500,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    "organizer": {
      "id": "uuid",
      "email": "organizer@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "organizer",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
]
```

---

### `POST /events`

Create a new event. **Organizer or Admin.**

**Auth:** Bearer (organizer, admin)

**Request Body**

```json
{
  "title": "Summer Jazz Night",
  "description": "An amazing evening of live jazz music.",
  "category": "concert",
  "event_poster_url": "https://example.com/posters/jazz-night.jpg",
  "venue_id": "uuid",
  "start_time": "2026-12-01T19:00:00Z",
  "end_time": "2026-12-01T23:00:00Z",
  "total_tickets": 200,
  "ticket_price": 49.99,
  "status": "published"
}
```

**Validation Rules**

- `end_time` must be after `start_time`
- `start_time` cannot be in the past
- `total_tickets` cannot exceed venue capacity

**Response `201`** — same shape as `GET /events` array item

**Errors:** `400` (validation), `404` (venue not found), `401`, `403`

---

### `GET /events/{id}`

Get a single event by ID. Public.

**Auth:** None

**Response `200`** — same shape as single `GET /events` item

**Errors:** `404`

---

### `PUT /events/{id}`

Update an event. Organizers can only update their own events; Admins can update any.

**Auth:** Bearer (organizer, admin)

**Request Body** (all fields optional)

```json
{
  "title": "Summer Jazz Night - Sold Out",
  "ticket_price": 59.99
}
```

**Response `200`** — same shape as `GET /events` item

**Errors:** `400`, `403` (not owner), `404`, `401`

---

### `DELETE /events/{id}`

Delete an event. Organizers can only delete their own; Admins can delete any.

**Auth:** Bearer (organizer, admin)

**Response `204`** — no content

**Errors:** `403` (not owner), `404`, `401`

---

### `POST /events/{id}/poster`

Upload an event poster image. **Organizer or Admin.**

**Auth:** Bearer (organizer, admin)

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | Image file (JPEG, PNG, WebP, max 5MB) |

**Response `200`**

```json
{
  "event_poster_url": "https://your-project.supabase.co/storage/v1/object/public/event-posters/events/{event_id}/{filename}.jpg"
}
```

**Errors:** `400` (unsupported type or size > 5MB), `403`, `404`, `401`

---

## Bookings

### `POST /bookings`

Create a new booking (purchase tickets). Uses row-level locking to prevent overbooking.

**Auth:** Bearer (any authenticated user)

**Request Body**

```json
{
  "event_id": "uuid",
  "num_tickets": 2
}
```

**Validation Rules**

- Event must be `published`
- Event must not have started yet
- Enough tickets must be available

**Response `201`**

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "event_id": "uuid",
  "num_tickets": 2,
  "total_price": 99.98,
  "status": "confirmed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "event": {
    "id": "uuid",
    "title": "Summer Jazz Night",
    "category": "concert",
    "start_time": "2026-12-01T19:00:00Z",
    "end_time": "2026-12-01T23:00:00Z",
    "total_tickets": 200,
    "ticket_price": 49.99,
    "status": "published",
    "venue": { ... },
    "organizer": { ... }
  },
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user"
  }
}
```

**Errors:** `400` (event not published, already started, not enough tickets), `404`, `401`

---

### `GET /bookings/my`

Get all bookings for the authenticated user.

**Auth:** Bearer (any authenticated user)

**Response `200`**

```json
[
  { ... same shape as single booking above ... }
]
```

**Errors:** `401`

---

### `GET /bookings/{id}`

Get a specific booking by ID. Booking owner or Admin.

**Auth:** Bearer (owner, admin)

**Response `200`** — same shape as `POST /bookings` response

**Errors:** `403` (not owner), `404`, `401`

---

### `POST /bookings/{id}/cancel`

Cancel a booking. Frees tickets back to inventory. Booking owner or Admin.

**Auth:** Bearer (owner, admin)

**Response `200`** — booking with `status: "cancelled"`

**Errors:** `400` (already cancelled, event already started), `403`, `404`, `401`

---

### `POST /bookings/{id}/refund`

Refund a booking. **Admin only.**

**Auth:** Bearer (admin)

**Response `200`** — booking with `status: "refunded"`

**Errors:** `400` (already refunded), `404`, `401`, `403`

---

## Error Response Format

All errors follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

Validation errors (`422`) use FastAPI's standard format:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

---

## Status Code Summary

| Status | Meaning |
|---|---|
| `200` | Success |
| `201` | Created |
| `204` | No content (delete, logout) |
| `400` | Bad request (validation error) |
| `401` | Unauthenticated (missing/invalid token) |
| `403` | Forbidden (insufficient role) |
| `404` | Not found |
| `422` | Validation error (request body/params) |
| `500` | Internal server error |
