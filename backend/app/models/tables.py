from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Dataset(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    cern_record_id: str                        # e.g. "700"
    name: str
    url: str                                   # direct CSV download URL
    category: str
    doi: Optional[str] = None                  # e.g. "10.7483/OPENDATA.CMS.A987.B2V2"
    doi_url: Optional[str] = None              # full clickable URL: https://doi.org/10.7483/...
    experiment: Optional[str] = None           # CMS, ATLAS, ALICE, LHCb
    year: Optional[int] = None
    description: Optional[str] = None

class Analysis(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    dataset_id: str
    findings: str
    anomaly_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
