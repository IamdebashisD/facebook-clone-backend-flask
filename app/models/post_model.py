from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
import datetime

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    content: str = Column(Text, nullable=False)
    author_id: str = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", backref="posts")
    
    # representation for debugging
    def __repr__(self) -> str:
        return f"<Post(id={self.id}, content={self.content[:20]}, author_id={self.author_id})>"
    
    
        
        
    

    
