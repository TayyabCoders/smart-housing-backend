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

---

# Voting System API Documentation

**Base URL:** `/api/v1/voting`

**Authentication:** Not Required (Public voting system)

---

## Overview

The Voting System API provides a complete election management solution for society committee elections. This includes candidate management, vote submission, live results tracking, activity logging, and election information.

---

## Architecture

The Voting System API follows the layered architecture pattern:

```
Route → Controller → Mediator → Service → Repository → Database
```

- **Route:** `app/edge/http/routes/voting_route.py`
- **Controller:** `app/edge/http/controller/voting_controller.py`
- **Mediator:** `app/mediator/voting_mediator.py`
- **Services:** 
  - `app/services/election_service.py`
  - `app/services/candidate_service.py`
  - `app/services/vote_service.py`
  - `app/services/activity_log_service.py`
- **Repositories:**
  - `app/repositories/election_repository.py`
  - `app/repositories/candidate_repository.py`
  - `app/repositories/vote_repository.py`
  - `app/repositories/activity_log_repository.py`
- **Models:**
  - `app/models/election.py`
  - `app/models/candidate.py`
  - `app/models/vote.py`
  - `app/models/activity_log.py`
- **Schemas:**
  - `app/schemas/election_schema.py`
  - `app/schemas/candidate_schema.py`
  - `app/schemas/vote_schema.py`
  - `app/schemas/activity_log_schema.py`

---

## Data Models

### Election Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| title | string | Yes | Election title |
| society_name | string | Yes | Society name |
| society_location | string | Yes | Society location |
| election_date | datetime | Yes | Election date |
| is_active | boolean | Yes | Election active status (default: true) |
| total_eligible_voters | integer | Yes | Total eligible voters (default: 0) |
| created_at | datetime | Auto | Creation timestamp |
| updated_at | datetime | Auto | Last update timestamp |

### Candidate Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| election_id | UUID | Yes | Reference to election |
| name | string | Yes | Candidate name |
| role | string | Yes | Candidate role (e.g., "Chairman Candidate") |
| party | string | Yes | Political party/group |
| p_class | string | Yes | CSS styling class |
| emoji | string | Yes | Emoji representation |
| created_at | datetime | Auto | Creation timestamp |

### Vote Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| candidate_id | UUID | Yes | Reference to candidate |
| voter_name | string | Yes | Voter's full name |
| voter_nic | string | Yes | Voter's CNIC (unique, format: XXXXX-XXXXXXX-X) |
| voter_block | string | No | Voter's block/flat |
| voter_phone | string | No | Voter's phone number |
| voted_at | datetime | Auto | Vote timestamp |
| is_verified | boolean | Yes | Vote verification status (default: true) |

### Activity Log Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| text | string | Yes | Activity description |
| timestamp | datetime | Auto | Activity timestamp |

---

## API Endpoints

### 1. Get Candidates

**Endpoint:** `GET /api/v1/voting/candidates`

**Description:** Retrieve all candidates for the active election.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "election_id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Muhammad Khalid Ansari",
      "role": "Chairman Candidate",
      "party": "Tehreek-e-Taraqqi",
      "p_class": "text-blue-500 bg-blue-500/15 border border-blue-500/20",
      "emoji": "👨‍💼",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

**Error Responses:**

- `404 Not Found` - No active election found

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/voting/candidates"
```

---

### 2. Submit Vote

**Endpoint:** `POST /api/v1/voting/vote`

**Description:** Submit a vote for a candidate.

**Request Body:**

```json
{
  "candidate_id": "550e8400-e29b-41d4-a716-446655440000",
  "voter_name": "Muhammad Ali Khan",
  "voter_nic": "42201-1234567-8",
  "voter_block": "Block C, Flat 401",
  "voter_phone": "03XX-XXXXXXX"
}
```

**Required Fields:** `candidate_id`, `voter_name`, `voter_nic`

**Optional Fields:** `voter_block`, `voter_phone`

**Response:** `200 OK` (Success)

```json
{
  "success": true,
  "message": "Vote successfully recorded",
  "data": {
    "vote_id": "770e8400-e29b-41d4-a716-446655440002",
    "candidate_name": "Muhammad Khalid Ansari",
    "voted_at": "2025-01-15T14:30:00Z"
  }
}
```

**Response:** `400 Bad Request` (Already Voted)

```json
{
  "success": false,
  "error": "ALREADY_VOTED",
  "message": "This CNIC has already been used to vote. Each voter can only vote once."
}
```

**Error Responses:**

- `400 Bad Request` - CNIC already voted
- `400 Bad Request` - No active election
- `404 Not Found` - Candidate not found
- `422 Unprocessable Entity` - Invalid CNIC format or name length

**Validation Rules:**

- CNIC must match format: `XXXXX-XXXXXXX-X`
- Voter name must be at least 3 characters

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/voting/vote" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "550e8400-e29b-41d4-a716-446655440000",
    "voter_name": "Muhammad Ali Khan",
    "voter_nic": "42201-1234567-8",
    "voter_block": "Block C, Flat 401",
    "voter_phone": "03XX-XXXXXXX"
  }'
```

