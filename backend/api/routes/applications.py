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

@router.get("/detect-constraints")
async def detect_constraints(address: str):
    """
    Auto-detect site constraints from a UK address using free government open data.
    No API key required. Uses Environment Agency, MHCLG Planning Data Platform,
    Historic England, and postcodes.io.
    """
    from services.gis_service import auto_detect_constraints
    if not address or len(address.strip()) < 5:
        raise HTTPException(status_code=422, detail="Please provide a full address including postcode.")
    return await auto_detect_constraints(address.strip())
