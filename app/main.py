import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database import init_db
from app.dependencies.rate_limit import limiter
from app.worker import booking_cleaner_worker
from app.routers.auth import router as auth_router
from app.routers.venues import router as venues_router
from app.routers.events import router as events_router
from app.routers.bookings import router as bookings_router
from app.routers.admin import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables on server boot
    try:
        await init_db()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Error initializing database tables: {e}")
        
    # Start background cleaner worker task
    cleaner_task = asyncio.create_task(booking_cleaner_worker(interval_seconds=60))
    yield
    # Shutdown: Clean up background tasks
    cleaner_task.cancel()
    try:
        await cleaner_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Event Management System Backend",
    description="A scalable, high-performance BookMyShow-style backend API built with FastAPI, SQLAlchemy, and Supabase.",
    version="1.0.0",
    lifespan=lifespan
)

# Attach slowapi rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS so frontends can securely connect to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount our routing groups
app.include_router(auth_router)
app.include_router(venues_router)
app.include_router(events_router)
app.include_router(bookings_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the Event Management System API. Head over to /docs to explore the interactive API specification."
    }
