"""
Document Analysis Service.
Takes uploaded planning application PDFs, extracts their text,
and checks content adequacy against policy requirements.
Uses the same LLM pipeline (Groq/Gemini) already in the system.
"""

import uuid
import json
import logging
from typing import List, Optional
from services.llm_client import call_llm
from services.embedding_client import embed_texts
from services.supabase_client import get_supabase
from utils.pdf_extractor import extract_pdf_pages
from data.validation_rules import DOCUMENT_REQUIREMENTS, VALIDATION_REQUIREMENTS

logger = logging.getLogger(__name__)

DOCUMENT_ASSESSMENT_PROMPT = """You are a senior UK planning officer reviewing a planning application document.

Your task is to assess whether this document meets the policy requirements and contains all mandatory sections.

DOCUMENT TYPE: {document_category}
POLICY BASIS: {policy_basis}
REQUIRED WHEN: {required_when}

MANDATORY SECTIONS THAT MUST BE PRESENT:
{mandatory_sections}

ADEQUACY INDICATORS TO LOOK FOR:
{adequacy_indicators}

COMMON DEFICIENCIES TO CHECK FOR:
{common_deficiencies}

DOCUMENT CONTENT TO ASSESS:
{document_text}

Assess this document and respond ONLY with valid JSON in this exact schema:
{{
  "overall_adequacy": "ADEQUATE | INADEQUATE | MISSING_SECTIONS | CANNOT_ASSESS",
  "adequacy_score": 0.0-1.0,
  "sections_present": ["section name", ...],
  "sections_missing": ["section name", ...],
  "policy_conflicts": [
    {{
      "policy_reference": "NPPF Para 167",
      "issue": "Plain English description of the conflict",
      "severity": "HIGH | MEDIUM | LOW"
    }}
  ],
  "recommendations": [
    "Specific plain English action the applicant must take"
  ],
  "summary": "2-3 sentence plain English assessment for the planning officer"
}}"""


def extract_document_text(pdf_path: str) -> tuple[str, int]:
    """Extract text from PDF and return (full_text, word_count)."""
    pages = extract_pdf_pages(pdf_path)
    if not pages:
        return "", 0
    full_text = "\n\n".join(p["text"] for p in pages)
    word_count = len(full_text.split())
    return full_text, word_count


def assess_document(
    document_text: str,
    document_category: str,
) -> dict:
    """
    Use LLM to assess whether a document meets planning policy requirements.
    Returns structured assessment dict.
    """
    if document_category not in DOCUMENT_REQUIREMENTS:
        return {
            "overall_adequacy": "CANNOT_ASSESS",
            "adequacy_score": 0.0,
            "sections_present": [],
            "sections_missing": [],
            "policy_conflicts": [],
            "recommendations": [f"Document category '{document_category}' not in validation rules."],
            "summary": "This document type is not currently in the PILOT-AI validation rules library."
        }

    rules = DOCUMENT_REQUIREMENTS[document_category]

    # Truncate very long documents to fit in context (keep first 8000 words)
    words = document_text.split()
    if len(words) > 8000:
        document_text = " ".join(words[:8000]) + "\n\n[Document truncated for analysis — first 8,000 words shown]"

    prompt = DOCUMENT_ASSESSMENT_PROMPT.format(
        document_category=document_category.replace("_", " ").title(),
        policy_basis=", ".join(rules["policy_basis"]),
        required_when=", ".join(rules["required_when"]),
        mandatory_sections="\n".join(f"- {s}" for s in rules["mandatory_sections"]),
        adequacy_indicators="\n".join(f"- {s}" for s in rules["adequacy_indicators"]),
        common_deficiencies="\n".join(f"- {s}" for s in rules["common_deficiencies"]),
        document_text=document_text,
    )

    system_prompt = """You are a senior UK planning officer with 20+ years experience.
    You assess submitted planning documents for policy compliance and adequacy.
    Be specific, technical, and honest. Do not be lenient — inadequate documents cause delays.
    Respond ONLY with valid JSON. No preamble, no markdown."""

    raw = call_llm(
        system_prompt=system_prompt,
        user_prompt=prompt,
        max_tokens=2000,
        temperature=0.0,
        require_json=True,
    )

    try:
        return json.loads(raw)
    except Exception:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {
            "overall_adequacy": "CANNOT_ASSESS",
            "adequacy_score": 0.0,
            "sections_present": [],
            "sections_missing": [],
            "policy_conflicts": [],
            "recommendations": ["Document assessment failed — please retry."],
            "summary": "Analysis could not be completed for this document."
        }


