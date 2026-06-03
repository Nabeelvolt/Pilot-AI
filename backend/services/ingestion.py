"""
PDF ingestion pipeline — cloud version.
PDF → chunks → Jina AI embeddings → Supabase pgvector + PostgreSQL.
No local model downloads. No ChromaDB. Runs entirely on cloud.
"""

import uuid
import logging
import time
from pathlib import Path
from typing import List

from config import settings
from models.schemas import DocumentMetadata, IngestionResult
from services.supabase_client import get_supabase
from services.embedding_client import embed_texts
from utils.pdf_extractor import extract_pdf_pages
from utils.chunker import hierarchical_chunk

logger = logging.getLogger(__name__)


def ingest_document(
    pdf_path: str,
    metadata: DocumentMetadata,
    pdf_bytes: bytes = None,
) -> IngestionResult:
    """
    Full ingestion pipeline for one planning PDF.
    Uploads PDF to Supabase Storage, extracts text, chunks,
    embeds with Jina AI, stores vectors in Supabase pgvector.
    """
    doc_id = str(uuid.uuid4())
    supabase = get_supabase()
    errors = []

    try:
        # ── Step 1: Upload PDF to Supabase Storage ──────────────────────────────
        filename = Path(pdf_path).name
        storage_path = f"{metadata.lpa_code}/{metadata.doc_type}/{doc_id}/{filename}"

        if pdf_bytes is None:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

        supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            path=storage_path,
            file=pdf_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"},
        )
        logger.info(f"PDF uploaded to Supabase Storage: {storage_path}")

        # ── Step 2: Extract text ────────────────────────────────────────────────
        pages = extract_pdf_pages(pdf_path)
        if not pages:
            raise ValueError(f"No text extracted from {pdf_path}")

        # ── Step 3: Hierarchical chunking ───────────────────────────────────────
        chunks = hierarchical_chunk(
            pages=pages,
            doc_id=doc_id,
            doc_type=metadata.doc_type,
            lpa_code=metadata.lpa_code,
            document_title=metadata.document_title,
        )
        if not chunks:
            raise ValueError("Chunking produced zero chunks")

        logger.info(f"Produced {len(chunks)} chunks")

        # ── Step 4: Embed with Jina AI (cloud, free tier) ───────────────────────
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts, batch_size=32)

        # ── Step 5: Upsert into Supabase pgvector ───────────────────────────────
        UPSERT_BATCH = 100
        for i in range(0, len(chunks), UPSERT_BATCH):
            batch_chunks = chunks[i : i + UPSERT_BATCH]
            batch_embeddings = embeddings[i : i + UPSERT_BATCH]

            rows = [
                {
                    "chunk_id":         c["chunk_id"],
                    "doc_id":           c["doc_id"],
                    "parent_id":        c.get("parent_id"),
                    "doc_type":         c["doc_type"],
                    "lpa_code":         c["lpa_code"],
                    "document_title":   c["document_title"],
                    "policy_reference": c.get("policy_reference", ""),
                    "section_title":    c.get("section_title", ""),
                    "page_number":      c.get("page_number", 1),
                    "date_effective":   metadata.date_effective or "",
                    "chunk_text":       c["text"],
                    "embedding":        emb,
                }
                for c, emb in zip(batch_chunks, batch_embeddings)
            ]
            supabase.table("policy_chunks").upsert(rows).execute()
            logger.info(f"Upserted batch {i//UPSERT_BATCH + 1} into Supabase pgvector")

        # ── Step 6: Record document in Supabase PostgreSQL ──────────────────────
        supabase.table("documents").upsert({
            "doc_id":         doc_id,
            "filename":       filename,
            "document_title": metadata.document_title,
            "doc_type":       metadata.doc_type,
            "lpa_code":       metadata.lpa_code,
            "chunk_count":    len(chunks),
            "status":         "indexed",
        }).execute()

        logger.info(f"Ingestion complete: {len(chunks)} chunks for '{metadata.document_title}'")
        return IngestionResult(
            doc_id=doc_id,
            chunk_count=len(chunks),
            status="indexed",
            errors=errors,
        )

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return IngestionResult(
            doc_id=doc_id,
            chunk_count=0,
            status="error",
            errors=[str(e)],
        )


def get_total_chunk_count() -> int:
    supabase = get_supabase()
    try:
        result = supabase.table("policy_chunks").select("chunk_id", count="exact").execute()
        return result.count or 0
    except Exception:
        return 0
