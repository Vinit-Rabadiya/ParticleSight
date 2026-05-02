from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your backend/.env file.")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from app.models.tables import Dataset, Analysis, AnalysisResult
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
