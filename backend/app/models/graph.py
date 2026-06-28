from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
class GraphNode(Base):
    """
    An entity extracted from documents (e.g. 'Everest Base Camp Trek',
    'Annapurna Region', 'TIMS Permit'). Used for multi-hop GraphRAG queries.
    """
    __tablename__ = "graph_nodes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=True)  # e.g. PLACE, PERMIT, ACTIVITY, ORG
    description = Column(Text, nullable=True)
    source_chunk_ids = Column(Text, nullable=True)  # JSON list of chunk ids that mention it
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bot = relationship("Bot", back_populates="graph_nodes")
class GraphEdge(Base):
    """
    A relationship between two entities (e.g. 'Annapurna Base Camp Trek'
    --requires--> 'TIMS Permit'). Direction: source -> target.
    """
    __tablename__ = "graph_edges"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_id = Column(String, ForeignKey("bots.id"), nullable=False, index=True)
    source_node_id = Column(String, ForeignKey("graph_nodes.id"), nullable=False)
    target_node_id = Column(String, ForeignKey("graph_nodes.id"), nullable=False)
    relation = Column(String, nullable=False)  # e.g. "requires", "located_in", "part_of"
    weight = Column(Float, default=1.0)
    source_chunk_ids = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    bot = relationship("Bot", back_populates="graph_edges")
