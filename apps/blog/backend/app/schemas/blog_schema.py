from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base properties shared across all blog interactions
class BlogPostBase(BaseModel):
    title: str
    slug: str
    subtitle: Optional[str] = None
    content: str
    excerpt: Optional[str] = None
    image_url: Optional[str] = None
    is_published: bool = False
    is_featured: bool = False

# Schema used when creating a new post (inherits everything from Base)
class BlogPostCreate(BlogPostBase):
    pass

# Schema used when returning a post to the frontend
class BlogPostResponse(BlogPostBase):
    id: int
    created_at: datetime
    author_id: Optional[int] = None

    class Config:
        from_attributes = True