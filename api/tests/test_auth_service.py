from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repo(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo)


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
async def test_authenticate_google_user_success(auth_service, mock_google_response):
    with patch.object(settings, "GOOGLE_CLIENT_ID", "test-google-client-id"):
        with patch("app.services.auth_service.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance

            mock_client_instance.get.return_value = Response(
                200, json=mock_google_response
            )

            auth_service.user_repo.get_by_email = AsyncMock(return_value=None)

            mock_user = AsyncMock()
            mock_user.id = 1
            auth_service.user_repo.create = AsyncMock(return_value=mock_user)

            result = await auth_service.authenticate_google_user("fake-token")

            assert "token" in result
            assert "user" in result
            assert result["user"]["id"] == "1"
            assert result["user"]["email"] == mock_user.email
            auth_service.user_repo.create.assert_called_once()
