import traceback
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.exceptions import AppException
from app.schemas.error import ErrorDetail, ErrorResponse


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.bind(
        error_code=exc.code,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "Unknown",
    ).warning(
        f"AppException raised\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Code: {exc.code}\n"
        f"  Status: {exc.status_code}\n"
        f"  Message: {exc.message}\n"
        f"  Detail: {exc.detail}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}"
    )

    error_response = ErrorResponse(
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
        field=exc.field,
        errors=exc.errors,
        timestamp=datetime.utcnow(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode="json", exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        f"HTTPException raised\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Status: {exc.status_code}\n"
        f"  Detail: {exc.detail}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    logger.bind(
        error_code="VALIDATION_001",
        status_code=422,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "Unknown",
        error_count=len(errors),
    ).error(
        f"Validation Error\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}\n"
        f"  Errors ({len(errors)}):"
    )

    for error in errors:
        loc = " -> ".join(str(x) for x in error["loc"])
        logger.error(
            f"    ❌ Field: {loc}\n"
            f"       Type: {error['type']}\n"
            f"       Message: {error['msg']}\n"
            f"       Input: {error.get('input', 'N/A')}"
        )

    simplified_errors = []
    for error in errors:
        loc = error.get("loc", ())
        field = loc[-1] if loc else "unknown"
        simplified_errors.append(
            ErrorDetail(field=str(field), message=error.get("msg", "Validation error"))
        )

    error_response = ErrorResponse(
        code="VALIDATION_001",
        message="Validation failed",
        errors=simplified_errors,
        timestamp=datetime.utcnow(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(mode="json", exclude_none=True),
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    errors = exc.errors()
    logger.error(
        f"Pydantic Validation Error\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}\n"
        f"  Errors ({len(errors)}):"
    )

    for error in errors:
        loc = " -> ".join(str(x) for x in error["loc"])
        logger.error(
            f"    ❌ Field: {loc}\n"
            f"       Type: {error['type']}\n"
            f"       Message: {error['msg']}"
        )

    simplified_errors = []
    for error in errors:
        loc = error.get("loc", ())
        field = loc[-1] if loc else "unknown"
        simplified_errors.append(
            ErrorDetail(field=str(field), message=error.get("msg", "Validation error"))
        )

    error_response = ErrorResponse(
        code="VALIDATION_001",
        message="Validation failed",
        errors=simplified_errors,
        timestamp=datetime.utcnow(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(mode="json", exclude_none=True),
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    logger.bind(
        error_code="CONFLICT_001",
        status_code=409,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "Unknown",
    ).error(
        f"Database Integrity Error\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}\n"
        f"  Error: {str(exc.orig)}\n"
        f"  Statement: {exc.statement}"
    )

    error_response = ErrorResponse(
        code="CONFLICT_001",
        message="Database integrity constraint violated",
        detail=str(exc.orig),
        timestamp=datetime.utcnow(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response.model_dump(mode="json", exclude_none=True),
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    logger.bind(
        error_code="SERVER_001",
        status_code=500,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "Unknown",
        error_type=type(exc).__name__,
    ).error(
        f"SQLAlchemy Error\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}\n"
        f"  Error Type: {type(exc).__name__}\n"
        f"  Error: {str(exc)}"
    )

    error_response = ErrorResponse(
        code="SERVER_001",
        message="Database error occurred",
        timestamp=datetime.utcnow(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode="json", exclude_none=True),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_str = "".join(tb)

    logger.bind(
        error_code="SERVER_001",
        status_code=500,
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "Unknown",
        error_type=type(exc).__name__,
    ).error(
        f"Unhandled Exception\n"
        f"  Path: {request.method} {request.url.path}\n"
        f"  Client: {request.client.host if request.client else 'Unknown'}\n"
        f"  Exception Type: {type(exc).__name__}\n"
        f"  Exception Message: {str(exc)}\n"
        f"  Traceback:\n{tb_str}"
    )

    error_response = ErrorResponse(
        code="SERVER_001",
        message="Internal server error",
        detail="An unexpected error occurred. Please try again later.",
        timestamp=datetime.utcnow(),
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode="json", exclude_none=True),
    )


def register_exception_handlers(app: Any) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("✅ Exception handlers registered")
