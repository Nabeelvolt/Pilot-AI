import io
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from models.schemas import DocumentMetadata, IngestionResult
from services.ingestion import ingest_document
from services.supabase_client import get_supabase
from config import settings
import tempfile, os

router = APIRouter()

@router.get("/")
def list_documents():
    supabase = get_supabase()
    result = (
        supabase.table("documents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_title: str = Form(...),
    doc_type: str = Form(...),
    lpa_code: str = Form(...),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()

    # Write to temp file for pdfplumber (needs file path)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        metadata = DocumentMetadata(
            document_title=document_title,
            doc_type=doc_type,
            lpa_code=lpa_code,
        )
        result = ingest_document(
            pdf_path=tmp_path,
            metadata=metadata,
            pdf_bytes=pdf_bytes,
        )
        return result
    finally:
        os.unlink(tmp_path)
