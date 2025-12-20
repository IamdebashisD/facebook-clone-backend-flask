from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from app.database.db import Base
import uuid
from datetime import datetime, timezone

class Like(Base):
    __tablename__ = "likes"
    
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: str = Column(String(36), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id: str = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
    )
    
    def __repr__(self) -> str:
        return f"<Like(ID={self.id}, POST_ID={self.post_id} USER_ID={self.user_id})>"
    
        
