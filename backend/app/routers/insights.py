from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.tables import AnalysisResult

router = APIRouter(tags = ["datasets"])

@router.get("/api/insights/{analysis_id}")
def get_insights(analysis_id: str, session: Session = Depends(get_session)):
    result = session.exec(select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result.ai_insights