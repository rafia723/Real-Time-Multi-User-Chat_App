from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.chat_room import ChatRoomCreate, ChatRoomResponse, ChatRoomDetailResponse
from ..schemas.message import MessageCreate, MessageDetailResponse
from ..services.chat import (
    get_chat_rooms, get_chat_room, create_chat_room, get_room_details, 
    get_room_messages, create_message, search_chat_rooms, search_messages
)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/rooms", response_model=List[ChatRoomResponse])
async def read_chat_rooms(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all available chat rooms.
    Optional search parameter to filter rooms by name.
    """
    if search:
        return search_chat_rooms(db, search, skip, limit)
    return get_chat_rooms(db, skip, limit)

@router.post("/rooms", response_model=ChatRoomResponse, status_code=201)
async def create_new_chat_room(
    chat_room: ChatRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat room.
    """
    return create_chat_room(db, chat_room, current_user.id)

@router.get("/rooms/{room_id}", response_model=ChatRoomDetailResponse)
async def read_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific chat room.
    """
    return get_room_details(db, room_id)

@router.get("/rooms/{room_id}/messages", response_model=List[MessageDetailResponse])
async def read_room_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve messages from a chat room.
    Optional search parameter to filter messages by content.
    """
    if search:
        return search_messages(db, room_id, search, skip, limit)
    return get_room_messages(db, room_id, skip, limit)

@router.post("/rooms/{room_id}/messages", response_model=MessageDetailResponse, status_code=201)
async def create_room_message(
    room_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Post a new message to a chat room.
    """
    return create_message(db, message, current_user.id, room_id)