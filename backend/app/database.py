from sqlmodel import SQLModel, create_engine
import os

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def init_db():
    from app.models.tables import Dataset, Analysis
    SQLModel.metadata.create_all(engine)