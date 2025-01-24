import os
from dotenv import load_dotenv

_ = load_dotenv()

SECRET = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
