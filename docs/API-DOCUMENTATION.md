# User API Documentation

**Base URL:** `/api/users`

**Authentication:** Required (Bearer Token)

---

## Overview

The User API provides CRUD operations for managing user accounts in the Smart Housing system. This includes creating, reading, updating, and deleting user records with support for additional profile information.

---

## Architecture

The User API follows the layered architecture pattern:

```
Route → Controller → Mediator → Service → Repository → Database
```

- **Route:** `app/edge/http/routes/users_route.py`
- **Controller:** `app/edge/http/controller/user_controller.py`
- **Mediator:** `app/mediator/user_mediator.py`
- **Service:** `app/services/user_service.py`
- **Repository:** `app/repositories/user_repository.py`
- **Model:** `app/models/user_model.py`
- **Schemas:** `app/schemas/user_schema.py`

---

## Data Model

### User Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| username | string | Yes | Unique username (max 50 chars) |
| email | string | Yes | Unique email address |
| hashed_password | string | Yes | Bcrypt hashed password |
| role | enum | Yes | User role (admin, user, guest) |
| phone_number | string | No | Phone number (max 20 chars) |
| age | integer | No | User age |
| gender | enum | No | Gender (male, female, other, prefer_not_to_say) |
| address | string | No | Street address (max 255 chars) |
| city | string | No | City name (max 100 chars) |
| country | string | No | Country name (max 100 chars) |
| zip_code | string | No | Postal code (max 20 chars) |
| is_active | boolean | Yes | Account status (default: true) |
| created_at | datetime | Auto | Creation timestamp |
| updated_at | datetime | Auto | Last update timestamp |

### Role Enum Values

- `admin` - Full system access
- `user` - Standard user access
- `guest` - Limited access

### Gender Enum Values

- `male`
- `female`
- `other`
- `prefer_not_to_say`

---

## API Endpoints

### 1. List Users

**Endpoint:** `GET /api/users`

**Description:** Retrieve a paginated list of users.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| offset | integer | No | 0 | Number of records to skip |
| limit | integer | No | 10 | Number of records to return (max 100) |

**Response:** `200 OK`

```json
{
  "total": 150,
  "rows": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "user",
      "is_active": true,
      "phone_number": "+1234567890",
      "age": 30,
      "gender": "male",
      "address": "123 Main St",
      "city": "New York",
      "country": "USA",
      "zip_code": "10001",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    }
  ],
  "offset": 0,
  "limit": 10
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/users?offset=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 2. Get User by ID

**Endpoint:** `GET /api/users/{user_id}`

**Description:** Retrieve a specific user by their ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User UUID |

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "phone_number": "+1234567890",
  "age": 30,
  "gender": "male",
  "address": "123 Main St",
  "city": "New York",
  "country": "USA",
  "zip_code": "10001",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

**Error Responses:**

- `400 Bad Request` - Invalid user ID format
- `404 Not Found` - User not found

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3. Create User

**Endpoint:** `POST /api/users`

**Description:** Create a new user account.

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "phone_number": "+1234567890",
  "age": 30,
  "gender": "male",
  "address": "123 Main St",
  "city": "New York",
  "country": "USA",
  "zip_code": "10001"
}
```

**Required Fields:** `username`, `email`, `password`

**Optional Fields:** `phone_number`, `age`, `gender`, `address`, `city`, `country`, `zip_code`

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "phone_number": "+1234567890",
  "age": 30,
  "gender": "male",
  "address": "123 Main St",
  "city": "New York",
  "country": "USA",
  "zip_code": "10001",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses:**

- `400 Bad Request` - Username or email already exists
- `400 Bad Request` - Invalid input data

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "phone_number": "+1234567890",
    "age": 30,
    "gender": "male",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "zip_code": "10001"
  }'
```

---

### 4. Update User

**Endpoint:** `PUT /api/users/{user_id}`

**Description:** Update an existing user's information.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User UUID |

**Request Body:** (All fields optional)

```json
{
  "username": "john_doe_updated",
  "email": "john.updated@example.com",
  "password": "NewSecurePassword123!",
  "phone_number": "+9876543210",
  "age": 31,
  "gender": "male",
  "address": "456 Oak Ave",
  "city": "Los Angeles",
  "country": "USA",
  "zip_code": "90001",
  "is_active": true,
  "role": "admin"
}
```

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe_updated",
  "email": "john.updated@example.com",
  "role": "admin",
  "is_active": true,
  "phone_number": "+9876543210",
  "age": 31,
  "gender": "male",
  "address": "456 Oak Ave",
  "city": "Los Angeles",
  "country": "USA",
  "zip_code": "90001",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-25T09:15:00Z"
}
```

