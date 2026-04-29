from fastapi import FastAPI
from app.database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the CERNSight API...")
    init_db()
    print("database initialized successfully.")
    yield
    print("Shutting down the CERNSight API...")

app = FastAPI(title="CERNSight API", lifespan=lifespan)
@app.get("/")
async def root():
    return {"message": "Welcome to the CERNSight API!",
            "status":"online",
            "system":"CERNSight"}