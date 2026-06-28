"""
Vector store wrapper around ChromaDB. Each Bot gets its own Chroma
collection so different users'/bots' knowledge bases never mix
(hard tenant isolation, not just metadata filtering).
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.services.embedding import embed_texts, embed_text

import threading
_client = None
_lock = threading.Lock()
def get_chroma_client():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = chromadb.PersistentClient(
                    path=settings.chroma_persist_dir,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
    return _client
def get_collection(collection_name: str):
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
def add_chunks(collection_name: str, ids: list[str], texts: list[str], metadatas: list[dict]):
    if not texts:
        return
    collection = get_collection(collection_name)
    embeddings = embed_texts(texts)
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
def deactivate_chunks(collection_name: str, chunk_ids: list[str]):
    """Mark chunks as superseded by setting metadata flag rather than deleting,
    so we keep history. Active retrieval filters these out via `where`."""
    if not chunk_ids:
        return
    collection = get_collection(collection_name)
    existing = collection.get(ids=chunk_ids)
    if not existing or not existing.get("ids"):
        return
    new_metas = []
    for meta in existing["metadatas"]:
        m = dict(meta)
        m["is_active"] = False
        new_metas.append(m)
    collection.update(ids=existing["ids"], metadatas=new_metas)
def delete_chunks(collection_name: str, chunk_ids: list[str]):
    if not chunk_ids:
        return
    collection = get_collection(collection_name)
    collection.delete(ids=chunk_ids)
def delete_by_document(collection_name: str, document_id: str):
    collection = get_collection(collection_name)

    collection.delete(where={"document_id": document_id})
def vector_search(collection_name: str, query: str, top_k: int = 20, active_only: bool = True) -> list[dict]:
    collection = get_collection(collection_name)
    if collection.count() == 0:
        return []
    where = {"is_active": True} if active_only else None
    query_emb = embed_text(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=min(top_k, collection.count()),
        where=where,
    )
    hits = []
    if results.get("documents") and results["documents"][0]:
        for i, doc_text in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else 1.0
            # cosine distance -> similarity score
            similarity = 1.0 - distance
            hits.append({
                "chunk_id": results["ids"][0][i],
                "text": doc_text,
                "source_file": meta.get("source_file", "unknown"),
                "document_id": meta.get("document_id"),
                "version": meta.get("version", 1),
                "vector_score": similarity,
                "metadata": meta,
            })
    return hits
def get_all_active_chunks(collection_name: str) -> list[dict]:
    """Used to build the BM25 index — needs the full active corpus."""
    collection = get_collection(collection_name)
    if collection.count() == 0:
        return []
    results = collection.get(where={"is_active": True})
    chunks = []
    if results and results.get("ids"):
        for i, cid in enumerate(results["ids"]):
            meta = results["metadatas"][i] if results.get("metadatas") else {}
            chunks.append({
                "chunk_id": cid,
                "text": results["documents"][i],
                "source_file": meta.get("source_file", "unknown"),
                "document_id": meta.get("document_id"),
                "version": meta.get("version", 1),
                "metadata": meta,
            })
    return chunks
def delete_collection(collection_name: str):
    client = get_chroma_client()
    try:

        client.delete_collection(collection_name)
    except Exception:
        pass
