from ..types import TestTokens
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


def test_move_robot_v1(client: TestClient, mock_http_client: AsyncMock, commander_tokens: TestTokens) -> None:
    mock_redis = AsyncMock()
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1

    mock_status_response = MagicMock()
    mock_status_response.json.return_value = {"position": {"x": 5, "y": 5}}
    mock_status_response.raise_for_status.return_value = None

    mock_move_response = MagicMock()
    mock_move_response.raise_for_status.return_value = None

    mock_http_client.get.return_value = mock_status_response
    mock_http_client.post.return_value = mock_move_response

    with patch("app.robot.service.redis_from_url", AsyncMock(return_value=mock_redis)):
        response = client.post(
            "/v1/robot/move/",
            json={"navigation": "RIGHT"},
            headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
        )

    assert response.status_code == 200


def test_reset_robot_v1(client: TestClient, mock_http_client: AsyncMock, commander_tokens: TestTokens) -> None:
    mock_redis = AsyncMock()
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1

    mock_reset_response = MagicMock()
    mock_reset_response.raise_for_status.return_value = None

    mock_http_client.post.return_value = mock_reset_response

    with patch("app.robot.service.redis_from_url", AsyncMock(return_value=mock_redis)):
        response = client.post(
            "/v1/robot/reset/",
            headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
        )

    assert response.status_code == 200
