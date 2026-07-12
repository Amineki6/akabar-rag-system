from sqlalchemy.orm import Session
from app.models import blog_model
from app.schemas import blog_schema

def get_blogs(db: Session, skip: int = 0, limit: int = 100):
    """Fetch a list of all blog posts (Drafts and Published)."""
    return db.query(blog_model.BlogPost).offset(skip).limit(limit).all()

def get_published_blogs(db: Session, skip: int = 0, limit: int = 100):
    """Fetch a list of strictly published blog posts."""
    return db.query(blog_model.BlogPost).filter(blog_model.BlogPost.is_published == True).offset(skip).limit(limit).all()

def get_blog_by_slug(db: Session, slug: str):
    """Fetch a single blog post by its URL-friendly slug."""
    return db.query(blog_model.BlogPost).filter(blog_model.BlogPost.slug == slug).first()

def create_blog(db: Session, blog: blog_schema.BlogPostCreate, author_id: int):
    db_blog = blog_model.BlogPost(**blog.model_dump(), author_id=author_id)
    
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog) # Refresh to get the generated ID and timestamp
    
    return db_blog

def update_blog(db: Session, slug: str, blog: blog_schema.BlogPostCreate):
    db_blog = get_blog_by_slug(db, slug=slug)
    if db_blog:
        for key, value in blog.model_dump().items():
            setattr(db_blog, key, value)
        db.commit()
        db.refresh(db_blog)
    return db_blog

def delete_blog(db: Session, slug: str):
    db_blog = get_blog_by_slug(db, slug=slug)
    if db_blog:
        db.delete(db_blog)
        db.commit()
    return db_blog