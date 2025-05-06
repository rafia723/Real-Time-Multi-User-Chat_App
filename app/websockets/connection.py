from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Set
import json
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..models.message import Message
from ..models.token import RevokedToken
from ..schemas.message import MessageCreate


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int, username: str):
        await websocket.accept()
        print(f"[CONNECT] WebSocket connected: room={room_id}, user_id={user_id}, username={username}")

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)

        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

        await self.broadcast(
            room_id,
            {
                "type": "system",
                "content": f"User {username} has joined the chat"
            }
        )

    def disconnect(self, websocket: WebSocket, room_id: int, user_id: int):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            if len(self.active_connections[room_id]) == 0:
                del self.active_connections[room_id]

        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if len(self.user_connections[user_id]) == 0:
                del self.user_connections[user_id]

        print(f"[DISCONNECT] User {user_id} disconnected from room {room_id}")

    async def broadcast(self, room_id: int, message: dict):
        print(f"[BROADCAST] Broadcasting in room {room_id}: {message}")
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"[ERROR] Failed to send message to a client: {e}")

    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(json.dumps(message))


manager = ConnectionManager()

async def get_user_from_token(token: str, db: Session):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    revoked_token = db.query(RevokedToken).filter(RevokedToken.jti == token).first()
    if revoked_token:
        print(f"[TOKEN] Token revoked for: {token}")
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("[TOKEN] Username not found in token payload")
            raise credentials_exception
    except JWTError as e:
        print(f"[TOKEN ERROR] JWTError: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        print(f"[AUTH ERROR] User not found: {username}")
        raise credentials_exception

    return user


async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    print(f"[REQUEST] WebSocket connection attempt in room {room_id} with token {token[:10]}...")

    try:
        user = await get_user_from_token(token, db)
        print(f"[AUTH] Authenticated user: {user.username} (ID: {user.id})")
    except HTTPException:
        await websocket.close(code=1008)
        print(f"[AUTH FAILED] Closing socket for token {token[:10]}...")
        return

    await manager.connect(websocket, room_id, user.id, user.username)

    try:
        while True:
            try:
                data = await websocket.receive_text()
                print(f"[RECEIVE] From {user.username}: {data}")
                message_data = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON decode failed: {e}")
                await websocket.send_text("Invalid JSON format. Please send proper JSON.")
                continue

            if "content" in message_data:
                content = message_data["content"]
                timestamp = datetime.utcnow()

                new_message = Message(
                    user_id=user.id,
                    room_id=room_id,
                    content=content,
                    timestamp=timestamp
                )
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                print(f"[DB] Stored message from {user.username} in DB: {content}")

                await manager.broadcast(
                    room_id,
                    {
                        "type": "message",
                        "user_id": user.id,
                        "username": user.username,
                        "content": content,
                        "timestamp": timestamp.isoformat()
                    }
                )
            else:
                print(f"[WARN] Message from {user.username} missing 'content': {message_data}")

    except WebSocketDisconnect:
        print(f"[DISCONNECT] {user.username} disconnected.")
        manager.disconnect(websocket, room_id, user.id)
        await manager.broadcast(
            room_id,
            {
                "type": "system",
                "content": f"User {user.username} has left the chat"
            }
        )
    except Exception as e:
        print(f"[ERROR] Unhandled exception: {e}")
