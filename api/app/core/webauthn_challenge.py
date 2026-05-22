"""Short-lived signed cookie used to round-trip a WebAuthn challenge.

We avoid an external store (Redis) by encoding the challenge bytes inside a
JWT scoped to ``/api/v1/auth/`` with a short TTL (see
``WEBAUTHN_CHALLENGE_TTL_SECONDS``).
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from fastapi import Response
from jose import JWTError, jwt
from loguru import logger
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

from app.core.config import settings
from app.exceptions import BadRequestError

CHALLENGE_COOKIE_NAME = "webauthn_challenge"
CHALLENGE_COOKIE_PATH = "/api/v1/auth"

Intent = Literal["register", "login", "add_passkey"]


def issue_challenge_cookie(
    response: Response,
    *,
    challenge: bytes,
    intent: Intent,
    extra: dict[str, Any] | None = None,
) -> None:
    """Sign the challenge into a short-lived cookie."""
    payload: dict[str, Any] = {
        "challenge": bytes_to_base64url(challenge),
        "intent": intent,
        "exp": datetime.now(UTC)
        + timedelta(seconds=settings.WEBAUTHN_CHALLENGE_TTL_SECONDS),
    }
    if extra:
        payload.update(extra)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response.set_cookie(
        key=CHALLENGE_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.WEBAUTHN_CHALLENGE_TTL_SECONDS,
        path=CHALLENGE_COOKIE_PATH,
    )


def pop_challenge_cookie(
    cookie_value: str | None,
    *,
    expected_intent: Intent,
    response: Response,
) -> dict[str, Any]:
    """Validate, consume, and clear the challenge cookie.

    Returns the decoded payload with an extra ``challenge_bytes`` field.
    """
    if not cookie_value:
        logger.warning("Missing WebAuthn challenge cookie")
        raise BadRequestError(detail="Missing WebAuthn challenge")

    try:
        payload = jwt.decode(
            cookie_value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError as e:
        logger.warning(f"Invalid WebAuthn challenge cookie: {e!s}")
        raise BadRequestError(detail="Invalid or expired WebAuthn challenge") from e

    if payload.get("intent") != expected_intent:
        logger.warning(
            f"WebAuthn challenge intent mismatch: "
            f"got={payload.get('intent')}, expected={expected_intent}"
        )
        raise BadRequestError(detail="WebAuthn challenge intent mismatch")

    challenge_str = payload.get("challenge")
    if not isinstance(challenge_str, str):
        raise BadRequestError(detail="Malformed WebAuthn challenge")

    try:
        payload["challenge_bytes"] = base64url_to_bytes(challenge_str)
    except Exception as e:
        logger.error(f"Failed to decode challenge bytes: {e!s}")
        raise BadRequestError(detail="Malformed WebAuthn challenge") from e

    # One-shot: drop the cookie immediately.
    response.delete_cookie(
        key=CHALLENGE_COOKIE_NAME,
        path=CHALLENGE_COOKIE_PATH,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )

    return payload
