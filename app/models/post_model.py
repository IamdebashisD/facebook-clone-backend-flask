from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base
import uuid
import datetime


class Post(Base):
    __tablename__ = "posts"
    
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: str = Column(String(255), nullable=False)
    content: str = Column(Text, nullable=False)
    user_id: str = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    comments = relationship("Comment", backref="post", cascade="all, delete-orphan")
    likes = relationship("Like", backref="post", cascade="all, delete-orphan")
    
    
    # representation for debugging
    def __repr__(self) -> str:
        return f"<Post(ID={self.id}, CONTENT={self.content[:20]}, USER_ID={self.user_id})>"
    
