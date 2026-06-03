from fastapi import APIRouter, HTTPException
from models.schemas import AnalysisRequest, AnalysisResponse
from services.analysis import analyse_application
from services.supabase_client import get_supabase

router = APIRouter()

@router.post("/analyse", response_model=AnalysisResponse)
def analyse(request: AnalysisRequest):
    if len(request.proposed_development.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Proposed development description must be at least 50 characters."
        )
    return analyse_application(request)

@router.get("/history")
def get_history():
    supabase = get_supabase()
    result = (
        supabase.table("analyses")
        .select("*")
        .order("created_at", desc=True)
        .limit(20)
        .execute()
    )
    return result.data or []
