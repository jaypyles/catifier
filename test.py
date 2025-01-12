from g4f.client import Client

client = Client()
response = client.images.generate(
    model="flux",
    prompt="a white siamese cat, who is a pirate on the moon",
    response_format="url"
)

image_url = response.data[0].url
print(f"Generated image URL: {image_url}")