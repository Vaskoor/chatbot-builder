from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
class UserCreate(BaseModel):

    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
class RefreshRequest(BaseModel):
    refresh_token: str
