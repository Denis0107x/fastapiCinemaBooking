from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    seat_number = Column(Integer)

    user = relationship("User", back_populates="bookings")
    movie = relationship("Movie", back_populates="bookings")


    paid = Column(Boolean, default=False)  # Поле для статуса оплаты