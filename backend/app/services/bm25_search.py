"""
BM25 keyword search to complement vector (semantic) search. Built
on-demand per request from the bot's active chunk corpus (cheap for
typical knowledge-base sizes; can be cached/optimized later).
"""
import re
from rank_bm25 import BM25Okapi
from app.services.vector_store import get_all_active_chunks
def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9']+", text.lower())
def bm25_search(collection_name: str, query: str, top_k: int = 20) -> list[dict]:
    corpus = get_all_active_chunks(collection_name)
    if not corpus:
        return []
    tokenized_corpus = [_tokenize(c["text"]) for c in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    scored = list(zip(corpus, scores))
    scored.sort(key=lambda x: x[1], reverse=True)
    max_score = max((s for _, s in scored), default=0) or 1.0
    results = []
    for chunk, score in scored[:top_k]:

        if score <= 0:
            continue
        item = dict(chunk)
        item["bm25_score"] = float(score) / max_score  # normalize to 0-1
        results.append(item)
    return results
