from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register():
    r = client.post("/register", json={
        "username": "tim", "email": "tim@mail.ru", "password": "qwerty123"
    })
    assert r.status_code == 200 or r.status_code == 400  # 400 если уже зарегистрирован


def test_login_wrong_password():
    r = client.post("/login", data={"username": "tim", "password": "wrongpass"})
    assert r.status_code == 401


def test_tasks_without_auth():
    r = client.get("/tasks")
    assert r.status_code == 401
