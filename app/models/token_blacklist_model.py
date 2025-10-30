from sqlalchemy import Column, String , Text, ForeignKey, DateTime
from app.database.db import Base
import uuid
from datetime import datetime, timezone


class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'
    
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token: str = Column(Text, nullable=False, unique=True)              # JWT string
    token_type: str = Column(String(10), nullable=False)                # Token Type (access or refresh)
    user_id: str =  Column(String(36), nullable=False)
    blacklisted_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reason: str = Column(String(100), default="logout", nullable=True)
    
    def __repr__(self) -> str:
        return f"<TokenBlacklist( user_id={self.user_id}, reason={self.reason}, blacklisted_at={self.blacklisted_at})>"
    