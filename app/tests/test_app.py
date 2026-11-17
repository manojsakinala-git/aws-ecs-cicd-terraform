from app import app


def test_health():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_create_task_requires_title():
    client = app.test_client()
    res = client.post("/tasks", json={})
    assert res.status_code == 400