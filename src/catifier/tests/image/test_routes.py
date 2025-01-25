from freezegun import freeze_time
from catifier.tests.utils.database import create_api_key, login, register
from catifier.tests.conftest import client
from unittest.mock import patch


def generate_image(username: str, password: str, api_key: str | None = None):
    if not api_key:
        access_token = login(client, username, password)
    else:
        access_token = api_key

    headers = {"Authorization": f"Bearer {access_token}"}

    if api_key:
        headers = {"X-API-Key": api_key}

    with patch(
        "catifier.app.generate_image_from_prompt",
        return_value="https://example.com/image.jpg",
    ):
        response = client.post(
            "/generate",
            json={"prompt": "a cat"},
            headers=headers,
        )

        return response


@freeze_time("2025-01-01 00:00:00")
class TestGenerate:
    def test_generate(self):
        register(client, "test_generate_user_image", "test")
        response = generate_image("test_generate_user_image", "test")

        assert response.status_code == 200
        assert response.json() == {
            "message": "success",
            "credits": 0,
            "image_url": "https://example.com/image.jpg",
        }

    def test_generate_with_api_key(self):
        register(client, "test_generate_user_image_with_api_key", "test")

        api_key = create_api_key(
            client, "test_generate_user_image_with_api_key", "test"
        )

        response = generate_image(
            "test_generate_user_image_with_api_key", "test", api_key
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "success",
            "credits": 0,
            "image_url": "https://example.com/image.jpg",
        }

    def test_generate_with_invalid_api_key(self):
        username = "test_generate_user_image_with_api_key"
        register(client, username, "test")

        api_key = "invalid_api_key"

        response = generate_image(username, "test", api_key)

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API key"}

    def test_generate_no_credits(self):
        register(client, "test_generate_user_image_no_credits", "test")
        response = generate_image("test_generate_user_image_no_credits", "test")

        assert response.status_code == 200
        assert response.json() == {
            "message": "success",
            "credits": 0,
            "image_url": "https://example.com/image.jpg",
        }

        response = generate_image("test_generate_user_image_no_credits", "test")

        assert response.status_code == 403
        assert response.json() == {"detail": "User has no credits"}
