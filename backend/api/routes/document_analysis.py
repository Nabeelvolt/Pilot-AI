"""
New endpoints for document bundle upload and analysis.
POST /api/document-analysis/upload    — upload one application document
POST /api/document-analysis/assess    — run adequacy assessment on uploaded docs
POST /api/document-analysis/validate  — run full validation checklist
GET  /api/document-analysis/{analysis_id} — get all doc assessments for an analysis
"""

import uuid
import tempfile
import os
import logging
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, BackgroundTasks
from services.supabase_client import get_supabase
from services.document_analyser import (
    extract_document_text,
    assess_document,
    run_validation_check,
)
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_application_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    analysis_id: str = Form(...),
    document_category: str = Form(...),
):
    try:
        """Upload a single application document PDF and extract its text."""
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=422, detail="Only PDF files supported.")

        pdf_bytes = await file.read()
        application_doc_id = str(uuid.uuid4())
        supabase = get_supabase()

        # Upload to Supabase Storage
        storage_path = f"applications/{analysis_id}/{document_category}/{file.filename}"
        supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            path=storage_path,
            file=pdf_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"},
        )

        # Extract text in temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            extracted_text, word_count = extract_document_text(tmp_path)
        finally:
            os.unlink(tmp_path)

        # Save record to Supabase
        supabase.table("application_documents").insert({
            "application_doc_id": application_doc_id,
            "analysis_id": analysis_id,
            "filename": file.filename,
            "document_category": document_category,
            "storage_path": storage_path,
            "extracted_text": extracted_text[:50000],  # Supabase text limit safety
            "word_count": word_count,
            "upload_status": "extracted",
        }).execute()

        return {
            "application_doc_id": application_doc_id,
            "filename": file.filename,
            "document_category": document_category,
            "word_count": word_count,
            "status": "extracted",
            "message": f"Document uploaded and text extracted ({word_count} words). Ready for assessment."
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}


@router.post("/assess/{application_doc_id}")
async def assess_single_document(application_doc_id: str):
    """Run policy adequacy assessment on a single uploaded document."""
    supabase = get_supabase()

    # Fetch document record
    result = supabase.table("application_documents").select("*").eq(
        "application_doc_id", application_doc_id
    ).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc = result.data[0]
    if not doc.get("extracted_text"):
        raise HTTPException(status_code=422, detail="Document text not yet extracted.")

    # Run LLM-based adequacy assessment
    assessment = assess_document(
        document_text=doc["extracted_text"],
        document_category=doc["document_category"],
    )

    assessment_id = str(uuid.uuid4())
    supabase.table("document_assessments").insert({
        "assessment_id": assessment_id,
        "analysis_id": doc["analysis_id"],
        "application_doc_id": application_doc_id,
        "document_category": doc["document_category"],
        "overall_adequacy": assessment.get("overall_adequacy", "CANNOT_ASSESS"),
        "adequacy_score": assessment.get("adequacy_score", 0.0),
        "sections_present": assessment.get("sections_present", []),
        "sections_missing": assessment.get("sections_missing", []),
        "policy_conflicts": assessment.get("policy_conflicts", []),
        "recommendations": assessment.get("recommendations", []),
    }).execute()

    # Update document status
    supabase.table("application_documents").update(
        {"upload_status": "analysed"}
    ).eq("application_doc_id", application_doc_id).execute()

    return {**assessment, "assessment_id": assessment_id}


@router.post("/validate")
async def run_validation(
    analysis_id: str = Form(...),
    application_type: str = Form(...),
    site_constraints: str = Form(default=""),  # comma-separated
):
    """Run full validation checklist for an application."""
    constraints = [c.strip() for c in site_constraints.split(",") if c.strip()]

    supabase = get_supabase()
    docs_result = supabase.table("application_documents").select(
        "document_category"
    ).eq("analysis_id", analysis_id).execute()

    uploaded_categories = [d["document_category"] for d in (docs_result.data or [])]

    validation = run_validation_check(
        analysis_id=analysis_id,
        application_type=application_type,
        uploaded_document_categories=uploaded_categories,
        site_constraints=constraints,
    )

    supabase.table("validation_results").upsert(validation).execute()
    return validation


@router.get("/{analysis_id}")
async def get_document_assessments(analysis_id: str):
    """Get all document uploads and assessments for an analysis."""
    try:
        supabase = get_supabase()

        docs = supabase.table("application_documents").select("*").eq(
            "analysis_id", analysis_id
        ).execute()

        assessments = supabase.table("document_assessments").select("*").eq(
            "analysis_id", analysis_id
        ).execute()

        validation = supabase.table("validation_results").select("*").eq(
            "analysis_id", analysis_id
        ).order("created_at", desc=True).limit(1).execute()

        return {
            "documents": docs.data or [],
            "assessments": assessments.data or [],
            "validation": validation.data[0] if validation.data else None,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
