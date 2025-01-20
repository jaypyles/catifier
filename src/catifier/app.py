from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from catifier.ai import generate_image_from_prompt
from catifier.auth.database import get_db
from catifier.auth.models import Image
from catifier.auth.utils import decrement_credit, get_user, get_user_credits
from catifier.storage import clear_images_from_bucket
from pydantic import BaseModel
import uvicorn
from catifier.auth.router import router as auth_router
from dotenv import load_dotenv

_ = load_dotenv()

app = FastAPI()

app.include_router(auth_router)

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
async def generate_image(
    request: GenerateRequest, token: str = Header(..., alias="Authorization")
):
    user = get_user(token)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    credits = get_user_credits(user["id"])

    if credits is None or credits <= 0:
        raise HTTPException(status_code=403, detail="No credits left")

    try:
        image_url = await generate_image_from_prompt(request.prompt)
        decrement_credit(user["id"])

        image = Image(user_id=user["id"], image_url=image_url)

        db = next(get_db())
        db.add(image)
        db.commit()

        return JSONResponse(
            content={
                "message": "success",
                "image_url": image_url,
                "credits": get_user_credits(user["id"]),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/images")
def list_images(token: str = Header(..., alias="Authorization")):
    user = get_user(token)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        db = next(get_db())
        images = db.query(Image).filter(Image.user_id == user["id"]).all()
        return JSONResponse(content={"images": [image.image_url for image in images]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/images")
def delete_images():
    try:
        clear_images_from_bucket(BUCKET_NAME)
        return {"message": "All images cleared from bucket."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
