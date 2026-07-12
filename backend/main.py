import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routes import applications, documents, health, keepalive, document_analysis
from config import settings
from seed import run_seed_if_empty

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed on first run — must never block app startup
    try:
        run_seed_if_empty()
    except Exception:
        logging.getLogger(__name__).exception(
            "Startup seeding failed (continuing without seed). "
            "Check SUPABASE_URL / SUPABASE_SERVICE_KEY."
        )
    yield

app = FastAPI(
    title="PILOT-AI Demo API",
    description="Zero-cost UK Planning AI demo — Groq + Gemini + local embeddings",
    version="0.1-free",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        settings.FRONTEND_URL,
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(keepalive.router, prefix="/api")
app.include_router(documents.router, prefix="/api/documents")
app.include_router(applications.router, prefix="/api/applications")
app.include_router(document_analysis.router, prefix="/api/document-analysis")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
