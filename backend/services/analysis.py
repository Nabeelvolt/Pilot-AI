"""
Core analysis service.
Builds multi-query retrieval → assembles structured prompt →
calls LLM (Groq / Gemini) → verifies citations → returns AnalysisResponse.
"""

import json
import logging
import uuid
from datetime import datetime
from config import settings
from models.schemas import AnalysisRequest, AnalysisResponse
from services.retrieval import multi_query_retrieve
from services.supabase_client import get_supabase
from services.llm_client import call_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are PILOT-AI, a planning decision-support assistant for UK Local Planning Authorities.
You analyse planning applications against UK national and local planning policy.

STRICT RULES — follow these without exception:
1. Only make findings directly supported by the retrieved policy context provided.
2. Every policy_finding and key_issue MUST include a citation_id (e.g. "C1", "C3") referencing the context.
3. If context is insufficient for a finding, use finding: "INSUFFICIENT_INFO" and say so.
4. Never invent policy, paragraph numbers, or document titles not in the provided context.
5. Apply policy in this hierarchy: National (NPPF) > Local Plan > SPD.
6. Write in plain English suitable for a planning officer — no jargon without explanation.
7. You are a decision-SUPPORT tool. Never say "approve" or "refuse" — say whether it appears to comply.
8. Output ONLY valid JSON matching the exact schema below. No preamble, no markdown, no extra keys.

OUTPUT JSON SCHEMA:
{
  "overall_status": "LIKELY_COMPLIANT | REQUIRES_FURTHER_INFO | LIKELY_NON_COMPLIANT | INSUFFICIENT_INFORMATION",
  "overall_confidence": 0.82,
  "summary": "3-4 sentence plain English compliance overview.",
  "policy_findings": [
    {
      "policy_reference": "NPPF 2024, Paragraph 135(c)",
      "document_title": "National Planning Policy Framework",
      "finding": "COMPLIES | POTENTIAL_CONFLICT | INSUFFICIENT_INFO | NOT_APPLICABLE",
      "confidence": 0.88,
      "explanation": "1-2 sentence plain English explanation.",
      "citation_id": "C3"
    }
  ],
  "key_issues": [
    {
      "severity": "HIGH | MEDIUM | LOW",
      "policy_reference": "NPPF Para 135(c)",
      "issue": "Plain English description of the issue.",
      "citation_id": "C3"
    }
  ],
  "recommended_actions": [
    "Plain English recommended action for the planning officer."
  ],
  "uncertainty_flags": [
    "Any notes about limited context, assumptions, or things to verify."
  ]
}"""


def build_retrieval_queries(request: AnalysisRequest) -> list[str]:
    """Build multiple targeted queries from the application details."""
    queries = [
        # Primary: full proposal description
        request.proposed_development,
        # Secondary: proposal + application type
        f"{request.application_type}: {request.proposed_development[:300]}",
    ]
    # Constraint-specific sub-queries
    if "Conservation Area" in (request.site_constraints or []):
        queries.append(
            "heritage impact conservation area setting listed building planning policy requirements"
        )
    if any("Flood" in c for c in (request.site_constraints or [])):
        queries.append(
            "flood risk sequential test exception test sustainable drainage planning policy"
        )
    if "Green Belt" in (request.site_constraints or []):
        queries.append("green belt very special circumstances exceptional development policy")
    if "Listed Building" in " ".join(request.site_constraints or []):
        queries.append("listed building consent heritage significance harm planning policy")
    # Always include affordable housing query for residential
    if any(kw in request.proposed_development.lower()
           for kw in ["dwelling", "apartment", "flat", "residential", "housing", "homes"]):
        queries.append("affordable housing provision requirement policy residential development")
    return queries


def assemble_context_string(chunks: list[dict]) -> str:
    """Format retrieved chunks as numbered context for the LLM prompt."""
    lines = []
    for chunk in chunks:
        lines.append(
            f"[{chunk['chunk_id']}] SOURCE: {chunk['document_title']} | "
            f"Policy: {chunk['policy_reference'] or 'N/A'} | "
            f"Section: {chunk['section_title'] or 'N/A'} | "
            f"Page: {chunk['page_number']} | "
            f"Relevance: {chunk['relevance']:.2f}\n"
            f"TEXT: {chunk['text']}\n"
        )
    return "\n---\n".join(lines)


def verify_citations(response_dict: dict, retrieved_chunks: list[dict]) -> dict:
    """
    Remove any findings whose citation_id does not exist in the retrieved chunks.
    Adds an uncertainty flag for each removed phantom citation.
    """
    valid_ids = {c["chunk_id"] for c in retrieved_chunks}
    phantoms = []

    verified_findings = []
    for finding in response_dict.get("policy_findings", []):
        cid = finding.get("citation_id", "")
        if cid and cid not in valid_ids:
            phantoms.append(f"Citation {cid} removed — not found in retrieved context")
        else:
            verified_findings.append(finding)

    verified_issues = []
    for issue in response_dict.get("key_issues", []):
        cid = issue.get("citation_id", "")
        if cid and cid not in valid_ids:
            phantoms.append(f"Issue citation {cid} removed — not in retrieved context")
        else:
            verified_issues.append(issue)

    response_dict["policy_findings"] = verified_findings
    response_dict["key_issues"] = verified_issues
    if phantoms:
        flags = response_dict.get("uncertainty_flags", [])
        flags.extend(phantoms)
        response_dict["uncertainty_flags"] = flags
        logger.warning(f"Removed {len(phantoms)} phantom citations")

    return response_dict


def analyse_application(request: AnalysisRequest) -> AnalysisResponse:
    """
    Full analysis pipeline:
    1. Multi-query retrieval
    2. Context assembly
    3. LLM call (Groq → Gemini fallback)
    4. JSON parse + citation verification
    5. Save to SQLite
    6. Return AnalysisResponse
    """
    analysis_id = request.analysis_id if request.analysis_id else str(uuid.uuid4())
    started_at = datetime.utcnow()

    # ── Step 1: Retrieve relevant policy chunks ─────────────────────────────────
    queries = build_retrieval_queries(request)
    chunks = multi_query_retrieve(
        queries=queries,
        top_k=settings.RERANK_TOP_K,
        lpa_code="lincoln",  # hardcoded for demo; parameterise in production
    )

    if not chunks:
        # No policy documents indexed yet — return graceful error
        return AnalysisResponse(
            analysis_id=analysis_id,
            overall_status="INSUFFICIENT_INFORMATION",
            overall_confidence=0.0,
            summary="No policy documents are currently indexed. Please upload planning policy documents in the Policy Library before running an analysis.",
            policy_findings=[],
            key_issues=[],
            recommended_actions=["Upload planning policy documents via the Policy Library page."],
            uncertainty_flags=["Policy corpus is empty."],
            retrieved_chunks=[],
            processing_time_seconds=0.0,
        )

    # ── Step 2: Assemble prompt ─────────────────────────────────────────────────
    context_str = assemble_context_string(chunks)
    constraints_str = (
        ", ".join(request.site_constraints) if request.site_constraints else "None identified"
    )
    user_prompt = f"""PLANNING APPLICATION DETAILS:
