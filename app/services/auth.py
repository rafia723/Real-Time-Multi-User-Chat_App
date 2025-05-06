from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.user import User
from ..models.token import RevokedToken
from ..config import settings
from ..exceptions import UserNotFoundException, InvalidPasswordException, UserAlreadyExistsException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise UserNotFoundException()
    if not verify_password(password, user.password):
        raise InvalidPasswordException()
    return user

def register_user(db: Session, username: str, email: str, password: str):
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise UserAlreadyExistsException()
    
    # Create new user
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, password=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def revoke_token(db: Session, token: str):
    revoked_token = RevokedToken(jti=token)
    db.add(revoked_token)
    db.commit()
    return {"message": "Successfully logged out"}