**Error Responses:**

- `400 Bad Request` - Invalid user ID format
- `404 Not Found` - User not found
- `400 Bad Request` - Username or email already exists

**Example Request:**

```bash
curl -X PUT "http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+9876543210",
    "age": 31,
    "city": "Los Angeles"
  }'
```

---

### 5. Delete User

**Endpoint:** `DELETE /api/users/{user_id}`

**Description:** Delete a user account.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User UUID |

**Response:** `200 OK`

```json
{
  "message": "User deleted successfully"
}
```

**Error Responses:**

- `400 Bad Request` - Invalid user ID format
- `404 Not Found` - User not found
- `500 Internal Server Error` - Failed to delete user

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/users/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input or duplicate data
- `401 Unauthorized` - Missing or invalid authentication
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Authentication

All endpoints require authentication using Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Tokens are obtained through the authentication endpoints in `/api/auth`.

---

## Validation Rules

### Username
- Must be unique
- Maximum 50 characters
- Cannot be empty

### Email
- Must be unique
- Must be valid email format
- Maximum 255 characters

### Password
- Minimum length enforced by security utility
- Hashed using bcrypt before storage

### Phone Number
- Optional
- Maximum 20 characters
- Can include country code prefix

### Age
- Optional
- Must be a positive integer

### Address Fields
- Address: Maximum 255 characters
- City: Maximum 100 characters
- Country: Maximum 100 characters
- Zip Code: Maximum 20 characters

---

## Business Logic

### User Creation
- Checks for duplicate username
- Checks for duplicate email
- Hashes password using bcrypt
- Sets default role to `user`
- Sets default `is_active` to `true`
- Records Prometheus metric for user creation

### User Update
- Validates user existsbefore update
- Hashes new password if provided
- Only updates fields that are provided
- Records Prometheus metric for user update

### User Deletion
- Validates user exists before deletion
- Records Prometheus metric for user deletion
- Soft delete or hard delete based on requirements

### User Listing
- Supports pagination with offset/limit
- Returns total count for pagination controls
- Maximum limit of 100 records per request

---

## Security Considerations

1. **Password Security**
   - Passwords are never returned in API responses
   - Passwords are hashed using bcrypt
   - Password hashing uses security_util from utils

2. **Authorization**
   - All endpoints require valid authentication
   - Role-based access control should be implemented at middleware level
   - Admin users may have additional permissions

3. **Data Validation**
   - All inputs validated using Pydantic schemas
   - SQL injection prevention through SQLAlchemy ORM
   - XSS prevention through proper response serialization

4. **Rate Limiting**
   - Consider implementing rate limiting for user creation
   - Prevent brute force attacks on login endpoints

---

## Database Schema

The User model is stored in the `users` table with the following columns:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    phone_number VARCHAR(20),
    age INTEGER,
    gender VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    zip_code VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

---

## Migration

To apply the new fields to your database, create and run an Alembic migration:

```bash
alembic revision --autogenerate -m "add user profile fields"
alembic upgrade head
```

---

## Testing

### Example Test Cases

1. **Create User**
   - Valid user creation
   - Duplicate username rejection
   - Duplicate email rejection
   - Invalid email format rejection

2. **Get User**
   - Valid user retrieval
   - Non-existent user returns 404
   - Invalid UUID format returns 400

3. **Update User**
   - Valid partial update
   - Valid full update
   - Password update hashes correctly
   - Non-existent user returns 404

4. **Delete User**
   - Valid deletion
   - Non-existent user returns 404
   - Deleted user cannot be retrieved

5. **List Users**
   - Pagination works correctly
   - Offset/limit validation
   - Empty list returns correctly

---

## Future Enhancements

Potential improvements to consider:

1. **Search and Filtering**
   - Add search by username/email
   - Filter by role, is_active status
   - Filter by location (city, country)

2. **Bulk Operations**
   - Bulk user creation
   - Bulk user update
   - Bulk user deletion

3. **User Profile**
   - Profile image upload
   - Profile preferences
   - User settings

4. **Audit Trail**
   - Track who created/updated users
   - Log all user changes
   - Soft delete with restore capability

5. **Advanced Validation**
   - Phone number format validation
   - Age range validation
   - Address validation

---

## Related Documentation

- [Routes Implementation Plan](./routes-implementation-plan.md)
- [Schemas Implementation Plan](./schemas-implementation-plan.md)
- [Models Implementation Plan](./models-implementation-plan.md)
- [Backend Implementation Plan](./backend-implementation-plan.md)

---

**Last Updated:** June 28, 2026
