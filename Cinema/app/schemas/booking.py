from pydantic import BaseModel

class BookingBase(BaseModel):
    user_id: int
    movie_id: int
    seat_number: int
    paid: bool

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int

    class Config:
        orm_mode = True
