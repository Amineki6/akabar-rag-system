from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas import blog_schema
from app.crud import blog_crud

# Make sure these imports are at the top
from app.api.deps import get_current_user
from app.models import user_model

router = APIRouter()

@router.post("/", response_model=blog_schema.BlogPostResponse)
def create_blog_post(
    blog: blog_schema.BlogPostCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user) # <-- THIS IS THE LOCK
):
    """
    Create a new blog post. Requires authentication.
    """
    existing_post = blog_crud.get_blog_by_slug(db, slug=blog.slug)
    if existing_post:
        raise HTTPException(status_code=400, detail="Blog post with this slug already exists.")
    
    # Pass the current_user.id to the database
    return blog_crud.create_blog(db=db, blog=blog, author_id=current_user.id)

@router.get("/", response_model=List[blog_schema.BlogPostResponse])
def read_all_blogs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of strictly published blog posts for the public site.
    """
    blogs = blog_crud.get_published_blogs(db, skip=skip, limit=limit)
    return blogs

@router.get("/admin", response_model=List[blog_schema.BlogPostResponse])
def read_admin_blogs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Retrieve a list of ALL blog posts (including drafts) for the Admin Dashboard.
    Requires valid authentication token.
    """
    blogs = blog_crud.get_blogs(db, skip=skip, limit=limit)
    return blogs

@router.get("/{slug}", response_model=blog_schema.BlogPostResponse)
def read_blog_by_slug(
    slug: str, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a single blog post by its slug.
    """
    blog = blog_crud.get_blog_by_slug(db, slug=slug)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    return blog

@router.put("/{slug}", response_model=blog_schema.BlogPostResponse)
def update_blog_post(
    slug: str,
    blog: blog_schema.BlogPostCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Update an existing blog post. Requires authentication.
    """
    existing_post = blog_crud.get_blog_by_slug(db, slug=slug)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    
    # Check if they are trying to change the slug to one that already exists
    if slug != blog.slug:
        post_with_new_slug = blog_crud.get_blog_by_slug(db, slug=blog.slug)
        if post_with_new_slug:
            raise HTTPException(status_code=400, detail="A blog post with the new slug already exists.")

    return blog_crud.update_blog(db=db, slug=slug, blog=blog)

@router.delete("/{slug}", status_code=204)
def delete_blog_post(
    slug: str, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Delete a blog post. Requires authentication.
    """
    existing_post = blog_crud.get_blog_by_slug(db, slug=slug)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    
    blog_crud.delete_blog(db=db, slug=slug)
    return None