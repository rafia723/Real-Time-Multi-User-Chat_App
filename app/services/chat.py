from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..models.chat_room import ChatRoom
from ..models.message import Message
from ..models.user import User
from ..exceptions import ChatRoomNotFoundException
from ..schemas.chat_room import ChatRoomCreate
from ..schemas.message import MessageCreate

def get_chat_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ChatRoom).offset(skip).limit(limit).all()

def search_chat_rooms(db: Session, query: str, skip: int = 0, limit: int = 100):
    search_pattern = f"%{query}%"
    return db.query(ChatRoom).filter(ChatRoom.name.like(search_pattern)).offset(skip).limit(limit).all()

def get_chat_room(db: Session, room_id: int):
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise ChatRoomNotFoundException()
    return room

def create_chat_room(db: Session, chat_room: ChatRoomCreate, user_id: int):
    db_chat_room = ChatRoom(name=chat_room.name, created_by=user_id)
    db.add(db_chat_room)
    db.commit()
    db.refresh(db_chat_room)
    return db_chat_room

def get_room_details(db: Session, room_id: int):
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise ChatRoomNotFoundException()
    
    # Get username of creator
    creator = db.query(User).filter(User.id == room.created_by).first()
    creator_username = creator.username if creator else None
    
    # Get message count
    message_count = db.query(func.count(Message.id)).filter(Message.room_id == room_id).scalar()
    
    return {
        "id": room.id,
        "name": room.name,
        "created_by": room.created_by,
        "created_at": room.created_at,
        "creator_username": creator_username,
        "message_count": message_count
    }

def get_room_messages(db: Session, room_id: int, skip: int = 0, limit: int = 100):
    # Check if room exists
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise ChatRoomNotFoundException()
    
    # Get messages with usernames
    messages = db.query(
        Message.id, 
        Message.content, 
        Message.user_id, 
        Message.room_id, 
        Message.timestamp,
        User.username
    ).join(User).filter(
        Message.room_id == room_id
    ).order_by(
        Message.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    # Format messages
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "id": msg.id,
            "content": msg.content,
            "user_id": msg.user_id,
            "room_id": msg.room_id,
            "timestamp": msg.timestamp,
            "username": msg.username
        })
    
    return formatted_messages

def create_message(db: Session, message: MessageCreate, user_id: int, room_id: int):
    # Check if room exists
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise ChatRoomNotFoundException()
    
    # Create message
    db_message = Message(
        content=message.content,
        user_id=user_id,
        room_id=room_id
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Get username
    user = db.query(User).filter(User.id == user_id).first()
    
    return {
        "id": db_message.id,
        "content": db_message.content,
        "user_id": db_message.user_id,
        "room_id": db_message.room_id,
        "timestamp": db_message.timestamp,
        "username": user.username
    }

def search_messages(db: Session, room_id: int, query: str, skip: int = 0, limit: int = 100):
    # Check if room exists
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise ChatRoomNotFoundException()
    
    # Search messages
    search_pattern = f"%{query}%"
    messages = db.query(
        Message.id, 
        Message.content, 
        Message.user_id, 
        Message.room_id, 
        Message.timestamp,
        User.username
    ).join(User).filter(
        Message.room_id == room_id,
        Message.content.like(search_pattern)
    ).order_by(
        Message.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    # Format messages
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "id": msg.id,
            "content": msg.content,
            "user_id": msg.user_id,
            "room_id": msg.room_id,
            "timestamp": msg.timestamp,
            "username": msg.username
        })
    
    return formatted_messages