---

### 3. Get Results

**Endpoint:** `GET /api/v1/voting/results`

**Description:** Get live election results with vote counts and percentages.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "total_votes": 150,
    "candidates": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Muhammad Khalid Ansari",
        "party": "Tehreek-e-Taraqqi",
        "emoji": "👨‍💼",
        "votes": 45,
        "percentage": 30,
        "rank": 1
      },
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Another Candidate",
        "party": "Another Party",
        "emoji": "👨‍💼",
        "votes": 35,
        "percentage": 23,
        "rank": 2
      }
    ]
  }
}
```

**Error Responses:**

- `404 Not Found` - No active election found

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/voting/results"
```

---

### 4. Get Activity Log

**Endpoint:** `GET /api/v1/voting/activity-log`

**Description:** Get recent voting activity log.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 15 | Number of records to return (1-50) |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "text": "Muhammad A*** ne Muhammad Khalid Ansari ko vote diya",
      "time": "14:30",
      "timestamp": "2025-01-15T14:30:00Z"
    },
    {
      "text": "Ahmed K*** ne Another Candidate ko vote diya",
      "time": "14:25",
      "timestamp": "2025-01-15T14:25:00Z"
    }
  ]
}
```

**Error Responses:**

- `400 Bad Request` - Invalid limit (must be 1-50)

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/voting/activity-log?limit=15"
```

---

### 5. Get Election Status

**Endpoint:** `GET /api/v1/voting/election/status`

**Description:** Get current election status with participation statistics.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "title": "Society Committee Election 2025",
    "society_name": "Green Valley Society",
    "society_location": "Gulshan-e-Iqbal, Karachi",
    "election_date": "2025-02-01T00:00:00Z",
    "is_active": true,
    "total_eligible_voters": 500,
    "total_votes_cast": 150,
    "participation_rate": 30.0
  }
}
```

**Error Responses:**

- `404 Not Found` - No active election found

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/voting/election/status"
```

---

### 6. Get Election Rules

**Endpoint:** `GET /api/v1/voting/election/rules`

