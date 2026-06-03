"""
Supabase free tier pauses projects after 1 week of inactivity.
This endpoint is called by a free cron service (cron-job.org)
every 3 days to keep the project active.
"""
from fastapi import APIRouter
from services.supabase_client import get_supabase

router = APIRouter()

@router.get("/keepalive")
def keepalive():
    supabase = get_supabase()
    supabase.table("documents").select("doc_id").limit(1).execute()
    return {"status": "alive", "supabase": "pinged"}
