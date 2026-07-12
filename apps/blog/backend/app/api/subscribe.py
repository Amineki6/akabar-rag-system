from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import subscriber_schema
from app.crud import subscriber_crud

router = APIRouter()

@router.post("/", response_model=subscriber_schema.SubscriberResponse)
def subscribe_newsletter(
    subscriber: subscriber_schema.SubscriberCreate,
    db: Session = Depends(get_db)
):
    """
    Subscribes a user to the newsletter safely by saving their email in the database.
    """
    existing_subscriber = subscriber_crud.get_subscriber_by_email(db, email=subscriber.email)
    if existing_subscriber:
        # Depending on UX, you can either throw an error or just return 200 to be nice 
        raise HTTPException(status_code=400, detail="Email is already subscribed.")
        
    return subscriber_crud.create_subscriber(db=db, subscriber=subscriber)
