from sqlalchemy.orm import Session
from app import models, schemas
import bcrypt
from app.core.security import create_access_token

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = models.User(username=user.username, 
                          email=user.email, 
                          hashed_password=hashed_password,
                          phone_number = user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "phone_number": db_user.phone_number
    }
    token = create_access_token(data=token_data)
    return db_user, token


def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
