from ..types import TestTokens
from fastapi.testclient import TestClient
from pytest_mock import AsyncMockType, MockerFixture


def test_get_map_v1(
    client: TestClient, 
    mocker: MockerFixture, 
    mock_http_client: AsyncMockType,
    mock_redis_client: AsyncMockType,
    commander_tokens: TestTokens
) -> None:
    mock_redis_client.get.return_value = None
    
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {
        "width": 20,
        "height": 20,
        "grid": [[0] * 20 for _ in range(20)],
    }
    mock_response.raise_for_status.return_value = None
    
    mock_http_client.get.return_value = mock_response

    response = client.get(
        "/v1/map/",
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )

    assert response.status_code == 200
