from fastapi.testclient import TestClient

from backend.app.api import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_serialized_graph(tmp_path) -> None:
    (tmp_path / "main.py").write_text("import helper\n", encoding="utf-8")
    (tmp_path / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")

    response = client.post("/api/analyze", json={"repo_path": str(tmp_path)})

    assert response.status_code == 200
    payload = response.json()
    assert payload["repo_root"] == str(tmp_path)
    assert {node["module_path"] for node in payload["nodes"]} == {"main", "helper"}
    assert payload["edges"][0]["source"] == "main"
    assert payload["edges"][0]["target"] == "helper"


def test_analyze_rejects_invalid_repository() -> None:
    response = client.post(
        "/api/analyze",
        json={"repo_path": "/path/that/does/not/exist"},
    )

    assert response.status_code == 400
    assert "Invalid repository path" in response.json()["detail"]
