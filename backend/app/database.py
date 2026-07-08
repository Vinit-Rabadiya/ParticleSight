from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def create_database_engine(database_url: str | None = None):
    if database_url and database_url.startswith("postgresql"):
        try:
            engine = create_engine(database_url, echo=True)
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            return engine
        except Exception as exc:
            print(f"Postgres unavailable at {database_url}; falling back to SQLite. {exc}")

    sqlite_url = f"sqlite:///{DB_PATH}"
    return create_engine(
        sqlite_url,
        echo=True,
        connect_args={"check_same_thread": False},
    )


engine = create_database_engine(DATABASE_URL)


def init_db():
    from app.models.tables import Dataset, Analysis, AnalysisResult
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
