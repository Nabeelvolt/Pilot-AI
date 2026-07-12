"""
Downloads and ingests real Central Lincolnshire planning documents
into the Supabase vector store.

Run once manually: python ingest_real_policies.py
Or called from seed.py on first startup.

All documents are publicly available from:
https://www.n-kesteven.gov.uk/central-lincolnshire/adopted-local-plan-2023/
supplementary-planning-documents-guidance-notes
"""

import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path

import httpx

# Add parent to path so imports work when run directly
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from models.schemas import DocumentMetadata
from services.ingestion import ingest_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real publicly available Central Lincolnshire documents
# Verify these URLs are still live before running — LPA websites occasionally restructure
POLICY_DOCUMENTS = [
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2024-05/"
            "Full%20Applications%20Validation%20List.pdf"
        ),
        "title": "Central Lincolnshire Full Applications Validation List (May 2024)",
        "doc_type": "validation_list",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2024-05-01",
    },
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2024-05/"
            "Householder%20Applications%20Validation%20List.pdf"
        ),
        "title": "Central Lincolnshire Householder Applications Validation List (May 2024)",
        "doc_type": "validation_list",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2024-05-01",
    },
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2024-05/"
            "Listed%20Building%20Consent%20Applications%20Validation%20List.pdf"
        ),
        "title": "Central Lincolnshire Listed Building Consent Validation List (May 2024)",
        "doc_type": "validation_list",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2024-05-01",
    },
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2024-05/"
            "Outline%20Applications%20Validation%20List.pdf"
        ),
        "title": "Central Lincolnshire Outline Applications Validation List (May 2024)",
        "doc_type": "validation_list",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2024-05-01",
    },
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2023-04/"
            "Central%20Lincs%20Energy%20Efficiency%20Design%20Guide%20-%20Final%202023.pdf"
        ),
        "title": "Central Lincolnshire Energy Efficiency Design Guide 2023 (Policies S6/S7/S8)",
        "doc_type": "spd",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2023-04-01",
    },
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2023-08/"
            "Health%20impact%20assessment%20for%20planning%20applications%20guidance%20note.pdf"
        ),
        "title": "Central Lincolnshire Health Impact Assessment Guidance Note (Policy S54)",
        "doc_type": "spd",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2023-08-01",
    },
    {
        "url": (
            "https://www.n-kesteven.gov.uk/sites/default/files/2026-01/"
            "Affordable%20Homes%20Annual%20Statement%20January%202026.pdf"
        ),
        "title": "Central Lincolnshire Affordable Homes Annual Statement January 2026 (Policy S22)",
        "doc_type": "local_plan",
        "lpa_code": "central_lincolnshire",
        "date_effective": "2026-01-01",
    },
]


async def download_pdf(url: str, timeout: int = 60) -> bytes | None:
    """Download a PDF from a URL. Returns bytes or None if failed."""
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "PILOT-AI Research Project / University of Lincoln"},
        ) as client:
            r = await client.get(url)
            if r.status_code == 200 and "pdf" in r.headers.get("content-type", "").lower():
                logger.info(f"Downloaded {len(r.content):,} bytes from {url}")
                return r.content
            else:
                logger.warning(f"Unexpected response {r.status_code} from {url}")
                return None
    except Exception as e:
        logger.error(f"Download failed for {url}: {e}")
        return None


async def ingest_all_real_policies(skip_existing: bool = True):
    """
    Download and ingest all real policy documents.
    skip_existing=True skips documents already in Supabase.
    """
    from services.supabase_client import get_supabase

    supabase = get_supabase()

    # Get already-indexed document titles to avoid re-ingesting
    existing = supabase.table("documents").select("document_title").execute()
    existing_titles = {d["document_title"] for d in (existing.data or [])}

    results = []
    for doc_info in POLICY_DOCUMENTS:
        title = doc_info["title"]

        if skip_existing and title in existing_titles:
            logger.info(f"Skipping (already indexed): {title}")
            results.append({"title": title, "status": "skipped"})
            continue

        logger.info(f"Downloading: {title}")
        pdf_bytes = await download_pdf(doc_info["url"])

        if not pdf_bytes:
            logger.error(f"Failed to download: {title}")
            results.append({"title": title, "status": "download_failed", "url": doc_info["url"]})
            continue

        # Write to temp file for pdfplumber
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            metadata = DocumentMetadata(
                document_title=title,
                doc_type=doc_info["doc_type"],
                lpa_code=doc_info["lpa_code"],
                date_effective=doc_info.get("date_effective"),
            )
            result = ingest_document(
                pdf_path=tmp_path,
                metadata=metadata,
                pdf_bytes=pdf_bytes,
            )
            logger.info(f"Ingested: {title} — {result.chunk_count} chunks ({result.status})")
            results.append({
                "title": title,
                "status": result.status,
                "chunk_count": result.chunk_count,
                "errors": result.errors,
            })
        finally:
            os.unlink(tmp_path)

        # Polite delay between documents
        await asyncio.sleep(1.5)

    return results


if __name__ == "__main__":
    logger.info("Starting ingestion of real Central Lincolnshire policy documents...")
    results = asyncio.run(ingest_all_real_policies())
    logger.info("\n=== INGESTION SUMMARY ===")
    for r in results:
        status = r["status"]
        chunks = r.get("chunk_count", "-")
        logger.info(f"  {status.upper():15} | {chunks:>5} chunks | {r['title'][:60]}")
    logger.info("=== DONE ===")
