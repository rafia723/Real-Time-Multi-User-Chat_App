from sqlalchemy import Column, Integer, String, DateTime, func

from ..database import Base

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, nullable=False)
    revoked_at = Column(DateTime, default=func.now())