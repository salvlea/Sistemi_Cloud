# Smart ATS API Specifications

## Overview

The Smart ATS API provides RESTful endpoints for managing the applicant tracking system. All endpoints (except `/health`) require authentication via AWS Cognito.

## Base URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/{environment}
```

Example: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev`

## Authentication

All authenticated endpoints require a valid JWT token from AWS Cognito in the `Authorization` header:

```http
Authorization: Bearer <ID_TOKEN>
```

### Getting a Token

Use AWS Cognito `USER_PASSWORD_AUTH` flow to obtain tokens.

**Example (AWS CLI)**:
```bash
aws cognito-idp initiate-auth \
  --client-id <CLIENT_ID> \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=<email>,PASSWORD=<password>
```

Returns:
```json
{
  "AuthenticationResult": {
    "AccessToken": "...",
    "IdToken": "...",
    "RefreshToken": "..."
  }
}
```

Use the `IdToken` for API requests.

## Endpoints

### Health Check

Check if the API is operational (no authentication required).

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "smart-ats-api"
}
```

**Status Codes**:
- `200 OK`: Service is healthy

---

### Upload CV (Future Enhancement)

This endpoint would be implemented to trigger CV processing via API instead of direct S3 upload.

**Endpoint**: `POST /candidates/upload`

**Headers**:
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Body**:
```
cv_file: <binary file data>
job_position: string
```

**Response**:
```json
{
  "candidate_id": "abc123",
  "s3_key": "cvs/20260115_123045_resume.pdf",
  "status": "processing",
  "message": "CV uploaded successfully"
}
```

**Status Codes**:
- `201 Created`: CV uploaded successfully
- `400 Bad Request`: Invalid file or parameters
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Server error

---

### List Candidates (Future Enhancement)

Retrieve list of candidates with rankings.

**Endpoint**: `GET /candidates`

**Headers**:
- `Authorization: Bearer <token>`

**Query Parameters**:
- `job_position` (optional): Filter by job position
- `limit` (optional): Max results (default: 50)
- `sort_order` (optional): `asc` or `desc` (default: `desc`)

**Response**:
```json
{
  "candidates": [
    {
      "candidate_id": "alice_2026010001",
      "candidate_name": "Alice Johnson",
      "email": "alice.j@email.com",
      "job_position": "Software Engineer",
      "ranking_score": 87.5,
      "skills_matched": "4/5",
      "experience_years": 5,
      "education": "Master's Degree",
      "status": "processed",
      "upload_date": "2026-01-13 10:30:00"
    }
  ],
  "count": 1,
  "next_token": null
}
```

---

### Get Candidate Details (Future Enhancement)

Get detailed information for a specific candidate.

**Endpoint**: `GET /candidates/{candidate_id}`

**Headers**:
- `Authorization: Bearer <token>`

**Response**:
```json
{
  "candidate_id": "alice_2026010001",
  "candidate_name": "Alice Johnson",
  "email": "alice.j@email.com",
  "phone": "+1-555-0101",
  "job_position": "Software Engineer",
  "ranking_score": 87.5,
  "skills_matched": "4/5",
  "experience_years": 5,
  "education": "Master's Degree",
  "skills": ["Python", "Java", "AWS", "Docker"],
  "s3_bucket": "smart-ats-cvs-dev-123456789",
  "s3_key": "cvs/alice_cv.pdf",
  "status": "processed",
  "upload_date": "2026-01-13 10:30:00",
  "uploaded_by": "admin@smartats.com"
}
```

**Status Codes**:
- `200 OK`: Success
- `404 Not Found`: Candidate not found
- `401 Unauthorized`: Missing or invalid token

---

### Download CV (Future Enhancement)

Generate a pre-signed URL to download the candidate's CV.

**Endpoint**: `GET /candidates/{candidate_id}/cv`

**Headers**:
- `Authorization: Bearer <token>`

**Response**:
```json
{
  "download_url": "https://s3.amazonaws.com/...",
  "expires_in": 3600
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes**:
- `UNAUTHORIZED`: Authentication failed
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid input
- `INTERNAL_ERROR`: Server error

## Rate Limiting

- **Authenticated endpoints**: 1000 requests/hour per user
- **Health check**: No limit

## Webhooks (Future Enhancement)

Smart ATS can send webhooks when processing is complete.

**Event Types**:
- `candidate.processed`: CV processing completed
- `candidate.failed`: CV processing failed

**Payload**:
```json
{
  "event": "candidate.processed",
  "timestamp": "2026-01-15T10:30:00Z",
  "data": {
    "candidate_id": "abc123",
    "candidate_name": "John Doe",
    "ranking_score": 85.5
  }
}
```

## SDK Examples

### Python

```python
import requests

API_URL = "https://abc123.execute-api.us-east-1.amazonaws.com/dev"
ID_TOKEN = "<your-cognito-id-token>"

headers = {
    "Authorization": f"Bearer {ID_TOKEN}"
}

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# List candidates (future)
# response = requests.get(f"{API_URL}/candidates", headers=headers)
# print(response.json())
```

### curl

```bash
# Health check
curl https://abc123.execute-api.us-east-1.amazonaws.com/dev/health

# List candidates (with auth)
curl -H "Authorization: Bearer <ID_TOKEN>" \
     https://abc123.execute-api.us-east-1.amazonaws.com/dev/candidates
```

## Versioning

Current version: **v1**

Future versions will be accessible via path prefix: `/v2/...`

## Support

For API issues, contact: salvatore.leanza@example.com
