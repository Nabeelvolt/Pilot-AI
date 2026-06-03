"""
Jina AI Embedding API client.
Free tier: 1M tokens/month, no credit card required.
Model: jina-embeddings-v3, 1024 dimensions, 8192 token context.
Drop-in replacement for local sentence-transformers.
"""

import httpx
import logging
import time
from typing import List
from config import settings

logger = logging.getLogger(__name__)

JINA_API_URL = "https://api.jina.ai/v1/embeddings"


def embed_texts(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Embed a list of texts using the Jina AI API.
    Returns a list of 1024-dimensional float vectors.
    Batches requests to respect rate limits (100 RPM free tier).
    """
    if not texts:
        return []

    if not settings.JINA_API_KEY:
        raise RuntimeError(
            "JINA_API_KEY not set. Get a free key at jina.ai (no credit card needed)."
        )

    headers = {
        "Authorization": f"Bearer {settings.JINA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        payload = {
            "model": settings.JINA_EMBEDDING_MODEL,
            "input": batch,
            "task": "retrieval.passage",  # optimised for document storage
            "dimensions": settings.EMBEDDING_DIM,
            "late_chunking": False,
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(JINA_API_URL, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    # Jina returns sorted by index — safe to extend directly
                    batch_vecs = [item["embedding"] for item in data["data"]]
                    all_embeddings.extend(batch_vecs)
                    logger.info(
                        f"Embedded batch {i//batch_size + 1}/"
                        f"{(len(texts) + batch_size - 1)//batch_size} "
                        f"({len(batch)} texts)"
                    )
                    break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit — wait and retry
                    wait = (attempt + 1) * 10
                    logger.warning(f"Jina rate limit hit. Waiting {wait}s before retry...")
                    time.sleep(wait)
                    if attempt == max_retries - 1:
                        raise RuntimeError(
                            f"Jina API rate limit exceeded after {max_retries} retries. "
                            "Free tier is 100 RPM / 100K TPM. Wait a minute and try again."
                        )
                else:
                    raise
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Jina embedding failed after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)

        # Polite delay between batches on free tier
        if i + batch_size < len(texts):
            time.sleep(0.7)

    return all_embeddings


def embed_query(query: str) -> List[float]:
    """
    Embed a single search query.
    Uses task='retrieval.query' (different from passage embedding — better retrieval).
    """
    if not settings.JINA_API_KEY:
        raise RuntimeError("JINA_API_KEY not set.")

    headers = {
        "Authorization": f"Bearer {settings.JINA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.JINA_EMBEDDING_MODEL,
        "input": [query],
        "task": "retrieval.query",
        "dimensions": settings.EMBEDDING_DIM,
        "late_chunking": False,
    }

    with httpx.Client(timeout=15.0) as client:
        response = client.post(JINA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
