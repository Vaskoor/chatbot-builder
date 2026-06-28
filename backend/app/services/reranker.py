"""
Cross-encoder reranking: takes the top-N hybrid retrieval candidates and
re-scores (query, chunk) pairs jointly for much higher precision than
embedding similarity alone. This is the step that makes retrieval
"intelligent" rather than just nearest-neighbor.
"""
from sentence_transformers import CrossEncoder

from app.core.config import settings
import threading
_reranker = None
_lock = threading.Lock()
def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        with _lock:
            if _reranker is None:
                _reranker = CrossEncoder(settings.reranker_model)
    return _reranker
def rerank(query: str, candidates: list[dict], top_k: int = 6) -> list[dict]:
    """
    candidates: list of dicts each with a 'text' key.
    Returns candidates sorted by cross-encoder relevance score, trimmed to top_k.
    Adds a 'rerank_score' field to each candidate.
    """
    if not candidates:
        return []
    if not settings.enable_reranking:
        return candidates[:top_k]
    model = get_reranker()
    pairs = [[query, c["text"]] for c in candidates]
    scores = model.predict(pairs)
    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)
    ranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:top_k]
