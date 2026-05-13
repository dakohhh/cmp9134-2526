import pytest
from ..types import TestTokens
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_get_map_integration(client: TestClient, commander_tokens: TestTokens) -> None:
    response = client.get(
        "/v1/map/",
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["width"] > 0
    assert data["height"] > 0
    assert len(data["grid"]) == data["height"]


def test_move_robot_integration(client: TestClient, commander_tokens: TestTokens) -> None:
    response = client.post(
        "/v1/robot/move/",
        json={"navigation": "RIGHT"},
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )
    assert response.status_code == 200

    audit_response = client.get(
        "/v1/audit-log/",
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )
    assert audit_response.status_code == 200
    logs = audit_response.json()["data"]["results"]
    assert any(log["action"] == "COMMAND" for log in logs)


def test_reset_robot_integration(client: TestClient, commander_tokens: TestTokens) -> None:
    response = client.post(
        "/v1/robot/reset/",
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )
    assert response.status_code == 200

    audit_response = client.get(
        "/v1/audit-log/",
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )
    assert audit_response.status_code == 200
    logs = audit_response.json()["data"]["results"]
    assert any(log["action"] == "RESET_ROBOT" for log in logs)
