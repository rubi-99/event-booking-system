from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# 1. Create the async engine with connection pooling limits
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.APP_ENV == "development" else False,
    pool_size=20,          # Minimum persistent open connections
    max_overflow=10,       # Maximum extra connections allowed during traffic spikes
    pool_pre_ping=True,    # Test connections before issuing queries
    pool_recycle=3600      # Recycle connections older than 1 hour
)

# 2. Async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Prevents database re-queries when accessing object attributes
)

# 3. FastAPI Dependency to yield sessions dynamically
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# 4. Developer tool to create tables on startup
async def init_db() -> None:
    from app.base import Base
    # Import the models to register them on the Declarative Base metadata
    from app.models.user import User
    from app.models.venue import Venue
    from app.models.event import Event
    from app.models.booking import Booking
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
