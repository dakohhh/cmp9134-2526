from uuid import uuid4
from ..types import TestTokens
from fastapi.testclient import TestClient


def test_update_user_role_v1(client: TestClient, commander_tokens: TestTokens) -> None:
    email = f"target_{uuid4().hex[:8]}@test.com"

    client.post("/v1/auth/register/", json={
        "full_name": "Target User",
        "email": email,
        "password": "password"
    })

    login_response = client.post("/v1/auth/login/", json={"email": email, "password": "password"})
    target_access_token = login_response.json()["data"]["access_token"]

    session_response = client.get(
        "/v1/auth/session",
        headers={"Authorization": f"Bearer {target_access_token}"}
    )
    target_user_id = session_response.json()["data"]["id"]

    response = client.post(
        f"/v1/admin/user/{target_user_id}/role",
        json={"role": "COMMANDER"},
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )

    assert response.status_code == 200
