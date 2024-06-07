from sqlalchemy.orm import Session
from app.models import Message
from app.schemas import MessageCreate

def create_message(db: Session, message: MessageCreate, user_id: int, movie_id: int):
    db_message = Message(**message.dict(), user_id=user_id, movie_id=movie_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, movie_id: int, skip: int = 0, limit: int = 100):
    return db.query(Message).filter(Message.movie_id == movie_id).offset(skip).limit(limit).all()
