from sqlalchemy.orm import Session
from app.models import subscriber_model
from app.schemas import subscriber_schema

def create_subscriber(db: Session, subscriber: subscriber_schema.SubscriberCreate):
    db_subscriber = subscriber_model.Subscriber(email=subscriber.email)
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber

def get_subscriber_by_email(db: Session, email: str):
    return db.query(subscriber_model.Subscriber).filter(subscriber_model.Subscriber.email == email).first()
