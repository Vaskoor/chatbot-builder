"""
Chunking: splits raw text into overlapping, sentence-aware chunks.
Uses tiktoken for accurate token counting (LLM-aware sizing) rather than
naive character counts.
"""
import re
import tiktoken
_encoder = None
def _get_encoder():
    global _encoder
    if _encoder is None:
        try:
            _encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            _encoder = None
    return _encoder
def count_tokens(text: str) -> int:
    enc = _get_encoder()
    if enc is None:
        return max(1, len(text) // 4)  # rough fallback
    return len(enc.encode(text))
def split_sentences(text: str) -> list[str]:
    # Split on sentence boundaries while keeping paragraph breaks meaningful.
    text = text.replace("\r\n", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = []
    for para in paragraphs:
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", para)
        for p in parts:
            p = p.strip()
            if p:
                sentences.append(p)
        sentences.append("")  # paragraph boundary marker (filtered later but helps spacing)
    return [s for s in sentences if s != ""]
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """
    Token-aware, sentence-boundary-respecting chunking with overlap.
    chunk_size/overlap are measured in tokens for LLM-context accuracy.
    """
    if not text or not text.strip():
        return []

    sentences = split_sentences(text)
    if not sentences:
        return []
    chunks = []
    current: list[str] = []
    current_tokens = 0
    for sent in sentences:
        stoks = count_tokens(sent)
        if current_tokens + stoks > chunk_size and current:
            chunks.append(" ".join(current).strip())
            # build overlap from the tail of the current chunk
            overlap_sents, overlap_tok = [], 0
            for s in reversed(current):
                t = count_tokens(s)
                if overlap_tok + t <= overlap:
                    overlap_sents.insert(0, s)
                    overlap_tok += t
                else:
                    break
            current, current_tokens = overlap_sents, overlap_tok
        current.append(sent)
        current_tokens += stoks
    if current:
        chunks.append(" ".join(current).strip())
    return [c for c in chunks if c]
