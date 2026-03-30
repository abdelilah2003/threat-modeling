from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_ask_endpoint() -> None:
    client = TestClient(app)
    res = client.post("/ask", json={"question": "What is password policy?"})
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body
    assert isinstance(body.get("retrieved_documents"), list)