**Description:** Get election rules and guidelines.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "title": "Election Guidelines",
    "rules": [
      {
        "icon": "🪪",
        "title": "CNIC Lazim Hai",
        "description": "Har voter ko apna valid Pakistani CNIC number dena hoga. Ek CNIC se sirf ek baar vote diya ja sakta hai."
      },
      {
        "icon": "👤",
        "title": "Naam Zaroori Hai",
        "description": "Voter ka poora naam dena lazim hai. Yeh record mein save hoga aur audit ke liye use hoga."
      },
      {
        "icon": "🏘️",
        "title": "Society Member",
        "description": "Sirf Green Valley Society ke registered residents vote de sakte hain. Bahar ke log eligible nahi hain."
      },
      {
        "icon": "🔒",
        "title": "Sirf Ek Vote",
        "description": "Ek voter sirf ek candidate ko vote de sakta hai. Dobara vote dene ki koshish system rokta hai."
      },
      {
        "icon": "📊",
        "title": "Shuafaf Nataij",
        "description": "Live Results tab mein har candidate ke votes real time mein dekhe ja sakte hain. Koi cheez chupayi nahi jati."
      },
      {
        "icon": "🏆",
        "title": "Jeet ka Faisla",
        "description": "Sab se zyada votes hasil karne wala candidate Green Valley Society Committee ka Chairman bane ga."
      }
    ]
  }
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/voting/election/rules"
```

---

### 7. Get Election Committee

**Endpoint:** `GET /api/v1/voting/election/committee`

**Description:** Get election committee members information.

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "title": "Election Committee Members",
    "members": [
      {
        "role": "Presiding Officer",
        "name": "Rao Tariq Mehmood",
        "icon": "🧑‍⚖️"
      },
      {
        "role": "Secretary",
        "name": "Mrs. Sana Javed",
        "icon": "📋"
      },
      {
        "role": "Observer",
        "name": "Haji Abdul Rehman",
        "icon": "🔍"
      },
      {
        "role": "System Admin",
        "name": "Usman Raza",
        "icon": "💻"
      }
    ]
  }
}
```

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/voting/election/committee"
```

---

## Business Logic

### Vote Submission
- Validates active election exists
- Checks if CNIC has already voted (duplicate prevention)
- Validates candidate exists
- Validates CNIC format (XXXXX-XXXXXXX-X)
- Validates voter name (minimum 3 characters)
- Creates vote record
- Automatically creates activity log entry
- Records Prometheus metric for vote submission

### Results Calculation
- Calculates total votes cast
- Calculates vote count per candidate
- Calculates percentage per candidate
- Ranks candidates by vote count (descending)
- Returns real-time results

### Activity Logging
- Automatically logs each vote with masked voter name
- Shows recent activity with time (HH:MM format)
- Supports pagination with limit parameter
- Maximum 50 records per request

### Election Status
- Retrieves active election information
- Calculates total votes cast
- Calculates participation rate percentage
- Returns comprehensive election statistics

---

## Security Considerations

1. **Vote Integrity**
   - CNIC uniqueness prevents duplicate voting
   - Database constraint on voter_nic field
   - Application-level validation before submission

2. **Data Privacy**
   - Voter names are masked in activity logs (first 3 chars + ***)
   - CNIC stored securely in database
   - Optional fields (block, phone) for additional verification

3. **Election Security**
   - Only active elections accept votes
   - Candidate validation before vote submission
   - Vote verification flag for audit purposes

4. **Rate Limiting**
   - Consider implementing rate limiting for vote submission
   - Prevent automated voting systems

---

## Database Schema

### Elections Table

```sql
CREATE TABLE elections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    society_name VARCHAR(255) NOT NULL,
    society_location VARCHAR(255) NOT NULL,
    election_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    total_eligible_voters INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Candidates Table

```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    election_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    party VARCHAR(255) NOT NULL,
    p_class VARCHAR(255) NOT NULL,
    emoji VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_candidates_election FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE
);
```

### Votes Table

```sql
CREATE TABLE votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    voter_name VARCHAR(255) NOT NULL,
    voter_nic VARCHAR(15) NOT NULL UNIQUE,
    voter_block VARCHAR(255),
    voter_phone VARCHAR(20),
    voted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_verified BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_votes_candidate FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE INDEX ix_votes_voter_nic ON votes(voter_nic);
```

### Activity Logs Table

```sql
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Migration

The voting system tables are created via Alembic migration:

```bash
alembic upgrade head
```

Migration file: `alembic/versions/voting_system_tables.py`

---

## Testing

### Example Test Cases

1. **Submit Vote**
   - Valid vote submission
   - Duplicate CNIC rejection
   - Invalid CNIC format rejection
   - Invalid name length rejection
   - Non-existent candidate rejection

2. **Get Candidates**
   - Valid candidate list retrieval
   - No active election returns 404

3. **Get Results**
   - Valid results calculation
   - Correct percentage calculation
   - Correct ranking by votes
   - No active election returns 404

4. **Activity Log**
   - Valid activity log retrieval
   - Correct name masking
   - Pagination with limit parameter
   - Invalid limit returns 400

5. **Election Status**
   - Valid status retrieval
   - Correct participation rate calculation
   - No active election returns 404

---

## Future Enhancements

Potential improvements to consider:

1. **Advanced Security**
   - CAPTCHA for vote submission
   - IP-based rate limiting
   - Device fingerprinting

2. **Enhanced Reporting**
   - Export results to PDF/Excel
   - Historical election data
   - Voter turnout analytics

3. **Real-time Updates**
   - WebSocket for live results
   - Push notifications for vote updates
   - Live dashboard

4. **Multi-Election Support**
   - Support for multiple simultaneous elections
   - Election categories (chairman, secretary, etc.)
   - Complex voting systems (preferential voting)

5. **Audit Trail**
   - Detailed vote audit logs
   - Admin override capabilities
   - Vote modification/deletion with reason

---

## Related Documentation

- [Routes Implementation Plan](./routes-implementation-plan.md)
- [Schemas Implementation Plan](./schemas-implementation-plan.md)
- [Models Implementation Plan](./models-implementation-plan.md)
- [Backend Implementation Plan](./backend-implementation-plan.md)

---

**Last Updated:** June 29, 2026
