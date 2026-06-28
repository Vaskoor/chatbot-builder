"""
Query understanding layer: expands ambiguous/short queries, generates a
HyDE (Hypothetical Document Embedding) passage to improve recall, and
classifies whether a query needs multi-hop graph reasoning.
"""
from app.services.llm import fast_completion, fast_json_completion
import logging
logger = logging.getLogger(__name__)
def expand_query(query: str, conversation_context: str = "") -> list[str]:
    """
    Generate 2-3 alternate phrasings / sub-questions to widen recall.
    Falls back to just the original query if the LLM call fails.
    """
    context_note = f"\nRecent conversation context:\n{conversation_context}" if conversation_context else ""
    prompt = (

        f"Rewrite the user's question into 2 alternative search queries that capture "
        f"the same intent using different wording or more specific terms. "
        f"Return ONLY a JSON object: {{\"queries\": [\"...\", \"...\"]}}."
        f"{context_note}\n\nUser question: {query}"
    )
    result = fast_json_completion(prompt, system="You are a search query rewriting assistant.")
    queries = result.get("queries", [])
    cleaned = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
    return [query] + cleaned[:2]
def generate_hyde_passage(query: str) -> str:
    """
    HyDE: ask the LLM to write a plausible passage that would answer the
    question, then embed THAT for retrieval. Often improves recall on
    vague or under-specified queries because the hypothetical answer is
    semantically closer to real knowledge-base passages than the raw question.
    """
    prompt = (
        f"Write a short, factual paragraph (3-4 sentences) that plausibly answers "
        f"this question, as if it were an excerpt from a travel knowledge base. "
        f"Question: {query}"
    )
    passage = fast_completion(prompt, system="You write concise hypothetical reference passages.", max_tokens=180)
    return passage.strip() if passage and "⚠️" not in passage else query
def needs_multihop_reasoning(query: str) -> bool:
    """
    Lightweight heuristic + LLM check for whether a query likely requires
    multi-hop relational reasoning (good candidate for GraphRAG escalation)
    versus a simple factual lookup (good for vector/BM25 alone).
    """
    heuristic_signals = [
        " and then ", " before ", " after ", " compare ", " versus ", " vs ",
        " relationship between", " connect", " depends on", " requires",
        " all the", " every", " which ones", " how many", " list all",
    ]
    lowered = query.lower()
    if any(sig in lowered for sig in heuristic_signals):
        return True
    prompt = (
        f"Does answering this question require connecting multiple distinct facts or "
        f"entities together (multi-hop reasoning), rather than a single direct lookup? "
        f"Answer with ONLY a JSON object: {{\"multihop\": true}} or {{\"multihop\": false}}.\n\n"
        f"Question: {query}"
    )
    result = fast_json_completion(prompt)
    return bool(result.get("multihop", False))
