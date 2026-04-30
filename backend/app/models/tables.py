from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Dataset(SQLModel, table=True):
    id: str = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    url: str
    category: str

class Analysis(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    dataset_id: str
    findings: str
    anomaly_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
