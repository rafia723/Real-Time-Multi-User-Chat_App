# Real-Time Chat Application

A multi-user real-time chat application built with FastAPI and MySQL.

## Features

- User registration and authentication (JWT)
- Real-time messaging via WebSockets
- Chat rooms
- Message history
- Search functionality for rooms and messages

## Tech Stack

- **Backend**: FastAPI
- **Database**: MySQL
- **Authentication**: JWT
- **Real-time Communication**: WebSockets
- **Containerization**: Docker

## File Structure

```
chat_app/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application setup
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection and session
│   ├── dependencies.py        # Dependency injection
│   ├── exceptions.py          # Custom exceptions
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   └── chat.py            # Chat endpoints
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py  
│   │   ├── user.py            # User model
│   │   ├── chat_room.py       # ChatRoom model
│   │   ├── message.py         # Message model
│   │   └── token.py           # RevokedToken model
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas
│   │   ├── chat_room.py       # ChatRoom schemas
│   │   ├── message.py         # Message schemas
│   │   └── token.py           # Token schemas
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication services
│   │   └── chat.py            # Chat services
│   └── websockets/            # WebSocket handlers
│       ├── __init__.py
│       └── connection.py      # WebSocket connections
├── env
├── Dockerfile                 # Docker setup for API
├── docker-compose.yml         # Docker Compose config
├── init.sql                   # Initial database setup
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Entity Relationship Diagram (ERD)

```
+--------------+          +--------------+          +--------------+
|    users     |          |  chat_rooms  |          |   messages   |
+--------------+          +--------------+          +--------------+
| id (PK)      |          | id (PK)      |          | id (PK)      |
| username     |<-------->| created_by   |<-------->| user_id (FK) |
| email        |    1:N   | name         |    1:N   | room_id (FK) |
| password     |          | created_at   |          | content      |
| created_at   |          +--------------+          | timestamp    |
+--------------+                                    +--------------+

+--------------+
|revoked_tokens|
+--------------+
| id (PK)      |
| jti          |
| revoked_at   |
+--------------+
```


## API Endpoints

| Method | Endpoint                       | Description                           |
|--------|--------------------------------|---------------------------------------|
| POST   | /api/register                  | Register a new user                   |
| POST   | /api/login                     | Authenticate a user and create a JWT  |
| POST   | /api/logout                    | End a user session (revoke JWT)       |
| GET    | /api/chat/rooms                | Retrieve all available chat rooms     |
| GET    | /api/chat/rooms/{id}           | Get details of a specific chat room   |
| POST   | /api/chat/rooms                | Create a new chat room                |
| GET    | /api/chat/rooms/{id}/messages  | Retrieve messages from a chat room    |
| POST   | /api/chat/rooms/{id}/messages  | Post a new message to a chat room     |
| WS     | /ws/{room_id}?token={token}    | WebSocket connection for real-time chat |

## Setup Instructions

### Prerequisites

- Docker and Docker Compose

### Installation and Running

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd chat-app
   ```

2. Build and run with Docker Compose
   ```bash
   docker-compose up --build
   ```

3. The API will be available at `http://localhost:8000`
   - API documentation: `http://localhost:8000/api/docs`
   - ReDoc documentation: `http://localhost:8000/api/redoc`

## Testing the API

You can use the Swagger UI at `/api/docs` to test the API endpoints, or use tools like Postman or curl.

### Example: Register a user

```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpassword"}'
```

### Example: Login

```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword"
```

### Example: Getting chat rooms

```bash
curl -X GET "http://localhost:8000/api/chat/rooms" \
  -H "Authorization: Bearer {your_access_token}"
```

## WebSocket Connection

To connect to a chat room via WebSocket, use the following URL format:

```
ws://localhost:8000/ws/{room_id}?token={your_access_token}
```

## Database Backup and Restore

### Creating a Backup

```bash
docker exec chat-app-db sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" chat_app' > backup.sql
```

### Restoring from Backup

```bash
cat backup.sql | docker exec -i chat-app-db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" chat_app'
```

## Challenges and Solutions

1. **Challenge**: Implementing token revocation for logout functionality
   **Solution**: Created a `revoked_tokens` table to keep track of invalidated tokens

2. **Challenge**: Real-time communication with multiple clients
   **Solution**: Used FastAPI's WebSocket support with a connection manager to handle multiple clients

3. **Challenge**: Database connection management in a containerized environment
   **Solution**: Used dependency injection for database sessions and proper connection pooling

4. **Challenge**: Ensuring security with JWT authentication
   **Solution**: Implemented proper token validation and verification for API endpoints and WebSocket connections

## Design Decisions

1. **Architecture**: Chose a layered architecture with clear separation between models, schemas, services, and API routes
2. **Authentication**: Used JWT for stateless authentication to support multiple clients and services
3. **Real-time Communication**: Implemented WebSockets for true real-time messaging
4. **Docker Containerization**: Used Docker to ensure consistent development and production environments
5. **API Documentation**: Utilized FastAPI's built-in Swagger UI for comprehensive API documentation

## Future Improvements

- Add user profiles with avatars
- Implement private messaging
- Add file sharing capabilities
- Enhance search with fuzzy matching
- Implement read receipts
- Add notifications for new messages