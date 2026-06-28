from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
class Document(Base):
    """
    Represents one uploaded file (or folder-relative file).
    A document can be RE-uploaded / updated, which creates a new `version`.
    Older versions' chunks are marked superseded so retrieval always
    prefers the newest version, but history is preserved for audit/rollback.
    """
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False)
    filename = Column(String, nullable=False)
    relative_path = Column(String, nullable=True)  # preserves folder structure
    file_hash = Column(String, nullable=True, index=True)  # content hash to detect real changes
    size = Column(Integer, default=0)
    mime_type = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, processing, done, failed, superseded
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)  # only one doc per (relative_path) is_latest=True
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    bot = relationship("Bot", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
class Chunk(Base):
    """
    Metadata mirror of what's stored in ChromaDB (the embeddings themselves
    live in Chroma; this table tracks lifecycle/versioning/priority so we
    can do SQL-side bookkeeping, supersede old chunks, and audit history).
    """
    __tablename__ = "chunks"
    id = Column(String, primary_key=True)  # same id used in Chroma
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)

    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    chunk_index = Column(Integer, default=0)
    text_preview = Column(Text, nullable=True)  # first ~300 chars for quick inspection
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)  # False = superseded by a newer version
    priority_boost = Column(Float, default=0.0)  # newest chunks get higher boost
    created_at = Column(DateTime, default=datetime.utcnow)
    document = relationship("Document", back_populates="chunks")
