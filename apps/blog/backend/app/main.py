from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.models import user_model, blog_model, subscriber_model
# Import the API routers
from app.api import blog
from app.api import auth
from app.api import subscribe

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Akabar Blog API",
    description="Backend API for the fullstack blog project and CMS.",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows your frontend to communicate with your backend during development.
# When Dockerized with Nginx as a proxy, this configuration can be locked down further.
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(blog.router, prefix="/api/blogs", tags=["Blogs"])
app.include_router(subscribe.router, prefix="/api/subscribe", tags=["subscribe"])

@app.get("/health", tags=["System"])
def health_check():
    """
    A simple health check endpoint to verify the API is up and running.
    """
    return {"status": "ok", "message": "Akabar API is running"}