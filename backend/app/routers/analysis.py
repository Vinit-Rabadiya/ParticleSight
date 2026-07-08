from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.database import get_session
from app.models.tables import Dataset, Analysis, AnalysisResult
from app.services.analyser import run_full_analysis
from app.services.cern_client import CERNClient
import asyncio

router = APIRouter(tags=["analysis"])

# This helper runs the full analysis pipeline and saves results to the DB.
# It runs as a background task so the API returns immediately
# and the user doesn't have to wait 30 seconds for a response.
def execute_analysis_pipeline(analysis_id: str, csv_url: str, dataset_name: str):
    from app.database import engine
    from sqlmodel import Session

    with Session(engine) as session:
        analysis = session.get(Analysis, analysis_id)
        if not analysis:
            return

        try:
            # Mark as running
            analysis.status = "running"
            session.add(analysis)
            session.commit()

            # Run the full pipeline — this is the slow part (10-30 seconds)
            # run_full_analysis is async so we run it with asyncio.run()
            results = asyncio.run(run_full_analysis(csv_url, dataset_name))

            # Save results to AnalysisResult table
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                distributions=results["distributions"],
                top_correlations=results["top_correlations"],
                anomaly_summary=results["anomaly_summary"],
                ai_insights=results["ai_insights"]
            )
            session.add(analysis_result)

            # Mark as completed
            analysis.status = "completed"
            analysis.completed_at = datetime.now(timezone.utc)
            session.add(analysis)
            session.commit()

            print(f"Analysis {analysis_id} completed successfully.")

        except Exception as e:
            # Save the error so the frontend can show it
            analysis.status = "failed"
            analysis.error_message = str(e)
            session.add(analysis)
            session.commit()
            print(f"Analysis {analysis_id} failed: {e}")


@router.post("/")
def trigger_analysis(
    dataset_id: str | None = None,
    cern_link: str | None = None,
    background_tasks: BackgroundTasks = None,
    session: Session = Depends(get_session)
):
    """
    Triggers a new analysis for a dataset.
    If a dataset_id is provided, it uses an existing stored dataset.
    Otherwise, it accepts a CERN link, creates a temporary dataset record,
    and starts analysis from that URL.
    """
    if dataset_id:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        analysis_dataset_id = dataset_id
        analysis_url = dataset.url
        analysis_name = dataset.name
    else:
        if not cern_link:
            raise HTTPException(status_code=400, detail="Provide either dataset_id or cern_link.")

        record_id = CERNClient.extract_record_id(cern_link)
        if not record_id:
            raise HTTPException(status_code=400, detail="Could not parse a CERN record ID from the provided link.")

        metadata = CERNClient.fetch_dataset_metadata(record_id)
        new_dataset = Dataset(
            cern_record_id=record_id,
            name=metadata.get("title", f"CERN Dataset {record_id}"),
            url=cern_link,
            category="particle-physics",
            doi=metadata.get("doi"),
            doi_url=metadata.get("doi_url"),
            experiment=metadata.get("experiment"),
            year=metadata.get("year"),
            description=metadata.get("description")
        )
        session.add(new_dataset)
        session.commit()
        session.refresh(new_dataset)

        analysis_dataset_id = new_dataset.id
        analysis_url = new_dataset.url
        analysis_name = new_dataset.name

    new_analysis = Analysis(dataset_id=analysis_dataset_id)
    session.add(new_analysis)
    session.commit()
    session.refresh(new_analysis)

    background_tasks.add_task(
        execute_analysis_pipeline,
        new_analysis.id,
        analysis_url,
        analysis_name
    )

    return {
        "analysis_id": new_analysis.id,
        "status": "pending",
        "message": "Analysis started. Poll GET /api/analysis/{id} to check status."
    }

@router.get("/")
def list_analyses(session:Session = Depends(get_session)):
    return session.exec(select(Analysis).order_by(Analysis.triggered_at.desc())).all()

@router.get("/{analysis_id}")
def get_analysis_status(analysis_id: str, session: Session = Depends(get_session)):
    """
    Returns the current status of an analysis.
    Status: pending → running → completed / failed
    """
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return {
        "analysis_id": analysis.id,
        "dataset_id": analysis.dataset_id,
        "status": analysis.status,
        "triggered_at": analysis.triggered_at,
        "completed_at": analysis.completed_at,
        "error_message": analysis.error_message
    }


@router.get("/{analysis_id}/results")
def get_analysis_results(analysis_id: str, session: Session = Depends(get_session)):
    """
    Returns the full results of a completed analysis.
    Returns 400 if analysis is not yet completed.
    """
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    if analysis.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis is not completed yet. Current status: {analysis.status}"
        )

    result = session.exec(
        select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Results not found.")

    return {
        "analysis_id": analysis_id,
        "distributions": result.distributions,
        "top_correlations": result.top_correlations,
        "anomaly_summary": result.anomaly_summary,
        "ai_insights": result.ai_insights,
        "created_at": result.created_at
    }
