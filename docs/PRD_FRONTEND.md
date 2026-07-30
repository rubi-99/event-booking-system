# Event Management System — Frontend PRD

## 1. Overview

A web application that allows users to discover events, purchase tickets, and manage their bookings. Administrators and organizers can create and manage venues, events, and user roles.

**Backend:** FastAPI + Supabase + PostgreSQL (existing)  
**Frontend:** To be built (SPA)

---

## 2. User Personas & Roles

| Role | Description | Key permissions |
|---|---|---|
| **Guest** | Unauthenticated visitor | Browse events & venues |
| **User** | Registered customer | Browse, book tickets, cancel own bookings |
| **Organizer** | Event creator | Create/update/delete own events |
| **Admin** | System administrator | Manage venues, promote users, refund bookings |

---

## 3. Functional Requirements

### 3.1 Authentication

| ID | Requirement | Role |
|---|---|---|
| F-A1 | User can sign up with email, password, first/last name | Guest |
| F-A2 | User can log in and receive a JWT token | Guest |
| F-A3 | User can view their profile | User+ |
| F-A4 | User can update their first/last name | User+ |
| F-A5 | User can log out | User+ |
| F-A6 | Admin can promote a user to organizer or admin | Admin |

### 3.2 Venue Management

| ID | Requirement | Role |
|---|---|---|
| F-V1 | Anyone can browse the list of all venues | Guest+ |
| F-V2 | Anyone can view a single venue's details | Guest+ |
| F-V3 | Admin can create a new venue (name, location, capacity) | Admin |
| F-V4 | Admin can update venue details | Admin |
| F-V5 | Admin can delete a venue | Admin |

### 3.3 Event Management

| ID | Requirement | Role |
|---|---|---|
| F-E1 | Anyone can browse events with filters (category, search, status) | Guest+ |
| F-E2 | Anyone can view a single event with venue & organizer details | Guest+ |
| F-E3 | Organizer/Admin can create an event (title, desc, category, venue, time, tickets, price) | Organizer+ |
| F-E4 | Organizer can only update their own events; Admin can update any | Organizer+ |
| F-E5 | Organizer can only delete their own events; Admin can delete any | Organizer+ |
| F-E6 | Organizer/Admin can upload an event poster image (JPEG, PNG, WebP, max 5MB) | Organizer+ |

### 3.4 Booking Management

| ID | Requirement | Role |
|---|---|---|
| F-B1 | Authenticated user can book tickets for a published event | User+ |
| F-B2 | User can view all their own bookings | User+ |
| F-B3 | User can view a single booking (event + user details) | User+ |
| F-B4 | User can cancel their own booking (before event starts) | User+ |
| F-B5 | Admin can refund any booking | Admin |
| F-B6 | Booking shows status (confirmed / cancelled / refunded) with total price | User+ |

### 3.5 Admin Dashboard

| ID | Requirement | Role |
|---|---|---|
| F-D1 | Admin can list all users | Admin |
| F-D2 | Admin can promote/demote any user's role | Admin |
| F-D3 | Admin can view all bookings across all users | Admin |
| F-D4 | Admin can refund any booking | Admin |

---

## 4. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | **SPA**: Single-page application with client-side routing |
| NFR-2 | **Responsive**: Works on desktop, tablet, and mobile (320px+) |
| NFR-3 | **Auth persist**: JWT stored in httpOnly cookie or localStorage; auto-attach to requests |
| NFR-4 | **Loading states**: Skeleton loaders or spinners on every data fetch |
| NFR-5 | **Error handling**: User-friendly error messages for all API failures (toast/alert) |
| NFR-6 | **Optimistic UI**: Booking creation/cancellation should feel instant |
| NFR-7 | **Accessibility**: WCAG AA compliance (contrast, focus, labels) |
| NFR-8 | **Performance**: Lighthouse score ≥ 90, bundle size ≤ 300KB (gzip) |

---

## 5. Tech Stack Recommendations

