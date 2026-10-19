def register(client, username="test", email="test@mail.ru", password="qwerty123"):
    return client.post("/register", json={"username": username, "email": email, "password": password})


def auth_headers(client, username="test", password="qwerty123"):
    r = client.post("/login", data={"username": username, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_register(client):
    r = register(client)
    assert r.status_code == 200
    assert r.json()["username"] == "test"
    assert "password" not in r.json()


def test_register_duplicate_username(client):
    assert register(client).status_code == 200 
    r = register(client, email="test1@mail.ru")
    assert r.status_code == 409


def test_login_wrong_password(client):
    assert register(client).status_code == 200 
    r = client.post("/login", data={"username": "test", "password": "password"})
    assert r.status_code == 401


def test_tasks_without_auth(client):
    r = client.get("/tasks")
    assert r.status_code == 401


def test_foreign_task_404(client):
    assert register(client, "anna", "anna@mail.ru").status_code == 200
    assert register(client, "boris", "boris@mail.ru").status_code == 200
    anna = auth_headers(client, "anna")
    boris = auth_headers(client, "boris")

    r = client.post("/tasks", json={"title": "секрет Анны"}, headers=anna)
    assert r.status_code == 201
    task_id = r.json()["id"]

    r = client.patch(f"/tasks/{task_id}", json={"title": "взломано"}, headers=boris)
    assert r.status_code == 404

    r = client.delete(f"/tasks/{task_id}", headers=boris)
    assert r.status_code == 404

    r = client.get("/tasks", headers=boris)
    assert r.json() == []

    r = client.get("/tasks", headers=anna)
    assert r.json()[0]["title"] == "секрет Анны"