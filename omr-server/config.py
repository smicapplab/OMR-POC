from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Config:
    STATIC_URL= os.getenv("STATIC_URL", "http://localhost:4000")
    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = Path(os.getenv("DB_PATH")) if os.getenv("DB_PATH") else BASE_DIR / "omr.db"