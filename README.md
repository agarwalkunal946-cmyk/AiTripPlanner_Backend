# Trip Planner Backend API

A comprehensive FastAPI backend for trip planning and management with user authentication, trip creation, search, and social features.

## Features

- **User Authentication**: JWT-based authentication with registration, login, and profile management
- **Trip Management**: Create, read, update, delete trips with detailed information
- **Search & Filter**: Advanced search functionality with multiple filters
- **Social Features**: Join/leave trips, view user-specific trips
- **Profile Management**: Update user profiles, change passwords
- **CORS Support**: Cross-origin resource sharing enabled
- **Error Handling**: Comprehensive error handling and logging

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database with Motor for async operations
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running the application

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your configuration:
   ```
   MONGO_DETAILS=mongodb://localhost:27017
   SECRET_KEY=your-secret-key-here
   ```
5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication (`/auth`)

#### POST `/auth/register`
Register a new user
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

#### POST `/auth/login`
Login user
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

#### GET `/auth/profile`
Get current user profile (requires authentication)

#### PUT `/auth/profile`
Update user profile (requires authentication)
```json
{
  "username": "new_username",
  "full_name": "New Full Name",
  "phone": "+1234567890",
  "profile_picture": "https://example.com/picture.jpg"
}
```

#### POST `/auth/change-password`
Change user password (requires authentication)
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

#### GET `/auth/verify-token`
Verify JWT token (requires authentication)

### Trips (`/trips`)

#### POST `/trips/`
Create a new trip (requires authentication)
```json
{
  "title": "Adventure in Paris",
  "destination": "Paris, France",
  "duration_days": 7,
  "price": 1500.0,
  "description": "Explore the beautiful city of Paris",
  "max_participants": 10,
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-06-08T00:00:00Z",
  "category": "Cultural",
  "difficulty_level": "Easy",
  "image_url": "https://example.com/paris.jpg",
  "itinerary": [
    {
      "day": 1,
      "description": "Visit Eiffel Tower",
      "location": "Eiffel Tower",
      "time": "09:00",
      "cost": 25.0
    }
  ]
}
```

#### GET `/trips/`
Get all trips with pagination
- Query parameters: `limit` (default: 50), `skip` (default: 0)

#### GET `/trips/search`
Search trips with filters
- Query parameters:
  - `destination`: Search by destination
  - `category`: Filter by category
  - `min_price`, `max_price`: Price range
  - `min_duration`, `max_duration`: Duration range
  - `difficulty_level`: Filter by difficulty
  - `limit`, `skip`: Pagination

#### GET `/trips/my-trips`
Get user's trips (requires authentication)
- Query parameters: `trip_type` (all/hosted/joined)

#### GET `/trips/{trip_id}`
Get specific trip by ID

#### PUT `/trips/{trip_id}`
Update trip (requires authentication, host only)

#### DELETE `/trips/{trip_id}`
Delete trip (requires authentication, host only)

#### POST `/trips/{trip_id}/join`
Join a trip (requires authentication)

#### POST `/trips/{trip_id}/leave`
Leave a trip (requires authentication)

#### GET `/trips/categories`
Get all available trip categories

#### GET `/trips/difficulty-levels`
Get all available difficulty levels

### General

#### GET `/`
Welcome message

#### GET `/health`
Health check endpoint

## Data Models

### User
- `id`: Unique identifier
- `username`: Username (unique)
- `email`: Email address (unique)
- `full_name`: Full name
- `phone`: Phone number
- `profile_picture`: Profile picture URL
- `created_at`: Account creation timestamp
- `is_active`: Account status

### Trip
- `id`: Unique identifier
- `title`: Trip title
- `destination`: Trip destination
- `duration_days`: Trip duration in days
- `price`: Trip price
- `description`: Trip description
- `max_participants`: Maximum number of participants
- `start_date`, `end_date`: Trip dates
- `category`: Trip category
- `difficulty_level`: Difficulty level
- `image_url`: Trip image URL
- `host_id`: Trip host user ID
- `joined_users`: List of joined user IDs
- `itinerary`: List of itinerary items
- `status`: Trip status (upcoming/ongoing/completed/cancelled)
- `created_at`: Creation timestamp

### Itinerary Item
- `day`: Day number
- `description`: Activity description
- `location`: Activity location
- `time`: Activity time
- `cost`: Activity cost

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## CORS

CORS is enabled for all origins. In production, configure specific origins in `main.py`.

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file with:

```
MONGO_DETAILS=mongodb://localhost:27017
SECRET_KEY=your-secret-key-here
```

## Database Setup

The application uses MongoDB. Make sure MongoDB is running and accessible at the configured connection string.

Collections:
- `users`: User accounts and profiles
- `trips`: Trip information and details 