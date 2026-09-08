from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.database import init_db, RESET_DB_ON_STARTUP
from app.routers import datasets, analysis, insights

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the ParticleSight API...")
    init_db(reset=RESET_DB_ON_STARTUP)
    print("Database initialized successfully.")
    yield
    print("Shutting down the ParticleSight API...")

app = FastAPI(title="ParticleSight API", version="1.0.0", lifespan=lifespan)

# Build allowed origins: always include localhost for dev,
# plus any production frontend URL set via FRONTEND_URL env var.
# Also allow all Vercel preview deployments (*.vercel.app).
_allowed_origins = [
    "http://localhost:5173",
    "https://particle-sight.vercel.app",
]
_frontend_url = os.getenv("FRONTEND_URL", "").strip()
if _frontend_url and _frontend_url not in _allowed_origins:
    _allowed_origins.append(_frontend_url)

# Allow the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://particle-sight.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers — each one handles a group of related endpoints
app.include_router(datasets.router, prefix="/api/datasets")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(insights.router, prefix="/api/insights")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the ParticleSight API!",
        "status": "online",
        "docs": "/docs"
    }
