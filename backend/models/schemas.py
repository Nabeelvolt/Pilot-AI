from pydantic import BaseModel
from typing import List, Optional

class DocumentMetadata(BaseModel):
    document_title: str
    doc_type: str  # national_policy | local_plan | spd | building_regs
    lpa_code: str  # e.g. "lincoln" or "national"
    date_effective: Optional[str] = None

class IngestionResult(BaseModel):
    doc_id: str
    chunk_count: int
    status: str  # "indexed" | "error"
    errors: List[str] = []

class AnalysisRequest(BaseModel):
    application_ref: Optional[str] = None
    site_address: Optional[str] = None
    application_type: str
    proposed_development: str
    site_constraints: Optional[List[str]] = []

class AnalysisResponse(BaseModel):
    analysis_id: str
    overall_status: str
    overall_confidence: float
    summary: str
    policy_findings: List[dict]
    key_issues: List[dict]
    recommended_actions: List[str]
    uncertainty_flags: List[str]
    retrieved_chunks: List[dict]
    processing_time_seconds: float

class DocumentRecord(BaseModel):
    doc_id: str
    filename: str
    document_title: str
    doc_type: str
    lpa_code: str
    chunk_count: int
    status: str
    created_at: str
