from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base
import datetime
import uuid
import bcrypt


class User(Base):
    __tablename__ = "users" # Table name in database
    
    id: str = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())) # Using UUID as primary key
    username: str = Column(String(50), nullable=False, unique=True)
    email: str = Column(String(100), nullable=False, unique=True)
    _password: str = Column("password", String(255), nullable=False)
    created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    posts = relationship("Post", backref="user", cascade="all, delete-orphan")
    comments = relationship("Comment", backref="user", cascade="all, delete-orphan")
    likes = relationship("Like", backref="user", cascade="all, delete-orphan")
    
    def __init__(self, username: str, email: str, password: str)-> None:
        self.username = username
        self.email = email
        self.password = password
    
    
    # Password property: Getter
    @property
    def password(self) -> str:
        return self._password
    
    @password.setter
    def password(self, plain_text: str) -> None:
        self._password = bcrypt.hashpw(
            plain_text.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')
        
    def verify_password(self, plain_text: str)-> None:
        return bcrypt.checkpw(
            plain_text.encode('utf-8'), self._password.encode('utf-8')
        )  
    
    def __repr__(self) -> str:
        return f"<User(ID={self.id}, USERNAME={self.username}, EMAIL={self.email})>"
        
