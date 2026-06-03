from fastapi import APIRouter
from config import settings
from services.ingestion import get_total_chunk_count
from services.supabase_client import get_supabase
from groq import Groq

router = APIRouter()

@router.get("/health")
def health_check():
    groq_ok = False
    try:
        Groq(api_key=settings.GROQ_API_KEY).models.list()
        groq_ok = True
    except Exception:
        pass

    supabase_ok = False
    try:
        get_supabase().table("documents").select("doc_id").limit(1).execute()
        supabase_ok = True
    except Exception:
        pass

    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "groq_connected": groq_ok,
        "supabase_connected": supabase_ok,
        "primary_model": settings.PRIMARY_LLM,
        "fallback_model": settings.FALLBACK_LLM,
        "embedding_service": "Jina AI API (jina-embeddings-v3, 1024-dim)",
        "vector_db": "Supabase pgvector (PostgreSQL)",
        "total_chunks_indexed": get_total_chunk_count(),
        "monthly_cost": "~£4/month (Railway backend only)",
    }