| Layer | Technology |
|---|---|
| **Framework** | React 18+ with TypeScript |
| **Routing** | React Router v6 |
| **State management** | React Query (TanStack Query) for server state + Context for auth |
| **HTTP client** | Axios or Fetch with interceptor for Bearer token |
| **UI library** | Tailwind CSS + shadcn/ui (or Ant Design for faster enterprise polish) |
| **Forms** | React Hook Form + Zod for validation |
| **Build tool** | Vite |
| **Testing** | Vitest + React Testing Library + Playwright (E2E) |
| **Linting** | ESLint + Prettier |

---

## 6. Page & Route Map

```
/                        Landing / Home (featured events)
/auth/login              Login page
/auth/signup             Signup page

/events                  Browse all events (filters: category, search, status)
/events/:id              Single event detail + book button

/venues                  Browse all venues
/venues/:id              Single venue detail

/me                      My profile
/me/bookings             My bookings list
/me/bookings/:id         Single booking detail

/admin                   Admin dashboard (stats overview)
/admin/users             Manage users (promote/demote)
/admin/venues            Manage venues (CRUD)
/admin/events            Manage all events
/admin/bookings          Manage all bookings

/organizer/events        My events (organizer)
/organizer/events/new    Create event
/organizer/events/:id/edit   Edit event
```

---

## 7. High-Level Component Tree

```
App
├── Layout
│   ├── Navbar (role-aware menu)
│   ├── ToastContainer
│   └── Outlet (page content)
│
├── Pages
│   ├── HomePage
│   │   └── FeaturedEvents (carousel/grid)
│   │
│   ├── AuthPage
│   │   ├── LoginForm
│   │   └── SignupForm
│   │
│   ├── EventListPage
│   │   ├── EventFilters (category, search, status)
│   │   └── EventCard[] → paginated grid
│   │
│   ├── EventDetailPage
│   │   ├── EventInfo (title, desc, time, price)
│   │   ├── VenueCard (name, location, capacity)
│   │   ├── OrganizerCard
│   │   ├── BookingWidget (ticket count selector + book button)
│   │   └── PosterImage
│   │
│   ├── VenueListPage
│   │   └── VenueCard[]
│   │
│   ├── VenueDetailPage
│   │   └── VenueInfo + EventListAtVenue
│   │
│   ├── ProfilePage
│   │   ├── ProfileForm (first_name, last_name)
│   │   └── MyBookingsList
│   │
│   ├── BookingDetailPage
│   │   ├── BookingStatusBadge
│   │   └── CancelButton / RefundButton (role-gated)
│   │
│   ├── AdminDashboard
│   │   ├── StatsCards (total users, events, bookings, revenue)
│   │   ├── UserTable + PromoteDropdown
│   │   └── BookingTable + RefundButton
│   │
│   └── OrganizerEventForm (create/edit)
│       ├── EventFormFields
│       ├── VenueSelector
│       └── PosterUpload
│
└── Shared Components
    ├── Button, Input, Select, Modal, Table, Badge, Card
    ├── Skeleton (loading)
    ├── EmptyState
    ├── ErrorBoundary
    └── RoleGate (conditional render by role)
```

---

## 8. Auth Flow

```
[Login/Signup]
    │
    ▼
[POST /auth/login] or [POST /auth/signup]
    │
    ▼
[Receive { access_token, user }]
    │
    ├── Store token in localStorage / memory
    ├── Set AuthContext { user, role, token }
    └── Redirect to dashboard / home

[Subsequent requests]
    │
    ├── Axios interceptor reads token from context
    ├── Attaches Authorization: Bearer <token>
    └── On 401 → clear auth → redirect to /auth/login
```

---

## 9. Key UX States (Every Data-Fetching Component)

Every component that fetches data must handle 4 states:

| State | UI |
|---|---|
| **Loading** | Skeleton / spinner |
| **Empty** | Illustrative empty state + CTA |
| **Error** | Error message + retry button |
| **Success** | Render data |

---

## 10. API Integration Points

All endpoints are documented in `API_REFERENCE.md`. The frontend should:

- Base URL: from environment variable `VITE_API_URL` (default `http://localhost:8000`)
- Auth: Bearer token injected via Axios interceptor
- On 401: clear auth state and redirect to login
- On 403: show "You don't have permission" toast
- On 422: display field-level validation errors from `detail[].msg`
