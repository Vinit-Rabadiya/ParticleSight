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

    # Mark any analyses that were left stuck in pending/running as failed.
    # This happens when Render restarts the server mid-analysis — the background
    # task dies but the DB record stays as "running" forever without this cleanup.
    try:
        from app.database import engine
        from app.models.tables import Analysis
        from sqlmodel import Session, select
        with Session(engine) as session:
            stuck = session.exec(
                select(Analysis).where(Analysis.status.in_(["pending", "running"]))
            ).all()
            for analysis in stuck:
                analysis.status = "failed"
                analysis.error_message = "Server restarted while analysis was in progress. Please re-run."
                session.add(analysis)
            if stuck:
                session.commit()
                print(f"Marked {len(stuck)} stuck analysis/analyses as failed.")
    except Exception as e:
        print(f"Could not clean up stuck analyses: {e}")

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
