"""
Auto-seeds the system on first run.
Checks if Supabase policy_chunks table has any rows.
If empty: generates sample PDFs and ingests them.
"""
import logging
from pathlib import Path
from datetime import datetime, timedelta
from services.supabase_client import get_supabase
from services.ingestion import ingest_document
from models.schemas import DocumentMetadata
from config import settings

logger = logging.getLogger(__name__)

SAMPLE_DOCS = [
    {
        "filename": "nppf_excerpt.pdf",
        "title":    "National Planning Policy Framework (2024 Edition)",
        "doc_type": "national_policy",
        "lpa_code": "national",
    },
    {
        "filename": "lincoln_local_plan.pdf",
        "title":    "Lincoln Local Plan 2023-2040",
        "doc_type": "local_plan",
        "lpa_code": "lincoln",
    },
    {
        "filename": "lincoln_design_spd.pdf",
        "title":    "Lincoln Design Supplementary Planning Document",
        "doc_type": "spd",
        "lpa_code": "lincoln",
    },
]

DEMO_ANALYSES = [
    {
        "analysis_id": "demo-001",
        "application_ref": "APP/2025/0234",
        "site_address": "12 Newport Road, Lincoln LN1 3DF",
        "application_type": "Full Planning Permission",
        "overall_status": "LIKELY_COMPLIANT",
        "overall_confidence": 0.84,
        "processing_time_seconds": 22.4,
        "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
    },
    {
        "analysis_id": "demo-002",
        "application_ref": "APP/2025/0301",
        "site_address": "Former Mill Site, Canwick Road LN5 8HL",
        "application_type": "Full Planning Permission",
        "overall_status": "REQUIRES_FURTHER_INFO",
        "overall_confidence": 0.71,
        "processing_time_seconds": 31.1,
        "created_at": (datetime.utcnow() - timedelta(days=4)).isoformat(),
    },
    {
        "analysis_id": "demo-003",
        "application_ref": "APP/2025/0187",
        "site_address": "14-18 Brayford Street, Lincoln LN1 3XX",
        "application_type": "Full Planning Permission",
        "overall_status": "LIKELY_NON_COMPLIANT",
        "overall_confidence": 0.78,
        "processing_time_seconds": 28.7,
        "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
    },
    {
        "analysis_id": "demo-004",
        "application_ref": "LBC/2025/0044",
        "site_address": "Greestone Place, Lincoln LN2 1PP",
        "application_type": "Listed Building Consent",
        "overall_status": "REQUIRES_FURTHER_INFO",
        "overall_confidence": 0.65,
        "processing_time_seconds": 19.2,
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
    },
    {
        "analysis_id": "demo-005",
        "application_ref": "APP/2025/0412",
        "site_address": "Outer Circle Road, Lincoln LN2 4JD",
        "application_type": "Change of Use",
        "overall_status": "LIKELY_COMPLIANT",
        "overall_confidence": 0.91,
        "processing_time_seconds": 15.8,
        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
    },
]


def run_seed_if_empty():
    supabase = get_supabase()

    # Check if already seeded
    result = supabase.table("policy_chunks").select("chunk_id", count="exact").limit(1).execute()
    if result.count and result.count > 0:
        logger.info(f"Already seeded ({result.count} chunks in Supabase). Skipping.")
        return

    logger.info("=== First run: seeding Supabase with sample documents... ===")

    docs_dir = settings.SAMPLE_DOCS_DIR
    generate_script = docs_dir / "generate_docs.py"

    if generate_script.exists():
        import subprocess, sys
        logger.info("Generating sample PDFs...")
        subprocess.run([sys.executable, str(generate_script)], cwd=str(docs_dir), check=True)
        logger.info("Sample PDFs generated.")

    for doc_info in SAMPLE_DOCS:
        pdf_path = docs_dir / doc_info["filename"]
        if not pdf_path.exists():
            logger.warning(f"Sample PDF not found: {pdf_path} — skipping")
            continue
        logger.info(f"Ingesting: {doc_info['title']}")
        metadata = DocumentMetadata(
            document_title=doc_info["title"],
            doc_type=doc_info["doc_type"],
            lpa_code=doc_info["lpa_code"],
            date_effective="2024-01-01",
        )
        result = ingest_document(str(pdf_path), metadata)
        logger.info(f"  → {result.chunk_count} chunks ({result.status})")

    # Seed demo history
    existing = supabase.table("analyses").select("analysis_id", count="exact").execute()
    if not existing.count or existing.count == 0:
        supabase.table("analyses").upsert(DEMO_ANALYSES).execute()
        logger.info("Demo analysis history seeded.")

    # Call real policy ingestion
    import asyncio
    from data.ingest_real_policies import ingest_all_real_policies
    try:
        logger.info("Starting ingestion of real Central Lincolnshire policies...")
        asyncio.run(ingest_all_real_policies())
        logger.info("Real policies ingested successfully.")
    except Exception as e:
        logger.error(f"Failed to ingest real policies: {e}")

    logger.info("=== Seeding complete. System ready. ===")
