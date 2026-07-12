"""
Retrieval service — cloud version.
Embeds query via Jina AI → queries Supabase pgvector via
match_policy_chunks SQL function → returns ranked chunks.
"""

import logging
from typing import List, Optional

from services.supabase_client import get_supabase
from services.embedding_client import embed_query

logger = logging.getLogger(__name__)


def retrieve_chunks(
    query: str,
    n_results: int = 12,
    lpa_code: Optional[str] = None,
    doc_types: Optional[List[str]] = None,
) -> List[dict]:
    """
    Embed query with Jina AI → call Supabase pgvector similarity search.
    Returns top-N chunks sorted by relevance score.
    """
    if not query.strip():
        return []

    supabase = get_supabase()

    # Embed query using Jina AI (task='retrieval.query')
    query_vec = embed_query(query)

    # Call Supabase RPC function for similarity search
    params = {
        "query_embedding": query_vec,
        "match_count": n_results,
        "filter_lpa": lpa_code,
        "filter_doc_types": doc_types,
    }

    try:
        result = supabase.rpc("match_policy_chunks", params).execute()
        rows = result.data or []
    except Exception as e:
        logger.error(f"Supabase retrieval error: {e}")
        return []

    chunks = []
    for i, row in enumerate(rows):
        chunks.append({
            "chunk_id":         f"C{i+1}",
            "text":             row.get("chunk_text", ""),
            "relevance":        round(float(row.get("relevance", 0)), 3),
            "doc_type":         row.get("doc_type", ""),
            "document_title":   row.get("document_title", ""),
            "policy_reference": row.get("policy_reference", ""),
            "section_title":    row.get("section_title", ""),
            "page_number":      str(row.get("page_number", "")),
            "lpa_code":         row.get("lpa_code", ""),
            "date_effective":   row.get("date_effective", ""),
        })

    chunks.sort(key=lambda x: x["relevance"], reverse=True)
    return chunks


import cohere
import os

co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

def rerank_chunks(query: str, chunks: List[dict], top_n: int = 5) -> List[dict]:
    """
    Use Cohere Re-Ranker to score relevance of retrieved chunks against the original query.
    Returns the top_n chunks.
    """
    if not chunks:
        return chunks
    docs = [c["text"] for c in chunks]
    try:
        results = co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=docs,
            top_n=top_n,
        )
        reranked = []
        for r in results.results:
            chunk = chunks[r.index].copy()
            chunk["relevance"] = round(r.relevance_score, 3)
            chunk["chunk_id"] = f"C{len(reranked)+1}"
            reranked.append(chunk)
        return reranked
    except Exception as e:
        logger.error(f"Cohere reranking error: {e}")
        # Fallback to original chunks if reranking fails
        return chunks[:top_n]

def multi_query_retrieve(
    queries: List[str],
    top_k: int = 15,
    lpa_code: Optional[str] = None,
) -> List[dict]:
    """
    Run multiple queries, merge and deduplicate results.
    Returns top_k unique chunks by best relevance score.
    """
    seen = {}
    for q in queries:
        for chunk in retrieve_chunks(q, n_results=12, lpa_code=lpa_code):
            key = chunk["text"][:100]
            if key not in seen or chunk["relevance"] > seen[key]["relevance"]:
                seen[key] = chunk

    merged = sorted(seen.values(), key=lambda x: x["relevance"], reverse=True)
    
    # We retrieve more initially, then re-rank down to top_k
    # Use the first query as the main semantic intent for re-ranking
    main_query = queries[0] if queries else ""
    if main_query and len(merged) > 0:
        return rerank_chunks(main_query, merged[:30], top_n=top_k)
    
    for i, chunk in enumerate(merged[:top_k]):
        chunk["chunk_id"] = f"C{i+1}"
    return merged[:top_k]
