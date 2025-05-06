import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

class Settings:
    PROJECT_NAME: str = "Chat App API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database - No default values for sensitive data
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")  
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB")

    if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB]):
        raise ValueError("Missing one or more required database environment variables.")
    
    DATABASE_URL: str = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in environment variables.")
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100

settings = Settings()