def run_validation_check(
    analysis_id: str,
    application_type: str,
    uploaded_document_categories: List[str],
    site_constraints: List[str],
) -> dict:
    """
    Run the full validation checklist against what has been submitted.
    Checks national requirements + Central Lincolnshire local list.
    Returns a validation result showing what is missing, present, or inadequate.
    """
    if application_type not in VALIDATION_REQUIREMENTS:
        application_type = "Full Planning Permission"

    rules = VALIDATION_REQUIREMENTS[application_type]
    results = []

    # Check national mandatory documents
    for doc in rules["national_mandatory"]:
        results.append({
            "document_name": doc,
            "requirement_type": "National — Mandatory",
            "required": True,
            "present": True,  # National mandatory are assumed submitted (form, plans, cert, fee)
            "adequate": True,
            "notes": "National mandatory requirement"
        })

    # Check national conditional documents
    for item in rules.get("national_conditional", []):
        is_required = _check_if_required(item["required_when"], site_constraints, application_type)
        is_present = item["document"].lower().replace(" ", "_").replace("/", "_") in [
            c.lower().replace(" ", "_") for c in uploaded_document_categories
        ]
        results.append({
            "document_name": item["document"],
            "requirement_type": "National — Conditional",
            "required_when": item["required_when"],
            "required": is_required,
            "present": is_present if is_required else None,
            "adequate": None,  # Will be populated after document assessment
            "notes": item["required_when"]
        })

    # Check Central Lincolnshire local list
    for item in rules.get("central_lincolnshire_local_list", []):
        is_required = _check_if_required(item["required_when"], site_constraints, application_type)
        doc_key = _normalise_doc_name(item["document"])
        is_present = any(
            _normalise_doc_name(cat) == doc_key or doc_key in _normalise_doc_name(cat)
            for cat in uploaded_document_categories
        )
        results.append({
            "document_name": item["document"],
            "requirement_type": "Central Lincolnshire — Local List",
            "required_when": item["required_when"],
            "required": is_required,
            "present": is_present if is_required else None,
            "adequate": None,
            "notes": f"Central Lincolnshire Local Validation List (adopted May 2024)"
        })

    missing = [r["document_name"] for r in results if r.get("required") and not r.get("present")]
    inadequate = [r["document_name"] for r in results if r.get("required") and r.get("present") and r.get("adequate") is False]

    if missing:
        overall_status = "INVALID"
    elif inadequate:
        overall_status = "REQUIRES_REVIEW"
    else:
        overall_status = "VALID"

    return {
        "validation_id": str(uuid.uuid4()),
        "analysis_id": analysis_id,
        "application_type": application_type,
        "required_documents": results,
        "overall_status": overall_status,
        "missing_documents": missing,
        "inadequate_documents": inadequate,
    }


def _check_if_required(required_when: str, site_constraints: List[str], application_type: str) -> bool:
    """Heuristic check whether a document is required given site constraints."""
    required_lower = required_when.lower()
    constraints_lower = [c.lower() for c in site_constraints]

    triggers = {
        "flood zone": ["flood zone 2", "flood zone 3"],
        "listed building": ["grade i listed building", "grade ii* listed building", "grade ii listed building"],
        "conservation area": ["conservation area"],
        "heritage": ["conservation area", "grade i listed building", "grade ii* listed building", "grade ii listed building"],
        "major": ["full planning permission", "outline planning permission"],
        "all application": ["_always_"],
        "mandatory": ["_always_"],
    }

    for trigger_key, constraint_matches in triggers.items():
        if trigger_key in required_lower:
            if "_always_" in constraint_matches:
                return True
            if any(cm in constraints_lower for cm in constraint_matches):
                return True

    return False


def _normalise_doc_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "").replace("-", "_")
