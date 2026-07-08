from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db, RESET_DB_ON_STARTUP
from app.routers import datasets, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the ParticleSight API...")
    init_db(reset=RESET_DB_ON_STARTUP)
    print("Database initialized successfully.")
    yield
    print("Shutting down the ParticleSight API...")

app = FastAPI(title="ParticleSight API", version="1.0.0", lifespan=lifespan)

# Allow the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://particlesight.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers — each one handles a group of related endpoints
app.include_router(datasets.router, prefix="/api/datasets")
app.include_router(analysis.router, prefix="/api/analysis")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the ParticleSight API!",
        "status": "online",
        "docs": "/docs"
    }
