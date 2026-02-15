import time
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = id(request)
        start_time = time.time()

        client_host = request.client.host if request.client else "Unknown"
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params) if request.query_params else {}

        logger.info(
            f"🔵 Incoming Request\n"
            f"  ID: {request_id}\n"
            f"  Method: {method}\n"
            f"  Path: {path}\n"
            f"  Client: {client_host}\n"
            f"  Query Params: {query_params if query_params else 'None'}"
        )

        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"🔴 Request Failed\n"
                f"  ID: {request_id}\n"
                f"  Method: {method}\n"
                f"  Path: {path}\n"
                f"  Client: {client_host}\n"
                f"  Duration: {process_time:.2f}ms\n"
                f"  Exception: {type(e).__name__}: {str(e)}"
            )
            raise

        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code

        if status_code < 400:
            log_level = "success"
            emoji = "🟢"
        elif status_code < 500:
            log_level = "warning"
            emoji = "🟡"
        else:
            log_level = "error"
            emoji = "🔴"

        logger.log(
            log_level.upper(),
            f"{emoji} Request Completed\n"
            f"  ID: {request_id}\n"
            f"  Method: {method}\n"
            f"  Path: {path}\n"
            f"  Status: {status_code}\n"
            f"  Duration: {process_time:.2f}ms\n"
            f"  Client: {client_host}",
        )

        return response
