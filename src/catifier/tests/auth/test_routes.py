from freezegun import freeze_time
from fastapi.testclient import TestClient
from catifier.app import app

from unittest.mock import patch
import uuid


client = TestClient(app)


class TestRegister:
    def test_register_user(self):
        response = client.post(
            "/register", json={"username": "test", "password": "test"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "User registered successfully"}

    def test_failed_register_user(self):
        response = client.post(
            "/register", json={"username": "test", "password": "test"}
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "User with this username already exists"}


class TestLogin:
    def test_login(self):
        response = client.post("/login", data={"username": "test", "password": "test"})
        assert response.status_code == 200
        assert response.json() == {"message": "User logged in successfully"}

    def test_failed_login(self):
        response = client.post("/login", data={"username": "test", "password": "wrong"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid username or password"}


class TestApiKey:
    @freeze_time("2023-01-01")
    def test_create_api_key(self):
        response = client.post("/login", data={"username": "test", "password": "test"})
        access_token = response.headers["Set-Cookie"].split("=")[1].split(";")[0]

        mock_uuid = uuid.UUID("12345678123456781234567812345678")
        with patch("uuid.uuid4", return_value=mock_uuid):
            response = client.put(
                "/create-api-key", headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            assert response.json() == {
                "message": "API key created successfully",
                "api_key": mock_uuid.hex,
            }
