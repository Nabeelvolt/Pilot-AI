"""
Hierarchical semantic chunking.
Splits on heading patterns → target chunk size via tiktoken → 
assigns parent_id, policy_reference, section_title from heading context.
"""

import re
import uuid
import logging
import tiktoken
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# tiktoken works offline — no API call
try:
    enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    enc = None


def count_tokens(text: str) -> int:
    if enc:
        return len(enc.encode(text))
    # Rough fallback: 4 chars ≈ 1 token
    return len(text) // 4


# Heading patterns for UK planning documents
HEADING_PATTERNS = [
    r'^(Policy\s+[A-Z]{1,3}\d+[\.\d]*)',          # Policy H3, Policy D1.1
    r'^(POLICY\s+[A-Z]{1,3}\d+[\.\d]*)',           # POLICY H3
    r'^(Paragraph\s+\d+[\.\d]*)',                   # Paragraph 135
    r'^(\d+\.\d+[\.\d]*\s+[A-Z][A-Za-z\s]{3,})',  # 5.1 Housing Supply
    r'^([A-Z][A-Z\s]{4,}$)',                        # ALL CAPS HEADINGS
    r'^(Chapter\s+\d+)',                            # Chapter 5
    r'^(Appendix\s+[A-Z\d]+)',                      # Appendix A
]
HEADING_RE = re.compile("|".join(HEADING_PATTERNS), re.MULTILINE)

# Policy reference extraction
POLICY_REF_RE = re.compile(
    r'(Policy\s+[A-Z]{1,3}\d+[\.\d]*|NPPF\s+Para(?:graph)?\s+\d+[\.\d]*|Paragraph\s+\d+[\.\d]*)',
    re.IGNORECASE
)


def extract_policy_ref(text: str) -> Optional[str]:
    match = POLICY_REF_RE.search(text)
    return match.group(1).strip() if match else None


def hierarchical_chunk(
    pages: List[Dict],
    doc_id: str,
    doc_type: str,
    lpa_code: str,
    document_title: str,
    target_tokens: int = 400,
    min_tokens: int = 80,
) -> List[Dict]:
    """
    Chunk a list of pages into policy-aware chunks.
    Each chunk includes: chunk_id, parent_id, doc_id, doc_type, lpa_code,
    document_title, policy_reference, section_title, page_number, text.
    """
    # Combine all pages into one text, tracking page boundaries
    full_text_parts = []
    page_map = {}  # char_start -> page_number
    char_pos = 0
    for page in pages:
        page_map[char_pos] = page["page_number"]
        full_text_parts.append(page["text"])
        char_pos += len(page["text"]) + 1
    full_text = "\n".join(full_text_parts)

    def get_page_for_char(pos: int) -> int:
        """Return page number for a character position."""
        last_page = 1
        for start, pg in sorted(page_map.items()):
            if pos >= start:
                last_page = pg
        return last_page

    # Split text into segments by heading boundaries
    segments = []
    last_end = 0
    current_section = "Introduction"
    current_policy_ref = None

    for match in HEADING_RE.finditer(full_text):
        # Save segment before this heading
        seg_text = full_text[last_end:match.start()].strip()
        if seg_text and count_tokens(seg_text) >= min_tokens:
            segments.append({
                "text": seg_text,
                "section_title": current_section,
                "policy_reference": current_policy_ref,
                "page_number": get_page_for_char(last_end),
            })
        # Update context from heading
        current_section = match.group(0).strip()
        current_policy_ref = extract_policy_ref(current_section)
        last_end = match.end()

    # Final segment after last heading
    remaining = full_text[last_end:].strip()
    if remaining and count_tokens(remaining) >= min_tokens:
        segments.append({
            "text": remaining,
            "section_title": current_section,
            "policy_reference": current_policy_ref,
            "page_number": get_page_for_char(last_end),
        })

    # If no headings detected, fall back to sentence-boundary splitting
    if not segments:
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        current_chunk = []
        current_tokens = 0
        current_page = pages[0]["page_number"] if pages else 1
        for sentence in sentences:
            t = count_tokens(sentence)
            if current_tokens + t > target_tokens and current_tokens >= min_tokens:
                segments.append({
                    "text": " ".join(current_chunk),
                    "section_title": "General",
                    "policy_reference": None,
                    "page_number": current_page,
                })
                current_chunk = [sentence]
                current_tokens = t
            else:
                current_chunk.append(sentence)
                current_tokens += t
        if current_chunk and count_tokens(" ".join(current_chunk)) >= min_tokens:
            segments.append({
                "text": " ".join(current_chunk),
                "section_title": "General",
                "policy_reference": None,
                "page_number": current_page,
            })

    # Convert segments to chunk dicts
    chunks = []
    parent_id = None
    for seg in segments:
        # If segment is very long, split further at target_tokens boundary
        tokens = count_tokens(seg["text"])
        if tokens <= target_tokens:
            sub_segs = [seg["text"]]
        else:
            # Split on sentence boundaries within the segment
            words = seg["text"].split()
            sub_segs = []
            current = []
            current_t = 0
            for word in words:
                wt = count_tokens(word)
                if current_t + wt > target_tokens and current_t >= min_tokens:
                    sub_segs.append(" ".join(current))
                    current = [word]
                    current_t = wt
                else:
                    current.append(word)
                    current_t += wt
            if current:
                sub_segs.append(" ".join(current))

        for j, sub_text in enumerate(sub_segs):
            if count_tokens(sub_text) < min_tokens:
                continue
            cid = str(uuid.uuid4())
            chunk = {
                "chunk_id":        cid,
                "parent_id":       parent_id if j > 0 else None,
                "doc_id":          doc_id,
                "doc_type":        doc_type,
                "lpa_code":        lpa_code,
                "document_title":  document_title,
                "policy_reference": seg.get("policy_reference") or extract_policy_ref(sub_text) or "",
                "section_title":   seg.get("section_title", ""),
                "page_number":     seg.get("page_number", 1),
                "text":            sub_text.strip(),
            }
            if j == 0:
                parent_id = cid  # first sub-chunk is parent for remainder
            chunks.append(chunk)

    logger.info(f"Chunked into {len(chunks)} chunks ({len(segments)} segments)")
    return chunks
