"""Endpoint-level tests for WebAuthn ceremonies.

We mock at the py-webauthn boundary (``generate_*_options``/``verify_*_response``)
and the persistence layer, so we exercise our orchestration code without
needing a real database or authenticator.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.webauthn_challenge import CHALLENGE_COOKIE_NAME
from app.db.session import get_db
from app.main import app


async def _override_get_db():
    mock_session = AsyncMock(spec=AsyncSession)

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_result.scalar_one_or_none.return_value = None

    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()

    yield mock_session


app.dependency_overrides[get_db] = _override_get_db


def _fake_options() -> MagicMock:
    opts = MagicMock()
    opts.challenge = b"\x01\x02\x03\x04challenge-bytes"
    return opts


def _fake_verified_registration() -> MagicMock:
    v = MagicMock()
    v.credential_id = b"new-credential-id"
    v.credential_public_key = b"new-public-key"
    v.sign_count = 0
    return v


@pytest.mark.asyncio
async def test_register_options_returns_json_and_sets_cookie():
    with patch(
        "app.services.webauthn_service.generate_registration_options",
        return_value=_fake_options(),
    ), patch(
        "app.services.webauthn_service.options_to_json",
        return_value='{"challenge": "AQIDBA"}',
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/api/v1/auth/register/options",
                json={"email": "new@example.com", "name": "New User"},
            )

    assert response.status_code == 200
    assert response.json()["challenge"] == "AQIDBA"
    set_cookie = response.headers.get("set-cookie", "")
    assert CHALLENGE_COOKIE_NAME in set_cookie


@pytest.mark.asyncio
async def test_register_verify_requires_challenge_cookie():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/v1/auth/register/verify",
            json={"credential": {"id": "abc", "rawId": "abc", "response": {}}},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_verify_with_bad_cookie():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        ac.cookies.set(CHALLENGE_COOKIE_NAME, "not-a-jwt")
        response = await ac.post(
            "/api/v1/auth/register/verify",
            json={"credential": {"id": "abc", "rawId": "abc", "response": {}}},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_options_returns_json_and_sets_cookie():
    with patch(
        "app.services.webauthn_service.generate_authentication_options",
        return_value=_fake_options(),
    ), patch(
        "app.services.webauthn_service.options_to_json",
        return_value='{"challenge": "AQIDBA"}',
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post("/api/v1/auth/login/options")

    assert response.status_code == 200
    assert response.json()["challenge"] == "AQIDBA"
    assert CHALLENGE_COOKIE_NAME in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_register_verify_success_creates_user_and_passkey():
    """Full ceremony: options sets the cookie, verify creates the user."""
    user = MagicMock()
    user.id = uuid4()
    user.email = "new@example.com"
    user.full_name = "New User"
    user.created_at = None

    fake_repo_create = AsyncMock(return_value=user)
    fake_repo_get_by_email = AsyncMock(return_value=None)

    with patch(
        "app.services.webauthn_service.generate_registration_options",
        return_value=_fake_options(),
    ), patch(
        "app.services.webauthn_service.options_to_json",
        return_value='{"challenge": "AQIDBA"}',
    ), patch(
        "app.services.webauthn_service.verify_registration_response",
        return_value=_fake_verified_registration(),
    ), patch(
        "app.services.webauthn_service.create_refresh_token_db",
        new=AsyncMock(return_value="fake-refresh-token"),
    ), patch(
        "app.services.webauthn_service.UserRepository.get_by_email",
        new=fake_repo_get_by_email,
    ), patch(
        "app.services.webauthn_service.UserRepository.create",
        new=fake_repo_create,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            options_resp = await ac.post(
                "/api/v1/auth/register/options",
                json={"email": "new@example.com", "name": "New User"},
            )
            assert options_resp.status_code == 200

            verify_resp = await ac.post(
                "/api/v1/auth/register/verify",
                json={
                    "credential": {
                        "id": "abc",
                        "rawId": "abc",
                        "response": {"transports": ["internal"]},
                    }
                },
            )

    assert verify_resp.status_code == 200, verify_resp.text
    body = verify_resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "new@example.com"
    fake_repo_create.assert_awaited_once()
