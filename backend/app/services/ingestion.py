# backend/app/services/ingestion.py
"""
Ingestion pipeline: takes an uploaded file, extracts text, chunks it,
embeds it into the bot's Chroma collection, and records everything in
SQL. This is where the "dynamic update" behavior lives:
 
  - If a file at the same relative_path is uploaded again, the OLD
    document's chunks are marked inactive (superseded) in both SQLite
    and Chroma (not deleted outright, so history/audit is preserved),
    and the NEW document/chunks become version N+1 and are marked
    is_latest=True / is_active=True.
  - Retrieval always filters to is_active=True, so newer data
    automatically takes priority without any extra logic at query time.
"""
import os
import uuid
import hashlib
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.document import Document, Chunk
from app.services.extraction import extract_text, SUPPORTED_EXTENSIONS
from app.utils.chunking import chunk_text
from app.services.vector_store import add_chunks, deactivate_chunks
from app.services.graph_rag import upsert_graph_from_chunk, remove_chunk_from_graph

logger = logging.getLogger(__name__)

def _hash_file(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()

def ingest_file(
    db: Session,
    bot_id: str,
    collection_name: str,
    file_path: str,
    original_filename: str,
    relative_path: str | None,
    build_graph: bool = True,
) -> Document:
    """
    Processes a single file end-to-end. Handles supersession of any
    previous version found at the same relative_path for this bot.
    Always returns a Document (status may be 'failed' if an error occurs).
    """
    relative_path = relative_path or original_filename
    file_size = os.path.getsize(file_path)
    file_hash = _hash_file(file_path)

    # Find any previous "latest" document at this path for this bot
    previous = (
        db.query(Document)
        .filter(Document.bot_id == bot_id, Document.relative_path == relative_path, Document.is_latest == True)
        .first()
    )

    # If identical content re-uploaded, just update timestamp and return
    if previous and previous.file_hash == file_hash:
        previous.uploaded_at = datetime.utcnow()
        db.commit()
        return previous

    new_version = (previous.version + 1) if previous else 1

    document = Document(
        id=str(uuid.uuid4()),
        bot_id=bot_id,
        filename=original_filename,
        relative_path=relative_path,
        file_hash=file_hash,
        size=file_size,
        mime_type=None,
        status="processing",
        version=new_version,
        is_latest=True,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: .{ext}")

        text = extract_text(file_path, original_filename)
        if not text or not text.strip():
            raise ValueError("No extractable text found in file")

        chunks = chunk_text(text, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
        if not chunks:
            raise ValueError("Chunking produced no chunks")

        # --- Supersede the previous version's chunks (don't delete: keep audit trail) ---
        if previous:
            old_chunks = db.query(Chunk).filter(Chunk.document_id == previous.id, Chunk.is_active == True).all()
            old_chunk_ids = [c.id for c in old_chunks]
            if old_chunk_ids:
                deactivate_chunks(collection_name, old_chunk_ids)
                for c in old_chunks:
                    c.is_active = False
                    if build_graph:
                        try:
                            remove_chunk_from_graph(db, bot_id, c.id)
                        except Exception:
                            logger.exception("Failed to prune graph for superseded chunk %s", c.id)
            previous.is_latest = False
            previous.status = "superseded"
            db.commit()

        # --- Add new chunks ---
        chunk_ids, chunk_texts, metadatas = [], [], []
        for i, chunk in enumerate(chunks):
            cid = f"{document.id}_{i}"
            chunk_ids.append(cid)
            chunk_texts.append(chunk)
            metadatas.append({
                "bot_id": bot_id,
                "document_id": document.id,
                "source_file": relative_path,
                "chunk_index": i,
                "version": new_version,
                "is_active": True,
            })

        add_chunks(collection_name, chunk_ids, chunk_texts, metadatas)

        for i, (cid, chunk) in enumerate(zip(chunk_ids, chunk_texts)):
            db.add(Chunk(
                id=cid,
                document_id=document.id,
                bot_id=bot_id,
                chunk_index=i,
                text_preview=chunk[:300],
                version=new_version,
                is_active=True,
                priority_boost=min(0.05 * (new_version - 1), 0.2),
            ))
        db.commit()

        # --- Build/update knowledge graph from new chunks (best-effort, non-fatal) ---
        if build_graph and settings.enable_graph_rag:
            for cid, chunk in zip(chunk_ids, chunk_texts):
                try:
                    upsert_graph_from_chunk(db, bot_id, cid, chunk)
                except Exception:
                    logger.exception("Graph extraction failed for chunk %s; continuing", cid)

        document.status = "done"
        document.chunk_count = len(chunks)
        document.processed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        logger.exception("Ingestion failed for %s", original_filename)
        document.status = "failed"
        document.error_message = str(e)   # fixed: previously was `document.err`
        db.commit()
        # Re‑raise so the caller knows it failed (the router will catch it)
        raise

    return document   # always return the document