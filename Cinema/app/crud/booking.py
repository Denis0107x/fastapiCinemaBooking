from sqlalchemy.orm import Session
from app import models, schemas

def create_booking(db: Session, user_id: int, movie_id: int, seat_number: int):
    db_booking = models.Booking(user_id=user_id, movie_id=movie_id, seat_number=seat_number)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings_for_user(db: Session, user_id: int):
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).all()

def get_bookings_for_movie(db: Session, movie_id: int):
    return db.query(models.Booking).filter(models.Booking.movie_id == movie_id).all()

def get_booked_seats(db: Session, movie_id: int):
    bookings = db.query(models.Booking).filter(models.Booking.movie_id == movie_id).all()
    booked_seats = [booking.seat_number for booking in bookings]
    return booked_seats

def get_booking_by_id(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

def update_booking_payment_status(db: Session, booking_id: int, paid: bool):
    booking = get_booking_by_id(db, booking_id)
    if booking:
        booking.paid = paid
        db.commit()
        db.refresh(booking)
        return booking
    return None