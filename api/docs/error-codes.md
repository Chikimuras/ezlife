# Error Codes Reference

This document provides a comprehensive reference for all error codes used in the Mon Vrai Projet API, following [RFC 7807](https://tools.ietf.org/html/rfc7807) Problem Details for HTTP APIs.

## Error Response Format

All error responses follow this standardized JSON structure:

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error summary",
  "detail": "Detailed explanation of what went wrong (optional)",
  "field": "specific_field (for single-field validation errors)",
  "errors": [
    {
      "field": "field_name",
      "message": "Field-specific error message"
    }
  ],
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/resource"
}
```

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | ✓ | Machine-readable error code (e.g., `AUTH_001`) |
| `message` | string | ✓ | Human-readable error summary |
| `detail` | string | | Detailed explanation of the error |
| `field` | string | | Specific field for single-field validation errors |
| `errors` | array | | List of field errors for multi-field validation |
| `timestamp` | string | ✓ | ISO 8601 timestamp when error occurred |
| `path` | string | ✓ | Request path that triggered the error |
| `retry_after` | integer | | Seconds to wait before retry (for rate limiting) |

---

## Error Code Categories

### Authentication Errors (401)

Errors related to user authentication and token validation.

#### AUTH_001 - Invalid Token

**HTTP Status:** 401 Unauthorized

**Description:** The provided authentication token is missing, malformed, or invalid.

**Example:**
```json
{
  "code": "AUTH_001",
  "message": "Could not validate credentials",
  "detail": "Invalid authentication token",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities"
}
```

**Common Causes:**
- Token is missing from the Authorization header
- Token is malformed or corrupted
- Token signature verification failed
- Token issuer does not match expected value

**Resolution:**
- Ensure the Authorization header is present: `Authorization: Bearer <token>`
- Verify the token is correctly formatted
- Re-authenticate to obtain a new token

---

#### AUTH_002 - Token Expired

**HTTP Status:** 401 Unauthorized

**Description:** The authentication token has expired and is no longer valid.

**Example:**
```json
{
  "code": "AUTH_002",
  "message": "Session expired",
  "detail": "Your authentication token has expired. Please log in again.",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities"
}
```

**Common Causes:**
- Access token exceeded its expiration time (default: 30 minutes)
- Refresh token exceeded its expiration time (default: 7 days)

**Resolution:**
- Use the `/api/v1/auth/refresh` endpoint to obtain a new access token
- If refresh token is also expired, re-authenticate via `/api/v1/login/google`

---

#### AUTH_003 - Invalid Credentials

**HTTP Status:** 401 Unauthorized

**Description:** The provided credentials are incorrect or do not match any user.

**Example:**
```json
{
  "code": "AUTH_003",
  "message": "Invalid credentials",
  "detail": "The provided username or password is incorrect.",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/login/google"
}
```

**Common Causes:**
- Invalid Google OAuth token
- Google Client ID mismatch
- Email not found in Google token payload

**Resolution:**
- Verify the Google OAuth token is valid and not expired
- Ensure the Google Client ID matches the configured value
- Re-authenticate through the Google OAuth flow

---

### Authorization Errors (403)

Errors related to user permissions and access control.

#### AUTH_004 - Insufficient Permissions

**HTTP Status:** 403 Forbidden

**Description:** The authenticated user does not have sufficient permissions to perform this action.

**Example:**
```json
{
  "code": "AUTH_004",
  "message": "Insufficient permissions",
  "detail": "You do not have permission to perform this action.",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/admin/users"
}
```

**Common Causes:**
- User attempting to access admin-only endpoints
- User trying to modify resources owned by another user
- User account is not active or has been suspended

**Resolution:**
- Contact an administrator to request necessary permissions
- Verify you are accessing resources you own
- Ensure your account is active

---

### Resource Errors (404)

Errors when requested resources cannot be found.

#### RESOURCE_001 - Resource Not Found

**HTTP Status:** 404 Not Found

**Description:** The requested resource does not exist or could not be found.

**Example:**
```json
{
  "code": "RESOURCE_001",
  "message": "Activity not found",
  "detail": "No activity exists with ID 'abc123'",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities/abc123"
}
```

**Resource Types:**
- `activity` - Activity records
- `category` - Activity categories
- `group` - Activity groups
- `user` - User accounts

**Common Causes:**
- Resource ID does not exist in the database
- Resource was deleted
- User does not have access to the resource (returns 404 instead of 403 for security)

**Resolution:**
- Verify the resource ID is correct
- Check if the resource was recently deleted
- Ensure you have access to the resource

---

### Validation Errors (422)

Errors related to invalid input data.

#### VALIDATION_001 - Required Field Missing

**HTTP Status:** 422 Unprocessable Entity

**Description:** One or more required fields are missing from the request.

**Example:**
```json
{
  "code": "VALIDATION_001",
  "message": "Validation failed",
  "errors": [
    {
      "field": "name",
      "message": "Field required"
    },
    {
      "field": "date",
      "message": "Field required"
    }
  ],
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities"
}
```

**Common Causes:**
- Missing required fields in request body
- Empty request body when data is expected
- Null values provided for required fields

**Resolution:**
- Include all required fields in the request
- Refer to the API schema for required fields
- Ensure field values are not null

---

#### VALIDATION_002 - Invalid Format

**HTTP Status:** 422 Unprocessable Entity

**Description:** The provided data is in an invalid format or does not meet validation constraints.

**Example:**
```json
{
  "code": "VALIDATION_002",
  "message": "Invalid format",
  "detail": "Email address is not valid",
  "field": "email",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/users"
}
```

**Common Format Errors:**
- Invalid email format
- Invalid date/time format (must be ISO 8601)
- Invalid UUID format
- String length constraints violated
- Numeric values out of range

**Resolution:**
- Verify data matches expected format
- Check field length constraints
- Use proper date/time format: `YYYY-MM-DD` for dates
- Ensure UUIDs are properly formatted

---

### Conflict Errors (409)

Errors when the request conflicts with the current state of the server.

#### CONFLICT_001 - Duplicate Resource

**HTTP Status:** 409 Conflict

**Description:** The resource already exists and cannot be created again.

**Example:**
```json
{
  "code": "CONFLICT_001",
  "message": "Duplicate resource",
  "detail": "A resource with these attributes already exists",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/categories"
}
```

**Common Causes:**
- Attempting to create a resource with a unique constraint violation
- Database integrity constraint (UNIQUE, PRIMARY KEY)
- Duplicate email, name, or other unique identifiers

**Resolution:**
- Use a different unique identifier
- Update the existing resource instead of creating a new one
- Check if the resource already exists before creating

---

#### CONFLICT_002 - Time Overlap

**HTTP Status:** 409 Conflict

**Description:** The specified time period overlaps with an existing activity.

**Example:**
```json
{
  "code": "CONFLICT_002",
  "message": "Time overlap detected",
  "detail": "The specified time period overlaps with an existing activity.",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities"
}
```

**Common Causes:**
- Creating activity with time range that overlaps another activity
- Updating activity time to overlap with existing activity

**Resolution:**
- Choose a different time range
- Delete or modify the conflicting activity
- Verify the start and end times are correct

---

#### CONFLICT_003 - State Conflict

**HTTP Status:** 409 Conflict

**Description:** The operation conflicts with the current state of the resource.

**Example:**
```json
{
  "code": "CONFLICT_003",
  "message": "State conflict",
  "detail": "Cannot perform this action in the current state",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities/abc123/complete"
}
```

**Common Causes:**
- Attempting to complete an already completed activity
- Modifying a locked or archived resource
- State transition not allowed

**Resolution:**
- Check the current state of the resource
- Ensure the operation is valid for the current state
- Follow the allowed state transition flow

---

#### CONFLICT_004 - Dependency Conflict

**HTTP Status:** 409 Conflict

**Description:** Cannot delete or modify the resource because it has dependencies.

**Example:**
```json
{
  "code": "CONFLICT_004",
  "message": "Cannot delete group",
  "detail": "Cannot delete group because it has associated categories",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/groups/abc123"
}
```

**Common Causes:**
- Deleting a group that has categories
- Deleting a category that has activities
- Foreign key constraint violation

**Resolution:**
- Delete dependent resources first
- Use cascade delete if supported
- Archive instead of delete

---

### Client Errors (400)

General client-side errors.

#### CLIENT_001 - Bad Request

**HTTP Status:** 400 Bad Request

**Description:** The request is malformed or contains invalid data.

**Example:**
```json
{
  "code": "CLIENT_001",
  "message": "Bad request",
  "detail": "Refresh token missing",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/auth/refresh"
}
```

**Common Causes:**
- Malformed JSON in request body
- Invalid query parameters
- Missing required headers
- Invalid Content-Type

**Resolution:**
- Verify JSON syntax is correct
- Check all required parameters are provided
- Ensure Content-Type header is set to `application/json`
- Review API documentation for correct request format

---

### Server Errors (500)

Internal server errors.

#### SERVER_001 - Internal Server Error

**HTTP Status:** 500 Internal Server Error

**Description:** An unexpected error occurred on the server.

**Example:**
```json
{
  "code": "SERVER_001",
  "message": "Internal server error",
  "detail": "An unexpected error occurred. Please try again later.",
  "timestamp": "2026-01-25T15:30:00.000000Z",
  "path": "/api/v1/activities"
}
```

**Common Causes:**
- Database connection error
- Unhandled exception in application code
- External service unavailable
- Configuration error

**Resolution:**
- Retry the request after a short delay
- Check system status page
- Contact support if the error persists
- Check logs for detailed error information

---

## Error Handling Best Practices

### For API Consumers

1. **Always check the `code` field** - Use machine-readable error codes, not HTTP status codes alone
2. **Display `message` to users** - Human-readable summary suitable for UI display
3. **Show `detail` for debugging** - Additional context for developers
4. **Handle `errors` array** - Display field-specific validation errors next to form fields
5. **Implement retry logic** - For 500-level errors and rate limiting (when `retry_after` is present)
6. **Log full error response** - Include timestamp and path for debugging

### For API Developers

1. **Use appropriate exception classes** - Choose the correct exception type for the error condition
2. **Provide meaningful details** - Include context that helps users understand and fix the issue
3. **Don't expose internals** - Never include stack traces or internal error messages in production
4. **Log with context** - Include error codes, request paths, and user context in logs
5. **Monitor error rates** - Track error codes to identify systemic issues

---

## Frontend Integration

The frontend error parser expects this format and automatically extracts:

- **Toast notifications**: Uses `message` for the toast title
- **Error details**: Shows `detail` in the toast description
- **Form validation**: Maps `errors` array to form fields
- **User guidance**: Displays actionable error messages based on error codes

Example frontend usage:

```typescript
try {
  const response = await api.createActivity(data);
} catch (error) {
  // Error parser automatically handles RFC 7807 format
  if (error.code === 'VALIDATION_001') {
    // Display field errors in form
    error.errors.forEach(fieldError => {
      form.setError(fieldError.field, fieldError.message);
    });
  } else if (error.code === 'AUTH_002') {
    // Token expired - redirect to login
    router.push('/login');
  } else {
    // Show generic error toast
    toast.error(error.message, { description: error.detail });
  }
}
```

---

## Monitoring and Alerting

All errors are logged with structured data for monitoring:

```json
{
  "error_code": "AUTH_001",
  "status_code": 401,
  "path": "/api/v1/activities",
  "method": "GET",
  "client_ip": "192.168.1.1",
  "timestamp": "2026-01-25T15:30:00.000000Z"
}
```

**Recommended Alerts:**

- `SERVER_001` rate > 1% of requests → Critical alert
- `AUTH_001` spike → Potential security issue
- `VALIDATION_001` rate > 10% → API usability issue
- `CONFLICT_004` frequent → Data model issue

---

## References

- [RFC 7807: Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
- [REST API Error Handling Best Practices](https://www.rfc-editor.org/rfc/rfc7807)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

**Last Updated:** January 25, 2026  
**Version:** 1.0.0
