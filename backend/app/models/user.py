from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from datetime import datetime
import uuid
from app.core.database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    bots = relationship("Bot", back_populates="owner", cascade="all, delete-orphan")
