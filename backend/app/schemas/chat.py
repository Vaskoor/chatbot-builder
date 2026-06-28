from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
class SourceChunk(BaseModel):
    text: str
    source_file: Optional[str] = None
    score: Optional[float] = None
    chunk_id: Optional[str] = None
class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: List[Dict[str, Any]] = []
    retrieval_strategy: Optional[str] = None
class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    retrieval_meta: Optional[Dict[str, Any]] = None
    map_data: Optional[List[Dict[str, Any]]] = None   # <-- add this
    created_at: datetime

    class Config:
        from_attributes = True
class ConversationOut(BaseModel):
    id: str
    bot_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
class ConversationDetail(ConversationOut):
    messages: List[MessageOut] = []
    
class MapLocation(BaseModel):
    day: int
    name: str
    lat: float
    lng: float
    description: Optional[str] = None   # e.g., "Hotel", "Checkpoint"

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: List[Dict[str, Any]] = []
    retrieval_strategy: Optional[str] = None
    map_data: Optional[List[MapLocation]] = None   # new