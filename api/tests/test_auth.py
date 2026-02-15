from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.main import app


# Override the database dependency to avoid connecting to a real DB
async def override_get_db():
    mock_session = AsyncMock(spec=AsyncSession)

    mock_scalars = AsyncMock()
    mock_scalars.first.return_value = None

    mock_result = AsyncMock()
    mock_result.scalars.return_value = mock_scalars

    async def mock_execute(*args, **kwargs):
        return mock_result

    mock_session.execute = mock_execute
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = AsyncMock()

    yield mock_session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def mock_google_response():
    return {
        "iss": "https://accounts.google.com",
        "aud": "test-google-client-id",
        "sub": "1234567890",
        "email": "test@example.com",
        "email_verified": True,
        "name": "Test User",
    }


@pytest.mark.asyncio
async def test_login_google_success(mock_google_response):
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-google-client-id"):
        with patch("app.services.auth_service.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance

            mock_client_instance.get.return_value = Response(
                200, json=mock_google_response
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                response = await ac.post(
                    "/api/v1/login/google", json={"token": "fake-valid-google-token"}
                )

            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert "user" in data
            assert "id" in data["user"]
            assert "email" in data["user"]
            assert "name" in data["user"]


@pytest.mark.asyncio
async def test_login_google_invalid_token():
    with patch("app.services.auth_service.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client_instance

        mock_client_instance.get.return_value = Response(
            400, json={"error": "invalid_token"}
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/api/v1/login/google", json={"token": "invalid-token"}
            )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid Google token"


@pytest.mark.asyncio
async def test_login_google_wrong_audience(mock_google_response):
    with patch.object(settings, "GOOGLE_CLIENT_ID", "my-real-app-id"):
        with patch("app.services.auth_service.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance

            mock_client_instance.get.return_value = Response(
                200, json=mock_google_response
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as ac:
                response = await ac.post(
                    "/api/v1/login/google", json={"token": "valid-token-wrong-app"}
                )

            assert response.status_code == 400
            assert response.json()["detail"] == "Invalid Google Client ID"
