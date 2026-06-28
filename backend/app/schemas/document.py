from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentOut(BaseModel):
    id: str
    filename: str
    relative_path: Optional[str] = None
    size: int
    status: str
    chunk_count: int
    version: int
    is_latest: bool
    uploaded_at: datetime
    error_message: Optional[str] = None
    class Config:
        from_attributes = True
class IngestResult(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    version: int
    status: str
    message: str
