from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    text: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    user_id: int
    movie_id: int

    class Config:
        orm_mode = True
