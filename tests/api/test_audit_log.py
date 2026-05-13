from ..types import TestTokens
from fastapi.testclient import TestClient


def test_get_all_audit_logs_v1(client: TestClient, commander_tokens: TestTokens) -> None:
    response = client.get(
        "/v1/audit-log/",
        headers={"Authorization": f"Bearer {commander_tokens['access_token']}"},
    )

    print()
    print()

    print(response.json())
    print()
    print()



    assert response.status_code == 200
