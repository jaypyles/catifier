from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from catifier.ai import generate_image_from_prompt
from catifier.storage import get_all_images_from_bucket, clear_images_from_bucket
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BUCKET_NAME = "catifier-images"

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    print(request)
    try:
        image_url = await generate_image_from_prompt(request.prompt)
        return JSONResponse(content={"message": "success", "image_url": image_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images")
def list_images():
    try:
        images = get_all_images_from_bucket(BUCKET_NAME)
        return JSONResponse(content=images)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/images")
def delete_images():
    try:
        clear_images_from_bucket(BUCKET_NAME)
        return {"message": "All images cleared from bucket."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

