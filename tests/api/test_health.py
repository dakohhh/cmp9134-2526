from fastapi.testclient import TestClient


def test_health_v1(client: TestClient) -> None:
    response = client.get("/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"message": "Health check", "data": None, "status_code": 200 }