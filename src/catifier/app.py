from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from catifier.logger import LOG
from catifier.ai import generate_image_from_prompt
from catifier.auth.database import get_db
from catifier.auth.models import Image, User
from catifier.auth.user_manager.user_manager import UserManager
from catifier.auth.decorators import requires_credit
from catifier.storage import clear_images_from_bucket
from pydantic import BaseModel
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
@requires_credit()
async def generate_image(
    request: GenerateRequest,
    user: User = Depends(UserManager.get_user_from_header),
):
    try:
        image_url = await generate_image_from_prompt(request.prompt)
        image = Image(user_id=user.id, image_url=image_url)

        db = next(get_db())
        db.add(image)
        db.commit()

        return {
            "message": "success",
            "image_url": image_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/images")
def list_images(
    user: User = Depends(UserManager.get_user_from_header),
):
    try:
        db = next(get_db())
        images = db.query(Image).filter(Image.user_id == user.id).all()
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
