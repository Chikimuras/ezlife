"""Custom exception classes for RFC 7807 compliant error handling.

All custom exceptions inherit from AppException which extends FastAPI's HTTPException
to include structured error fields (code, message, detail, field, errors).
"""

from fastapi import HTTPException

from app.schemas.error import ErrorDetail


class AppException(HTTPException):
    """Base exception for all application errors with RFC 7807 fields.

    Args:
        status_code: HTTP status code
        code: Machine-readable error code (e.g., "AUTH_001")
        message: Human-readable error summary
        detail: Detailed explanation (optional)
        field: Specific field for single-field errors (optional)
        errors: List of field errors for multi-field validation (optional)
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        detail: str | None = None,
        field: str | None = None,
        errors: list[ErrorDetail] | None = None,
    ):
        super().__init__(status_code=status_code)
        self.code = code
        self.message = message
        self.detail = detail
        self.field = field
        self.errors = errors


# ============================================================================
# Authentication Errors (401)
# ============================================================================


class AuthenticationError(AppException):
    """401 - Authentication failed."""

    def __init__(
        self,
        code: str = "AUTH_001",
        message: str = "Authentication failed",
        detail: str | None = None,
    ):
        super().__init__(
            status_code=401,
            code=code,
            message=message,
            detail=detail,
        )


class TokenExpiredError(AuthenticationError):
    """401 - AUTH_002 - Token expired."""

    def __init__(self, detail: str | None = None):
        super().__init__(
            code="AUTH_002",
            message="Session expired",
            detail=detail
            or "Your authentication token has expired. Please log in again.",
        )


class InvalidCredentialsError(AuthenticationError):
    """401 - AUTH_003 - Invalid username/password."""

    def __init__(self, detail: str | None = None):
        super().__init__(
            code="AUTH_003",
            message="Invalid credentials",
            detail=detail or "The provided username or password is incorrect.",
        )


# ============================================================================
# Authorization Errors (403)
# ============================================================================


class AuthorizationError(AppException):
    """403 - Insufficient permissions."""

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=403,
            code="AUTH_004",
            message="Insufficient permissions",
            detail=detail or "You do not have permission to perform this action.",
        )


# ============================================================================
# Resource Errors (404)
# ============================================================================


class NotFoundError(AppException):
    """404 - RESOURCE_001 - Resource not found."""

    def __init__(
        self,
        resource: str | None = None,
        resource_id: str | None = None,
        detail: str | None = None,
    ):
        if detail is None and resource:
            if resource_id:
                detail = f"No {resource} exists with ID '{resource_id}'"
            else:
                detail = f"{resource.capitalize()} not found"

        message = (
            f"{resource.capitalize()} not found" if resource else "Resource not found"
        )

        super().__init__(
            status_code=404,
            code="RESOURCE_001",
            message=message,
            detail=detail,
        )


# ============================================================================
# Validation Errors (422)
# ============================================================================


class AppValidationError(AppException):
    """422 - VALIDATION_001/002 - Validation failed.

    Note: Named AppValidationError to avoid conflict with Pydantic's ValidationError.
    """

    def __init__(
        self,
        code: str = "VALIDATION_001",
        message: str = "Validation failed",
        detail: str | None = None,
        field: str | None = None,
        errors: list[ErrorDetail] | None = None,
    ):
        super().__init__(
            status_code=422,
            code=code,
            message=message,
            detail=detail,
            field=field,
            errors=errors,
        )


class RequiredFieldError(AppValidationError):
    """422 - VALIDATION_001 - Required field missing."""

    def __init__(self, field: str, detail: str | None = None):
        super().__init__(
            code="VALIDATION_001",
            message="Required field missing",
            detail=detail or f"Field '{field}' is required",
            field=field,
        )


class InvalidFormatError(AppValidationError):
    """422 - VALIDATION_002 - Invalid field format."""

    def __init__(self, field: str, detail: str | None = None):
        super().__init__(
            code="VALIDATION_002",
            message="Invalid format",
            detail=detail,
            field=field,
        )


# ============================================================================
# Conflict Errors (409)
# ============================================================================


class ConflictError(AppException):
    """409 - CONFLICT_001/002/003/004 - Business logic conflict."""

    def __init__(
        self,
        code: str = "CONFLICT_001",
        message: str = "Conflict occurred",
        detail: str | None = None,
    ):
        super().__init__(
            status_code=409,
            code=code,
            message=message,
            detail=detail,
        )


class DuplicateResourceError(ConflictError):
    """409 - CONFLICT_001 - Resource already exists."""

    def __init__(self, resource: str | None = None, detail: str | None = None):
        message = f"Duplicate {resource}" if resource else "Resource already exists"
        if detail is None and resource:
            detail = f"A {resource} with these attributes already exists"

        super().__init__(
            code="CONFLICT_001",
            message=message,
            detail=detail,
        )


class TimeOverlapError(ConflictError):
    """409 - CONFLICT_002 - Time period overlaps with existing activity."""

    def __init__(self, detail: str | None = None):
        super().__init__(
            code="CONFLICT_002",
            message="Time overlap detected",
            detail=detail
            or "The specified time period overlaps with an existing activity.",
        )


class DependencyConflictError(ConflictError):
    """409 - CONFLICT_004 - Cannot delete/modify due to dependencies."""

    def __init__(self, resource: str | None = None, detail: str | None = None):
        message = f"Cannot modify {resource}" if resource else "Dependency conflict"
        if detail is None and resource:
            detail = f"Cannot delete {resource} because it has associated dependencies"

        super().__init__(
            code="CONFLICT_004",
            message=message,
            detail=detail,
        )


# ============================================================================
# Client Errors (400)
# ============================================================================


class BadRequestError(AppException):
    """400 - CLIENT_001 - Malformed request."""

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=400,
            code="CLIENT_001",
            message="Bad request",
            detail=detail or "The request is malformed or contains invalid data.",
        )


# ============================================================================
# Server Errors (500)
# ============================================================================


class InternalServerError(AppException):
    """500 - SERVER_001 - Internal server error."""

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=500,
            code="SERVER_001",
            message="Internal server error",
            detail=detail or "An unexpected error occurred. Please try again later.",
        )
