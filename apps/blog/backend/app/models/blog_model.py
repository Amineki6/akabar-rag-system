from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    subtitle = Column(String, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User")