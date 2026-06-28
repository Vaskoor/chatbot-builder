"""
Embedding model loader. Loaded once as a singleton since SentenceTransformer
model loading is expensive (downloads + initializes on first use).
"""
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import threading
_model = None
_lock = threading.Lock()

def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer(settings.embedding_model)
    return _model
def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedder()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()
def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
