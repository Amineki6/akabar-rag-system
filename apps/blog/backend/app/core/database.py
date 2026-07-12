import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Fetch the database URL from the environment (set in docker-compose)
# Fallback is provided for local non-Docker testing
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:adminpassword@localhost:5432/akabar_db"
)

# The engine is the core interface to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal will be used to create individual database sessions for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models (if you haven't defined it here already)
Base = declarative_base()

# Dependency function to get the database session in our routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()