import os
import shutil
import tempfile

import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.document import Document, Chunk
from app.schemas.document import DocumentOut, IngestResult
from app.services.ingestion import ingest_file
from app.services.vector_store import delete_by_document
from app.services.graph_rag import remove_chunk_from_graph
from app.routers.bots import _get_owned_bot
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bots/{bot_id}/documents", tags=["documents"])
@router.post("/upload", response_model=List[IngestResult])
async def upload_documents(
    bot_id: str,
    files: List[UploadFile] = File(...),
    relative_paths: Optional[List[str]] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Upload one or many files (also used for folder uploads — the frontend
    sends each file's webkitRelativePath in `relative_paths`, aligned by
    index, so folder structure is preserved as document source labels).
    Re-uploading a file at the same relative path creates a NEW VERSION
    and automatically supersedes the old chunks (dynamic update behavior).
    """
    bot = _get_owned_bot(db, bot_id, user)
    results = []
    for i, upload in enumerate(files):
        rel_path = None
        if relative_paths and i < len(relative_paths):
            rel_path = relative_paths[i]
        tmp_path = None
        try:
            suffix = "_" + os.path.basename(upload.filename)
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(upload.file, tmp)
                tmp_path = tmp.name
            document = ingest_file(
                db=db,
                bot_id=bot.id,
                collection_name=bot.chroma_collection_name,
                file_path=tmp_path,
                original_filename=upload.filename,
                relative_path=rel_path or upload.filename,
            )

            results.append(IngestResult(
                document_id=document.id,
                filename=document.filename,
                chunk_count=document.chunk_count,
                version=document.version,
                status=document.status,
                message="Updated existing document (new version)" if document.version > 1 else "Ingested successfully"
                        if document.status == "done" else (document.error_message or "Failed"),
            ))
        except Exception as e:
            logger.exception("Upload failed for %s", upload.filename)
            results.append(IngestResult(
                document_id="", filename=upload.filename, chunk_count=0,
                version=0, status="failed", message=str(e),
            ))
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
    return results
@router.get("", response_model=List[DocumentOut])
def list_documents(bot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    docs = (
        db.query(Document)
        .filter(Document.bot_id == bot.id)
        .order_by(desc(Document.uploaded_at))
        .all()
    )
    return docs
@router.get("/{document_id}/versions", response_model=List[DocumentOut])
def document_versions(bot_id: str, document_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Returns the full version history for the file at the same path as the given document."""
    bot = _get_owned_bot(db, bot_id, user)
    target = db.query(Document).filter(Document.id == document_id, Document.bot_id == bot.id).first()
    if not target:
        raise HTTPException(404, "Document not found")
    versions = (
        db.query(Document)
        .filter(Document.bot_id == bot.id, Document.relative_path == target.relative_path)
        .order_by(desc(Document.version))
        .all()
    )
    return versions
@router.delete("/{document_id}")
def delete_document(bot_id: str, document_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = _get_owned_bot(db, bot_id, user)
    document = db.query(Document).filter(Document.id == document_id, Document.bot_id == bot.id).first()
    if not document:
        raise HTTPException(404, "Document not found")
    chunk_ids = [c.id for c in db.query(Chunk).filter(Chunk.document_id == document.id).all()]
    delete_by_document(bot.chroma_collection_name, document.id)
    for cid in chunk_ids:

        try:
            remove_chunk_from_graph(db, bot.id, cid)
        except Exception:
            logger.exception("Failed to prune graph for deleted chunk %s", cid)
    db.query(Chunk).filter(Chunk.document_id == document.id).delete()
    db.delete(document)
    db.commit()
    return {"success": True}
