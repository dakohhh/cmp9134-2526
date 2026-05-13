from fastapi.testclient import TestClient


def test_register_v1(client: TestClient) -> None:
    response = client.post("/v1/auth/register/", json={
        "full_name": "Test Wisdom", 
        "email": "test@wisdom.com",
        "password": "password"
    })

    assert response.status_code == 200

def test_login_v1(client: TestClient) -> None:
    client.post("/v1/auth/register/", json={
        "full_name": "Test User",
        "email": "user@wisdom.com",
        "password": "password"
    })

    response = client.post("/v1/auth/login/", json={
        "email": "user@wisdom.com",
        "password": "password"
    })
    assert response.status_code == 200



def test_refresh_token_v1(client: TestClient) -> None:
    client.post("/v1/auth/register/", json={
        "full_name": "test_refresh_token_v1",
        "email": "test_refresh_token_v1@test.com",
        "password": "password"
    })


    login_response = client.post("/v1/auth/login/", json={
        "email": "test_refresh_token_v1@test.com",
        "password": "password"
    })
    refresh_token = login_response.json()["data"]["refresh_token"]

    response = client.post("/v1/auth/refresh-token", cookies={"refresh_token": refresh_token})

    assert response.status_code == 200


def test_get_session_v1(client: TestClient) -> None:
    client.post("/v1/auth/register/", json={
        "full_name": "test_get_session_v1",
        "email": "test_get_session_v1@test.com",
        "password": "password"
    })

    login_response = client.post("/v1/auth/login/", json={
        "email": "test_get_session_v1@test.com",
        "password": "password"
    })
    access_token = login_response.json()["data"]["access_token"]

    response = client.get("/v1/auth/session", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200


def test_logout_v1(client: TestClient) -> None:
    client.post("/v1/auth/register/", json={
        "full_name": "test_logout_v1",
        "email": "test_logout_v1@test.com",
        "password": "password"
    })

    login_response = client.post("/v1/auth/login/", json={
        "email": "test_logout_v1@test.com",
        "password": "password"
    })
    access_token = login_response.json()["data"]["access_token"]
    refresh_token = login_response.json()["data"]["refresh_token"]

    response = client.post(
        "/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        cookies={"refresh_token": refresh_token},
    )

    assert response.status_code == 200