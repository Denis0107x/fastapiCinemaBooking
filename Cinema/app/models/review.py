from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    text = Column(String)

    # Связь с пользователями и фильмами
    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")