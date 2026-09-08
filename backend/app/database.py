from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"
RESET_DB_ON_STARTUP = os.getenv("RESET_DB_ON_STARTUP", "false").strip().lower() == "true"


def create_database_engine(database_url: str | None = None):
    if database_url and database_url.startswith("postgresql"):
        try:
            engine = create_engine(
                database_url,
                # NullPool disables connection pooling entirely.
                # This is the correct setting for serverless/PaaS environments
                # where the database (Neon) scales to zero — pooled connections
                # go stale when Neon suspends, causing 9h9h/7s2a errors.
                # Each request opens and closes its own fresh connection instead.
                poolclass=NullPool,
                echo=False,
                connect_args={
                    "connect_timeout": 10,
                    "sslmode": "require",
                },
            )
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            print("Connected to Neon PostgreSQL successfully.")
            return engine
        except Exception as exc:
            print(f"Postgres unavailable ({exc}); falling back to SQLite.")

    sqlite_url = f"sqlite:///{DB_PATH}"
    return create_engine(
        sqlite_url,
        echo=False,
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
