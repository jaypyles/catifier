from g4f.client import Client
import requests
from catifier.prompts import CAT_PROMPT
from catifier.storage import store_image, write_to_google_storage
from catifier.constants import APP_MODE
import asyncio
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()

def download_from_url(url: str, prompt: str) -> str:
    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError(f"Failed to download image from {url}")

    return store_image(response.content, prompt)


def blocking_generate_image(prompt: str) -> str:
    client = Client()
    response = client.images.generate(
        model="flux",
        prompt=CAT_PROMPT.format(prompt=prompt),
        response_format="url"
    )

    image_url = response.data[0].url
    if image_url is None:
        raise ValueError("No image URL returned from AI")

    return image_url

async def generate_image_from_prompt(prompt: str) -> str | None:
    loop = asyncio.get_event_loop()
    image_url = await loop.run_in_executor(executor, blocking_generate_image, prompt)
    image_path = download_from_url(image_url, prompt)

    if APP_MODE == "prod":
        return write_to_google_storage(image_path, "catifier-images")
