"""WebAuthn / passkeys service.

Wraps the py-webauthn library to provide registration and authentication
ceremonies, and manage stored credentials. Challenge state is kept in a
short-lived signed cookie issued by the calling endpoint (see
``app.core.webauthn_challenge``).
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import Response
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import options_to_json
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app.core.config import settings
from app.core.security import create_access_token
from app.core.tokens import create_refresh_token_db
from app.core.webauthn_challenge import (
    issue_challenge_cookie,
    pop_challenge_cookie,
)
from app.exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    DuplicateResourceError,
    NotFoundError,
)
from app.models.user import User
from app.models.webauthn_credential import WebAuthnCredential
from app.repositories.user_repository import UserRepository


class WebAuthnService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.session: AsyncSession = user_repo.session

    # ------------------------------------------------------------------
    # Registration (new user)
    # ------------------------------------------------------------------
    async def begin_registration(
        self, email: str, name: str, response: Response
    ) -> dict[str, Any]:
        logger.info(f"Beginning WebAuthn registration for email={email}")

        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            logger.warning(f"Registration attempted for existing email={email}")
            raise DuplicateResourceError(
                resource="user",
                detail="An account with this email already exists.",
            )

        # We use the email as the user_id surrogate at this stage so the user
        # can be recreated deterministically on verify. py-webauthn requires
        # bytes for user_id.
        user_handle = email.encode("utf-8")

        options = generate_registration_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            rp_name=settings.WEBAUTHN_RP_NAME,
            user_name=email,
            user_id=user_handle,
            user_display_name=name or email,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )

        issue_challenge_cookie(
            response,
            challenge=options.challenge,
            intent="register",
            extra={"email": email, "name": name},
        )

        return _json_options(options)

    async def finish_registration(
        self,
        credential: dict[str, Any],
        challenge_cookie: str | None,
        response: Response,
    ) -> dict[str, Any]:
        payload = pop_challenge_cookie(
            challenge_cookie, expected_intent="register", response=response
        )
        email = payload.get("email")
        name = payload.get("name") or ""
        if not email:
            logger.error("Registration challenge missing email")
            raise BadRequestError(detail="Invalid registration session")

        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=payload["challenge_bytes"],
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                expected_origin=settings.WEBAUTHN_EXPECTED_ORIGIN,
                require_user_verification=True,
            )
        except Exception as e:
            logger.error(f"Registration verification failed: {e!s}")
            raise BadRequestError(detail="Invalid registration response") from e

        # Just in case someone raced us
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            logger.warning(f"User created between options and verify: email={email}")
            raise DuplicateResourceError(resource="user")

        user = await self.user_repo.create(
            email=email,
            full_name=name or None,
            is_active=True,
            is_superuser=False,
        )
        logger.success(f"New user created via passkey: id={user.id}, email={email}")

        transports = _extract_transports(credential)
        device_name = _guess_device_name(credential)

        cred = WebAuthnCredential(
            user_id=user.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            transports=transports,
            device_name=device_name,
        )
        self.session.add(cred)
        await self.session.commit()
        await self.session.refresh(cred)
        logger.info(f"Passkey registered for user_id={user.id}, cred_id={cred.id}")

        await _issue_session(self.session, user, response)
        return _login_payload(user)

    # ------------------------------------------------------------------
    # Authentication (existing user, usernameless)
    # ------------------------------------------------------------------
    async def begin_authentication(self, response: Response) -> dict[str, Any]:
        logger.info("Beginning WebAuthn authentication (usernameless)")

        options = generate_authentication_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            user_verification=UserVerificationRequirement.REQUIRED,
            allow_credentials=[],
        )

        issue_challenge_cookie(response, challenge=options.challenge, intent="login")
        return _json_options(options)

    async def finish_authentication(
        self,
        credential: dict[str, Any],
        challenge_cookie: str | None,
        response: Response,
    ) -> dict[str, Any]:
        payload = pop_challenge_cookie(
            challenge_cookie, expected_intent="login", response=response
        )

        credential_id = _decode_credential_id(credential)
        stored = await _get_credential_by_credential_id(self.session, credential_id)
        if stored is None:
            logger.warning(
                f"Authentication for unknown credential_id={credential_id!r}"
            )
            raise AuthenticationError(detail="Unknown credential")

        try:
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=payload["challenge_bytes"],
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                expected_origin=settings.WEBAUTHN_EXPECTED_ORIGIN,
                credential_public_key=stored.public_key,
                credential_current_sign_count=stored.sign_count,
                require_user_verification=True,
            )
        except Exception as e:
            logger.error(f"Authentication verification failed: {e!s}")
            raise AuthenticationError(detail="Invalid authentication response") from e

        stored.sign_count = verification.new_sign_count
        stored.last_used_at = datetime.now(UTC)
        await self.session.commit()

        user = await self.user_repo.get(stored.user_id)
        if user is None:
            logger.error(f"Credential references missing user_id={stored.user_id}")
            raise AuthenticationError(detail="Account no longer exists")

        await _issue_session(self.session, user, response)
        logger.success(f"Passkey login successful for user_id={user.id}")
        return _login_payload(user)

    # ------------------------------------------------------------------
    # Passkey management (authenticated)
    # ------------------------------------------------------------------
    async def list_passkeys(self, user_id: UUID) -> list[WebAuthnCredential]:
        result = await self.session.execute(
            select(WebAuthnCredential)
            .where(WebAuthnCredential.user_id == user_id)
            .order_by(WebAuthnCredential.created_at.asc())
        )
        return list(result.scalars().all())

    async def begin_add_passkey(self, user: User, response: Response) -> dict[str, Any]:
        logger.info(f"Beginning add-passkey for user_id={user.id}")

        existing = await self.list_passkeys(user.id)
        exclude = [PublicKeyCredentialDescriptor(id=c.credential_id) for c in existing]

        options = generate_registration_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            rp_name=settings.WEBAUTHN_RP_NAME,
            user_name=user.email,
            user_id=str(user.id).encode("utf-8"),
            user_display_name=user.full_name or user.email,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            exclude_credentials=exclude,
        )

        issue_challenge_cookie(
            response,
            challenge=options.challenge,
            intent="add_passkey",
            extra={"user_id": str(user.id)},
        )
        return _json_options(options)

    async def finish_add_passkey(
        self,
        user: User,
        credential: dict[str, Any],
        challenge_cookie: str | None,
        response: Response,
    ) -> WebAuthnCredential:
        payload = pop_challenge_cookie(
            challenge_cookie, expected_intent="add_passkey", response=response
        )
        if payload.get("user_id") != str(user.id):
            logger.error(
                f"Add-passkey user mismatch: cookie={payload.get('user_id')}, "
                f"session={user.id}"
            )
            raise BadRequestError(detail="Invalid add-passkey session")

        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=payload["challenge_bytes"],
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                expected_origin=settings.WEBAUTHN_EXPECTED_ORIGIN,
                require_user_verification=True,
            )
        except Exception as e:
            logger.error(f"Add-passkey verification failed: {e!s}")
            raise BadRequestError(detail="Invalid passkey response") from e

        transports = _extract_transports(credential)
        device_name = _guess_device_name(credential)
        cred = WebAuthnCredential(
            user_id=user.id,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            transports=transports,
            device_name=device_name,
        )
        self.session.add(cred)
        await self.session.commit()
        await self.session.refresh(cred)
        logger.success(f"Added passkey id={cred.id} for user_id={user.id}")
        return cred

    async def delete_passkey(self, user: User, passkey_id: UUID) -> None:
        result = await self.session.execute(
            select(WebAuthnCredential).where(
                WebAuthnCredential.id == passkey_id,
                WebAuthnCredential.user_id == user.id,
            )
        )
        cred = result.scalar_one_or_none()
        if cred is None:
            logger.warning(
                f"Delete-passkey not found: id={passkey_id}, user_id={user.id}"
            )
            raise NotFoundError(resource="passkey", resource_id=str(passkey_id))

        all_passkeys = await self.list_passkeys(user.id)
        if len(all_passkeys) <= 1:
            logger.warning(f"Refusing to delete last passkey for user_id={user.id}")
            raise ConflictError(
                code="CONFLICT_005",
                message="Cannot delete last passkey",
                detail="At least one passkey must remain on the account.",
            )

        await self.session.delete(cred)
        await self.session.commit()
        logger.info(f"Deleted passkey id={passkey_id} for user_id={user.id}")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _json_options(options: Any) -> dict[str, Any]:
    """Convert py-webauthn options struct to a plain JSON-serialisable dict.

    py-webauthn returns Pydantic-like structs with binary fields. ``options_to_json``
    handles all of the base64url encoding correctly, including
    ``allowCredentials``/``excludeCredentials`` and ``user.id``.
    """
    import json

    return json.loads(options_to_json(options))


def _login_payload(user: User) -> dict[str, Any]:
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.full_name or "",
            "created_at": user.created_at,
        },
    }


async def _issue_session(session: AsyncSession, user: User, response: Response) -> None:
    refresh_token_value = await create_refresh_token_db(session, user.id)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_value,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1",
    )


def _extract_transports(credential: dict[str, Any]) -> list[str]:
    response = credential.get("response") if isinstance(credential, dict) else None
    if not isinstance(response, dict):
        return []
    raw = response.get("transports")
    if isinstance(raw, list):
        return [str(t) for t in raw if isinstance(t, str)]
    return []


def _guess_device_name(credential: dict[str, Any]) -> str | None:
    """Best-effort device label from authenticatorAttachment if provided."""
    if not isinstance(credential, dict):
        return None
    attachment = credential.get("authenticatorAttachment")
    if isinstance(attachment, str) and attachment:
        return attachment
    return None


def _decode_credential_id(credential: dict[str, Any]) -> bytes:
    from webauthn.helpers import base64url_to_bytes

    raw_id = credential.get("rawId") if isinstance(credential, dict) else None
    if not isinstance(raw_id, str):
        # ``id`` is also base64url-encoded per the spec
        raw_id = credential.get("id") if isinstance(credential, dict) else None
    if not isinstance(raw_id, str):
        raise BadRequestError(detail="Credential is missing id")
    try:
        return base64url_to_bytes(raw_id)
    except Exception as e:
        logger.error(f"Failed to decode credential id: {e!s}")
        raise BadRequestError(detail="Invalid credential id") from e


async def _get_credential_by_credential_id(
    session: AsyncSession, credential_id: bytes
) -> WebAuthnCredential | None:
    result = await session.execute(
        select(WebAuthnCredential).where(
            WebAuthnCredential.credential_id == credential_id
        )
    )
    return result.scalar_one_or_none()
