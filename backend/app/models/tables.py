from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime, timezone
import uuid

class Dataset(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    cern_record_id: str                        # e.g. "700"
    name: str                                  # display name
    url: str                                   # direct CSV download URL
    category: str
    doi: Optional[str] = None                  # e.g. "10.7483/OPENDATA.CMS.A987.B2V2"
    doi_url: Optional[str] = None              # full clickable URL: https://doi.org/10.7483/...
    experiment: Optional[str] = None           # CMS, ATLAS, ALICE, LHCb
    year: Optional[int] = None
    description: Optional[str] = None

class Analysis(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    dataset_id: str = Field(foreign_key="dataset.id")
    # Status flow: pending → running → completed / failed
    status: str = Field(default="pending")
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class AnalysisResult(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    analysis_id: str = Field(foreign_key="analysis.id")
    # JSON columns — store the full output of each service
    distributions: dict = Field(default={}, sa_column=Column(JSON))
    top_correlations: list = Field(default=[], sa_column=Column(JSON))
    anomaly_summary: dict = Field(default={}, sa_column=Column(JSON))
    ai_insights: list = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
