import os

IMAGE_PATH = "/app/images"
APP_MODE = os.environ.get("APP_MODE", "prod")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
