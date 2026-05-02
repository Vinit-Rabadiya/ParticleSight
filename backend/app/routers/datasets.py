from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.tables import Dataset
from app.services.cern_client import CERNClient


router = APIRouter(prefix="/api/datasets", tags=["datasets"])

@router.get("/")
def list_datasets(session: Session = Depends(get_session)):
    datasets = session.exec(select(Dataset)).all()
    return datasets

@router.post("/")
def add_dataset(cern_id: int, csv_url: str, session: Session = Depends(get_session)):
    metadata = CERNClient.fetch_dataset_metadata(cern_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Dataset not found in CERN Open Data Portal.")
    new_dataset = Dataset(
        cern_record_id=str(cern_id),
        name=metadata.get("name", f"CERN Dataset {cern_id}"),
        csv_url=csv_url,
        category=metadata.get("category", "Unknown"),
        title=metadata.get("title"),
        doi=metadata.get("doi"),
        doi_url=metadata.get("doi_url"),
        experiment=metadata.get("experiment"),
        year=metadata.get("year"),
        description=metadata.get("description")
    )
    session.add(new_dataset)
    session.commit()
    session.refresh(new_dataset)
    return new_dataset

@router.get("/{dataset_id}")
def get_dataset(dataset_id: int, session: Session = Depends(get_session)):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset