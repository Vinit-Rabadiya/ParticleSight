from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.tables import Dataset
from app.services.cern_client import CERNClient

router = APIRouter(tags=["datasets"])

@router.get("/")
def list_datasets(session: Session = Depends(get_session)):
    """Returns all datasets stored in the database."""
    datasets = session.exec(select(Dataset)).all()
    return datasets

@router.post("/")
def add_dataset(cern_record_id: str, csv_url: str, category: str = "particle-physics", session: Session = Depends(get_session)):
    """
    Adds a new dataset to the database.
    Automatically fetches DOI, title, experiment, and year from the CERN API.
    """
    # Fetch metadata from CERN API — this gets the DOI automatically
    metadata = CERNClient.fetch_dataset_metadata(cern_record_id)

    new_dataset = Dataset(
        cern_record_id=cern_record_id,
        name=metadata.get("title", f"CERN Dataset {cern_record_id}"),
        url=csv_url,
        category=category,
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
def get_dataset(dataset_id: str, session: Session = Depends(get_session)):
    """Returns one dataset by its ID."""
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset
