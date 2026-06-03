"""
Supabase client — provides PostgreSQL connection and Storage access.
Replaces both ChromaDB and SQLite.
"""

from supabase import create_client, Client
from config import settings
import logging

logger = logging.getLogger(__name__)

_supabase_client: Client | None = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set. "
                "Create a free project at supabase.com."
            )
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY,
        )
        logger.info("Supabase client initialised")
    return _supabase_client
