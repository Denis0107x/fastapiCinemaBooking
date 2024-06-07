from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    poster = Column(String)
    country = Column(String)
    genre = Column(String)
    director = Column(String)
    year = Column(Integer)
    premiere_date = Column(String)
    duration = Column(Integer)
    rating = Column(Float)
    
    bookings = relationship("Booking", back_populates="movie")
    reviews = relationship("Review", back_populates="movie")
    messages = relationship("Message", back_populates="movie")

