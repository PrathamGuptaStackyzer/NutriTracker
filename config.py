import os
from dotenv import load_dotenv
import uuid
from fastapi import Depends

load_dotenv()

SECRET_KET = os.getenv("SECRET_KET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
URL_ENDPOINT = os.getenv("IMAGE_KIT_ID")

debug_mode = os.getenv("DEBUG", "False") == "True"
