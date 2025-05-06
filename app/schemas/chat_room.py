from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatRoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoomResponse(ChatRoomBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRoomDetailResponse(ChatRoomResponse):
    creator_username: Optional[str] = None
    message_count: Optional[int] = None