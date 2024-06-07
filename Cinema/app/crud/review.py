from sqlalchemy.orm import Session
from app import models, schemas

def create_review(db: Session, review: schemas.ReviewCreate, user_id: int, movie_id: int):
    db_review = models.Review(**review.dict(), user_id=user_id, movie_id=movie_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_for_movie(db: Session, movie_id: int):
    return db.query(models.Review).filter(models.Review.movie_id == movie_id).all()
