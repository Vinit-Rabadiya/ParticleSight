from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.database import get_session
from app.models.tables import Dataset, Analysis, AnalysisResult
from app.services.analyser import run_full_analysis
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
    dataset_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Triggers a new analysis for a dataset.
    Returns immediately with an analysis ID.
    The actual analysis runs in the background.
    Poll GET /api/analysis/{id} to check when it's done.
    """
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # Create an Analysis record with status "pending"
    new_analysis = Analysis(dataset_id=dataset_id)
    session.add(new_analysis)
    session.commit()
    session.refresh(new_analysis)

    # Add the pipeline to background tasks — runs after this function returns
    background_tasks.add_task(
        execute_analysis_pipeline,
        new_analysis.id,
        dataset.url,
        dataset.name
    )

    return {
        "analysis_id": new_analysis.id,
        "status": "pending",
        "message": "Analysis started. Poll GET /api/analysis/{id} to check status."
    }

@router.get("/")
def list_analyses(session:Session = Depends(get_session)):
    return session.exec(Analysis).order_by(Analysis.triggered_at.desc()).all()

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
