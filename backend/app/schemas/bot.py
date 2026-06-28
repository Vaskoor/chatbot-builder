from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
class BotCreate(BaseModel):
    name: str = "My Chatbot"
    description: Optional[str] = None
    system_prompt: Optional[str] = None
class BotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
class BotOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    chunk_count: int = 0
    class Config:

        from_attributes = True
