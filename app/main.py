
from fastapi import FastAPI

from app.database.base import Base
from app.database.database import engine

# Import all models
from app.models.user import User
from app.models.event import Event
from app.models.booking import Booking

from app.api.user_api import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)

@app.get("/", tags=["Home"])
def root():
    return {
        "message": "Welcome to Event Management System API"
    }