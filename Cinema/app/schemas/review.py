from pydantic import BaseModel

class ReviewBase(BaseModel):
    text: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    user_id: int
    movie_id: int

    class Config:
        orm_mode = True