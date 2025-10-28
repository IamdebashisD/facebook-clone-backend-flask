from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from app.database.db import Base
import uuid 
from datetime import datetime, timezone


class Comment(Base):
    __tablename__ = "comments"
    
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: str = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False) 
    user_id: str = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    
    def __repr__(self):
        return f"<Comment(ID={self.id}, POST_ID={self.post_id}, USER_ID={self.user_id}, CONTENT={self.content[:20]})>"