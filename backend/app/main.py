from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.services.cern_client import CERNClient
from app.services.anomaly import AnomalyDetector

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the ParticleSight API...")
    init_db()
    print("database initialized successfully.")
    yield
    print("Shutting down the ParticleSight API...")

app = FastAPI(title="ParticleSight API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
async def root():
    return {"message": "Welcome to the ParticleSight API!",
            "status": "online",
            "system": "ParticleSight"}

@app.get("/analyze")
async def analyze_physics():
    """
    Triggers the physics engine to load CERN data and run anomaly detection.
    """
    df = CERNClient.get_data()
    if df is None:
        return {"error": "Dataset not found in /data folder"}

    anomalies = AnomalyDetector.find_outliers(df)

    return {
        "total_events": len(df),
        "anomalies_count": len(anomalies),
        "anomalies": anomalies.to_dict(orient="records")
    }
