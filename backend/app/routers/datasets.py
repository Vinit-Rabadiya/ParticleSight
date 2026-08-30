from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.tables import Dataset
from app.services.cern_client import CERNClient
import requests

router = APIRouter(tags=["datasets"])

@router.get("/")
def list_datasets(session: Session = Depends(get_session)):
    """Returns all datasets stored in the database."""
    datasets = session.exec(select(Dataset)).all()
    return datasets

@router.get("/preview")
def preview_dataset(cern_url: str):
    """
    Fetches metadata and available CSV files for a CERN record URL.
    Does NOT save anything — used by the frontend to show a preview before adding.
    """
    record_id = CERNClient.extract_record_id(cern_url)
    if not record_id:
        raise HTTPException(status_code=400, detail="Could not extract a record ID from that URL. Make sure it contains /record/{id}.")

    metadata = CERNClient.fetch_dataset_metadata(record_id)

    # Fetch the file list from the CERN API
    try:
        api_url = f"https://opendata.cern.ch/api/records/{record_id}"
        headers = {"User-Agent": "ParticleSight/1.0 (independent open-source project; not affiliated with CERN)"}
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        files = data.get("metadata", {}).get("_files", [])
        csv_files = [
            {
                "name": f["key"],
                "size_mb": round(f["size"] / 1_000_000, 1),
                "url": f"https://opendata.cern.ch/record/{record_id}/files/{f['key']}"
            }
            for f in files
            if f["key"].endswith(".csv")
        ]
    except Exception:
        csv_files = []

    return {
        "record_id": record_id,
        "title": metadata.get("title", f"CERN Dataset {record_id}"),
        "experiment": metadata.get("experiment"),
        "year": metadata.get("year"),
        "doi_url": metadata.get("doi_url"),
        "description": metadata.get("description"),
        "csv_files": csv_files,
    }

@router.post("/")
def add_dataset(cern_record_id: str, csv_url: str, category: str = "particle-physics", session: Session = Depends(get_session)):
    """
    Adds a new dataset to the database.
    Automatically fetches DOI, title, experiment, and year from the CERN API.
    """
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
