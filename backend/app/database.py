from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"
RESET_DB_ON_STARTUP = os.getenv("RESET_DB_ON_STARTUP", "false").strip().lower() == "true"


def create_database_engine(database_url: str | None = None):
    if database_url and database_url.startswith("postgresql"):
        try:
            # Keep local startup responsive when Postgres isn't available.
            engine = create_engine(
                database_url,
                echo=True,
                connect_args={"connect_timeout": 3},
            )
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


def init_db(reset: bool = False):
    from app.models.tables import Dataset, Analysis, AnalysisResult

    if reset:
        SQLModel.metadata.drop_all(engine)

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
