from app import app


def test_health_check():
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
    assert data["service"] == "backend"


def test_get_modes():
    client = app.test_client()

    response = client.get("/api/modes")

    assert response.status_code == 200

    data = response.get_json()

    assert "modes" in data
    assert isinstance(data["modes"], list)
    assert len(data["modes"]) > 0


def test_create_task_without_text():
    client = app.test_client()

    response = client.post(
        "/api/tasks",
        json={
            "text": "",
            "mode": "improve"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data


def test_create_task_invalid_mode():
    client = app.test_client()

    response = client.post(
        "/api/tasks",
        json={
            "text": "тестовый текст",
            "mode": "unknown_mode"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Invalid mode"