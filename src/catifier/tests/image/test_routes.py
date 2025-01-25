from freezegun import freeze_time
from catifier.tests.utils.database import login, register
from catifier.tests.conftest import client
from unittest.mock import patch


@freeze_time("2025-01-01 00:00:00")
class TestGenerate:
    def test_generate(self):
        register(client, "test_generate_user_image", "test")

        access_token = login(client, "test_generate_user_image", "test")

        with patch(
            "catifier.app.generate_image_from_prompt",
            return_value="https://example.com/image.jpg",
        ):
            response = client.post(
                "/generate",
                json={"prompt": "a cat"},
                headers={"Authorization": f"Bearer {access_token}"},
            )

            assert response.status_code == 200
            assert response.json() == {
                "message": "success",
                "credits": 0,
                "image_url": "https://example.com/image.jpg",
            }
