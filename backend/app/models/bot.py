from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
class Bot(Base):
    """
    A Bot is a self-contained chatbot instance: its own knowledge base
    (documents/chunks/graph), its own conversations, owned by one user.
    This is what the 'chatbot builder' produces.
    """
    __tablename__ = "bots"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, default="My Chatbot")
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)  # custom persona/instructions
    chroma_collection_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="bots")
    documents = relationship("Document", back_populates="bot", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="bot", cascade="all, delete-orphan")
    graph_nodes = relationship("GraphNode", back_populates="bot", cascade="all, delete-orphan")
    graph_edges = relationship("GraphEdge", back_populates="bot", cascade="all, delete-orphan")
