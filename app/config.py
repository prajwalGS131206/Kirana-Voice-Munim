import os
from dotenv import load_dotenv

load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY")

if not GNANI_API_KEY:
    raise RuntimeError("GNANI_API_KEY is missing. Check your .env file.")