from catifier.ai import generate_image_from_prompt
from catifier.storage import clear_images_from_bucket

def main():
    clear_images_from_bucket("catifier-images")
    prompt = input("Enter a prompt: ")
    image_path = generate_image_from_prompt(prompt)
    print(f"Image saved to {image_path}")

if __name__ == "__main__":
    main()