Reference: {request.application_ref or 'Not provided'}
Site Address: {request.site_address or 'Not provided'}
Application Type: {request.application_type}
Site Constraints: {constraints_str}

Proposed Development:
{request.proposed_development}

RETRIEVED POLICY CONTEXT ({len(chunks)} sections):
{context_str}

Analyse this application against the policy context above and return the JSON response."""

    # ── Step 3: Call LLM ────────────────────────────────────────────────────────
    raw_response = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=3000,
        temperature=0.0,
        require_json=True,
    )

    # ── Step 4: Parse + verify ──────────────────────────────────────────────────
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        # Extract JSON if wrapped in markdown
        import re
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
        else:
            raise ValueError(f"LLM did not return valid JSON: {raw_response[:200]}")

    parsed = verify_citations(parsed, chunks)

    # ── Step 5: Save to SQLite ──────────────────────────────────────────────────
    processing_seconds = (datetime.utcnow() - started_at).total_seconds()
    supabase = get_supabase()
    supabase.table("analyses").upsert({
        "analysis_id":               analysis_id,
        "application_ref":           request.application_ref or "N/A",
        "site_address":              request.site_address or "N/A",
        "application_type":          request.application_type,
        "overall_status":            parsed.get("overall_status", "INSUFFICIENT_INFORMATION"),
        "overall_confidence":        parsed.get("overall_confidence", 0.0),
        "processing_time_seconds":   processing_seconds,
    }).execute()

    # ── Step 5.5: Run Document Validation ───────────────────────────────────────
    try:
        from services.document_analyser import run_validation_check, assess_document
        
        # Get uploaded docs
        docs_res = supabase.table("application_documents").select("*").eq("analysis_id", analysis_id).execute()
        uploaded_docs = docs_res.data or []
        
        if uploaded_docs:
            for doc in uploaded_docs:
                if doc.get("extracted_text") and doc.get("upload_status") != "analysed":
                    assessment = assess_document(doc["extracted_text"], doc["document_category"])
                    supabase.table("document_assessments").insert({
                        "assessment_id": str(uuid.uuid4()),
                        "analysis_id": analysis_id,
                        "application_doc_id": doc["application_doc_id"],
                        "document_category": doc["document_category"],
                        "overall_adequacy": assessment.get("overall_adequacy", "CANNOT_ASSESS"),
                        "adequacy_score": assessment.get("adequacy_score", 0.0),
                        "sections_present": assessment.get("sections_present", []),
                        "sections_missing": assessment.get("sections_missing", []),
                        "policy_conflicts": assessment.get("policy_conflicts", []),
                        "recommendations": assessment.get("recommendations", []),
                    }).execute()
                    supabase.table("application_documents").update({"upload_status": "analysed"}).eq("application_doc_id", doc["application_doc_id"]).execute()
            
        uploaded_categories = [d["document_category"] for d in uploaded_docs]
        validation = run_validation_check(
            analysis_id=analysis_id,
            application_type=request.application_type,
            uploaded_document_categories=uploaded_categories,
            site_constraints=request.site_constraints or [],
        )
        supabase.table("validation_results").upsert(validation).execute()
    except Exception as e:
        logger.error(f"Failed to run document validation: {e}")

    # ── Step 6: Return ──────────────────────────────────────────────────────────
    return AnalysisResponse(
        analysis_id=analysis_id,
        overall_status=parsed.get("overall_status", "INSUFFICIENT_INFORMATION"),
        overall_confidence=parsed.get("overall_confidence", 0.0),
        summary=parsed.get("summary", ""),
        policy_findings=parsed.get("policy_findings", []),
        key_issues=parsed.get("key_issues", []),
        recommended_actions=parsed.get("recommended_actions", []),
        uncertainty_flags=parsed.get("uncertainty_flags", []),
        retrieved_chunks=chunks,
        processing_time_seconds=processing_seconds,
    )
