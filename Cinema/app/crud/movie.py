from sqlalchemy.orm import Session
from app import models, schemas

def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()

def get_movies(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Movie).offset(skip).limit(limit).all()

def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def search_movies(db: Session, title: str = None, country: str = None, genre: str = None, year: int = None, premiere_date: str = None):
    query = db.query(models.Movie)
    if title:
        query = query.filter(models.Movie.title.ilike(f"%{title}%"))
    if country:
        query = query.filter(models.Movie.country.ilike(f"%{country}%"))
    if genre:
        query = query.filter(models.Movie.genre.ilike(f"%{genre}%"))
    if year:
        query = query.filter(models.Movie.year == year)
    if premiere_date:
        query = query.filter(models.Movie.premiere_date == premiere_date)
    return query.all()

