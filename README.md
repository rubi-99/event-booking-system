# Event Management System Backend 🎟️🚀

A scalable, high-performance, production-ready Event Management & Ticket Booking API built with **FastAPI**, **SQLAlchemy**, **Supabase (PostgreSQL & Auth & Storage)**, and **Redis**.

Designed to support **1 Million active users** and high-concurrency ticket launches (100,000 req/sec) using pessimistic row locking and Redis distributed locks.

---

## ⚡ Features & Capabilities

* **🔐 Authentication & RBAC**: Supabase JWT authentication with local JWKS public key validation. Role-Based Access Control (`USER`, `ORGANIZER`, `ADMIN`).
* **🏢 Venue & Event Management**: Full CRUD for Venues & Events with date window validation, seating capacity limits, compound database indexing, and public catalog search.
* **⏳ 10-Minute Ticket Hold Lifecycle**: Purchases start as `PENDING` holds with a 10-minute expiry timestamp (`expires_at`), preventing overbooking.
* **💳 Payment Gateway Webhook (`POST /bookings/webhook`)**: Handles `payment_success` (transitions `PENDING` $\rightarrow$ `CONFIRMED`) and `payment_failed` (transitions `PENDING` $\rightarrow$ `CANCELLED`).
* **🔄 Automated Expiry Sweep**: Background worker running inside FastAPI `lifespan` sweeps expired holds every 60s and releases tickets back to available inventory.
* **⚡ Redis Caching & Distributed Locks**: Serves catalog searches in $<2\text{ms}$ with smart cache invalidation and handles ticket drops without DB lock contention.
* **✉️ Transactional Email Gateway**: Provider-agnostic gateway (`dev` logger and `production` Resend/SendGrid client) for ticket confirmations and hold expirations.
* **📊 Admin Moderation**: Global dashboard aggregate metrics and force-cancellation with automatic refund cascading.
* **🛡️ Security & Clean Layered Architecture**: `slowapi` rate limiting (`/auth`: 5 req/min, `/bookings`: 20 req/min) and strict 3-tier layering (Routers $\rightarrow$ Services $\rightarrow$ Repositories).

---

## 🛠️ Technology Stack

* **Framework**: FastAPI (Python 3.12)
* **Database & ORM**: PostgreSQL via SQLAlchemy 2.0 (Async Session) & Asyncpg
* **Authentication & Storage**: Supabase Auth (JWT/JWKS) & Supabase Storage Buckets
* **Cache & Locking**: Redis & `redis.asyncio`
* **Rate Limiting**: Slowapi
* **Server**: Uvicorn

---

## 🚀 Quickstart & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/event-management-system.git
cd event-management-system
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
# Or using uv:
uv sync
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Supabase and database credentials:
```bash
cp .env.example .env
```

Example `.env` configuration:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

DATABASE_URL=postgresql+asyncpg://postgres:your-db-password@db.your-project-id.supabase.co:5432/postgres

APP_ENV=development
APP_PORT=8000
SUPABASE_STORAGE_BUCKET=event-posters

EMAIL_PROVIDER=dev
EMAIL_PROVIDER_KEY=your_resend_or_sendgrid_api_key

REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
```

---

## 💻 Running the Application

Start the local Uvicorn development server:
```bash
uvicorn app.main:app --reload --port 8000
```

Access the interactive API documentation in your browser:
* **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Automated Tests

Run the test verification suites:
```bash
python scratch/verify_api.py
python scratch/test_phase1.py
python scratch/test_phase2.py
```

---

## 📁 Project Directory Structure

```text
├── app/
│   ├── main.py                   # App entrypoint, middleware & lifespan setup
│   ├── base.py                   # Declarative SQLAlchemy Base & TimestampMixin
│   ├── config/config.py          # App settings via Pydantic BaseSettings
│   ├── database/                 # Async DB engine & session dependency
│   ├── dependencies/             # Auth JWT/JWKS, RBAC & Redis Locks
│   ├── enums/                    # Enums (UserRole, EventCategory, BookingStatus)
│   ├── models/                   # SQLAlchemy Models (User, Event, Venue, Booking)
│   ├── repositories/             # Persistence Layer (Pure SQL CRUD operations)
│   ├── routers/                  # API Routers / Controllers
│   ├── schemas/                  # Pydantic Schemas (Requests & Responses)
│   ├── services/                 # Business Logic & Transaction Coordination
│   ├── tasks/                    # Async Background Task Queueing
│   ├── email.py                  # Transactional Email Gateway
│   ├── redis.py                  # Redis Caching & Connection Client
│   ├── supabase.py               # Supabase Storage helper
│   └── worker.py                 # Background Ticket Expiry Worker
├── scratch/                      # Automated Test Verification Scripts
├── .env.example                  # Environment Variables Template
├── .gitignore                    # Git Ignore Configuration
├── pyproject.toml                # Dependencies configuration
└── README.md                     # Documentation
```

---

## 📜 License
MIT License. Free for commercial and non-commercial use.