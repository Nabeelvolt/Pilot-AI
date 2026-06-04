"""Extract text from PDFs page-by-page using pdfplumber (primary) or PyMuPDF (fallback)."""

import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def extract_pdf_pages(pdf_path: str) -> List[Dict]:
    """
    Returns a list of dicts: [{ page_number: int, text: str }, ...]
    Skips pages with less than 50 characters (blank/image pages).
    Uses PyMuPDF first; falls back to pdfplumber if PyMuPDF fails.
    """
    pages = []

    # ── Primary: PyMuPDF (Fast & Memory Efficient) ──────────────────────
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            if len(text) >= 50:
                pages.append({"page_number": i + 1, "text": text})
        doc.close()
        if pages:
            return pages
    except Exception as e:
        logger.warning(f"PyMuPDF failed ({e}), trying pdfplumber fallback")

    # ── Fallback: pdfplumber (Memory Heavy) ─────────────────────────────
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                # Also extract tables as pipe-delimited text
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            row_text = " | ".join(str(cell or "").strip() for cell in row)
                            if row_text.strip(" |"):
                                text += f"\n{row_text}"
                text = text.strip()
                if len(text) >= 50:
                    pages.append({"page_number": i + 1, "text": text})
        return pages
    except Exception as e:
        logger.error(f"pdfplumber also failed: {e}")
        return []
