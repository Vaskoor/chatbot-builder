from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
class Conversation(Base):
    """
    A persistent chat thread, scoped to one user + one bot.
    Holds a rolling summary once the thread gets long, so memory
    stays efficient instead of growing the prompt unboundedly.
    """
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, default="New Conversation")
    rolling_summary = Column(Text, nullable=True)  # compressed memory of older turns
    summarized_through_message_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bot = relationship("Bot", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                             order_by="Message.created_at")
class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # retrieved chunks/citations used for this answer
    retrieval_meta = Column(JSON, nullable=True)  # debug info: strategy used, scores, graph hits
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")
    map_data = Column(JSON, nullable=True)