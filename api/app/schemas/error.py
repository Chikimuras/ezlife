from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    field: str = Field(..., description="Field that caused the validation error")
    message: str = Field(..., description="Error message for the field")


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Machine-readable error code (e.g., AUTH_001)")
    message: str = Field(..., description="Human-readable error summary")
    detail: str | None = Field(
        default=None, description="Detailed explanation of what went wrong"
    )
    field: str | None = Field(
        default=None,
        description="Specific field that caused the error (for single field errors)",
    )
    errors: list[ErrorDetail] | None = Field(
        default=None,
        description="List of field errors (for multiple validation errors)",
    )
    timestamp: datetime = Field(
        ..., description="ISO 8601 timestamp when error occurred"
    )
    path: str = Field(..., description="Request path that triggered the error")
    retry_after: int | None = Field(
        default=None, description="Seconds to wait before retry (for rate limiting)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "code": "RESOURCE_001",
                    "message": "Activity not found",
                    "detail": "No activity exists with ID 'abc123'",
                    "timestamp": "2026-01-25T15:30:00Z",
                    "path": "/api/v1/activities/abc123",
                },
                {
                    "code": "VALIDATION_001",
                    "message": "Validation failed",
                    "errors": [
                        {"field": "name", "message": "Name is required"},
                        {
                            "field": "duration",
                            "message": "Duration must be positive",
                        },
                    ],
                    "timestamp": "2026-01-25T15:30:00Z",
                    "path": "/api/v1/activities",
                },
                {
                    "code": "AUTH_002",
                    "message": "Session expired",
                    "detail": (
                        "Your authentication token has expired. Please log in again."
                    ),
                    "timestamp": "2026-01-25T15:30:00Z",
                    "path": "/api/v1/activities",
                },
            ]
        }
    )
