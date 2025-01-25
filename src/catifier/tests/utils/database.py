from fastapi.testclient import TestClient


def register(client: TestClient, username: str, password: str):
    response = client.post(
        "/register", json={"username": username, "password": password}
    )
    return response.json()


def login(client: TestClient, username: str, password: str):
    response = client.post("/login", data={"username": username, "password": password})
    return response.headers["Set-Cookie"].split("=")[1].split(";")[0]
