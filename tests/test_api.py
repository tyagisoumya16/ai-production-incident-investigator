from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_rag_endpoint():
    response = client.post(
        "/rag/search",
        json={
            "incident": (
                "Payment requests are timing out "
                "with database connection errors"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "query" in data
    assert "context" in data