from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token

from app.core.database import get_db
from app.schemas import user_schema
from app.crud import user_crud

router = APIRouter()

@router.post("/register", response_model=user_schema.UserResponse, status_code=status.HTTP_201_CREATED)
def register_admin(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new admin user.
    """
    # Restrict registration to only the first admin account
    if user_crud.get_user_count(db) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="An admin account already exists. Registration is disabled."
        )
        
    # Check if email is already taken
    existing_email = user_crud.get_user_by_email(db, email=user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username is already taken
    existing_username = user_crud.get_user_by_username(db, username=user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
        
    return user_crud.create_user(db=db, user=user)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Authenticate an admin user and return a JWT token.
    """
    # 1. Find the user
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    # 2. Verify the password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
        
    # 3. Generate the token
    access_token = create_access_token(data={"sub": user.username, "id": user.id})
    
    # 4. Return token in the exact format OAuth2 expects
    return {"access_token": access_token, "token_type": "bearer"}