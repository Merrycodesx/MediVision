# MediVision Backend API Documentation

This document describes the REST API endpoints for the MediVision backend, built with Django REST Framework.

## Base URL
`http://127.0.0.1:8000/api/` (local development)

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the access token in the `Authorization` header as `Bearer <token>`.

## Endpoints

### Authentication

#### POST /auth/register/
Register a new user account.

**Permissions:** AllowAny

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

#### POST /auth/token/
Obtain JWT token pair for authentication.

**Permissions:** AllowAny

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /auth/token/refresh/
Refresh the access token using the refresh token.

**Permissions:** AllowAny

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Patients

#### GET /patients/
List all patients accessible to the authenticated user.

**Permissions:** IsAuthenticated, PatientPermission

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "age": 30,
    "clinician_id": 1
  }
]
```

#### POST /patients/
Create a new patient record.

**Permissions:** IsAuthenticated, PatientPermission

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "string",
  "age": 0
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "string",
  "age": 0,
  "clinician_id": 1
}
```

#### GET /patients/{id}/
Retrieve details of a specific patient.

**Permissions:** IsAuthenticated, PatientPermission

**Parameters:**
- `id` (integer): Patient ID

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30,
  "clinician_id": 1
}
```

#### PUT /patients/{id}/
Update a patient's information.

**Permissions:** IsAuthenticated, PatientPermission

**Parameters:**
- `id` (integer): Patient ID

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Jane Doe",
  "age": 31
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "age": 31,
  "clinician_id": 1
}
```

#### DELETE /patients/{id}/
Delete a patient record.

**Permissions:** IsAuthenticated, PatientPermission

**Parameters:**
- `id` (integer): Patient ID

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**

### Test

#### GET /test/
A simple test endpoint to verify API connectivity.

**Permissions:** None

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Welcome to the TEST api?"
}
```

## Error Responses
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Notes
- All requests should include `Content-Type: application/json` for POST/PUT requests.
- Use HTTPS in production.
- For CXR image handling APIs, refer to future updates as they are not yet implemented in this version.