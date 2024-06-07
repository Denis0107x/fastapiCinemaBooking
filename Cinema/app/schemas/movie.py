from pydantic import BaseModel

class MovieBase(BaseModel):
    title: str
    description: str
    poster: str
    country: str
    genre: str
    director: str
    year: int
    premiere_date: str
    duration: int
    rating: float

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True
