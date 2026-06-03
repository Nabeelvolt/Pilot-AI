import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

class Settings:
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PRIMARY_LLM: str = os.getenv("PRIMARY_LLM", "llama-3.3-70b-versatile")
    FALLBACK_LLM: str = os.getenv("FALLBACK_LLM", "gemini-1.5-flash")

    # Jina AI Embeddings (replaces local sentence-transformers)
    JINA_API_KEY: str = os.getenv("JINA_API_KEY", "")
    JINA_EMBEDDING_MODEL: str = os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v3")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "1024"))

    # Supabase (replaces ChromaDB + SQLite + local storage)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "pilot-ai-documents")

    # App
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Retrieval
    RETRIEVAL_TOP_K: int = 12
    RERANK_TOP_K: int = 5

    # Chunking
    CHUNK_SIZE_TOKENS: int = 400
    CHUNK_MIN_TOKENS: int = 80

    # Sample docs (still used for seeding)
    SAMPLE_DOCS_DIR: Path = BASE_DIR / "data" / "sample_docs"

settings = Settings()
