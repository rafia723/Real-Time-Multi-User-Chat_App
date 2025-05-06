from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    user_id: int
    room_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MessageDetailResponse(MessageResponse):
    username: str