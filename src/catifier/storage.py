import os
import random
import string
import subprocess

from catifier.constants import IMAGE_PATH

def store_image(image_content: bytes, prompt: str) -> str:
    os.makedirs(IMAGE_PATH, exist_ok=True)

    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    path = f"{IMAGE_PATH}/{'_'.join(prompt.split(' ')[:4])}-{random_suffix}.png"

    with open(path, "wb") as f:
        _ = f.write(image_content)

    return path

def write_to_google_storage(image_path: str, bucket_name: str) -> str:
    try:
        # Upload the image to the bucket
        _ = subprocess.run(
            ["gsutil", "cp", image_path, f"gs://{bucket_name}/"],
            check=True
        )
        print(f"File {image_path} uploaded to {bucket_name}.")

        # Make the image publicly accessible
        image_name = os.path.basename(image_path)
        _ = subprocess.run(
            ["gsutil", "acl", "ch", "-u", "AllUsers:R", f"gs://{bucket_name}/{image_name}"],
            check=True
        )
        print(f"File {image_name} is now publicly accessible.")

        # Return the public URL
        public_url = f"https://storage.googleapis.com/{bucket_name}/{image_name}"

        return public_url

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return ""

def get_all_images_from_bucket(bucket_name: str) -> dict[str, bytes]:
    try:
        result = subprocess.run(
            ["gsutil", "ls", f"gs://{bucket_name}/"],
            check=True,
            capture_output=True,
            text=True
        )
        image_paths = result.stdout.splitlines()
        images = {}
        for image_path in image_paths:
            image_name = os.path.basename(image_path)
            image_content = subprocess.run(
                ["gsutil", "cp", image_path, "-"],
                check=True,
                capture_output=True
            ).stdout
            images[image_name] = image_content
        return images
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return {}

def clear_images_from_bucket(bucket_name: str) -> None:
    try:
        subprocess.run(
            ["gsutil", "rm", f"gs://{bucket_name}/*"],
            check=True
        )
        print(f"All images from {bucket_name} have been deleted.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
